"""快速测试 ComfyUI 图像生成（跳过 Agent，直接送 Prompt）"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json
import time
import requests
from config import COMFYUI_CONFIG, SD_DEFAULTS

print("=" * 60)
print("ComfyUI 图像生成测试")
print("=" * 60)

# SD 1.5 简单工作流
workflow = {
    "3": {
        "inputs": {"ckpt_name": SD_DEFAULTS["checkpoint"]},
        "class_type": "CheckpointLoaderSimple",
    },
    "4": {
        "inputs": {
            "text": "interior design, living room, wabisabi style, natural materials, warm lighting, photorealistic, high quality, masterpiece",
            "clip": ["3", 1],
        },
        "class_type": "CLIPTextEncode",
    },
    "5": {
        "inputs": {
            "text": "ugly, blurry, low quality, distorted, watermark, text, signature",
            "clip": ["3", 1],
        },
        "class_type": "CLIPTextEncode",
    },
    "6": {
        "inputs": {
            "width": SD_DEFAULTS["width"],
            "height": SD_DEFAULTS["height"],
            "batch_size": 1,
        },
        "class_type": "EmptyLatentImage",
    },
    "7": {
        "inputs": {
            "seed": 42,
            "steps": 20,
            "cfg": 7.0,
            "sampler_name": "euler_ancestral",
            "scheduler": "normal",
            "denoise": 1.0,
            "model": ["3", 0],
            "positive": ["4", 0],
            "negative": ["5", 0],
            "latent_image": ["6", 0],
        },
        "class_type": "KSampler",
    },
    "8": {
        "inputs": {
            "samples": ["7", 0],
            "vae": ["3", 2],
        },
        "class_type": "VAEDecode",
    },
    "9": {
        "inputs": {
            "filename_prefix": "test_design",
            "images": ["8", 0],
        },
        "class_type": "SaveImage",
    },
}

# 1. 提交
print(f"\n[1/4] 提交工作流...")
print(f"  Checkpoint: {SD_DEFAULTS['checkpoint']}")
print(f"  Resolution: {SD_DEFAULTS['width']}x{SD_DEFAULTS['height']}")

resp = requests.post(
    f"{COMFYUI_CONFIG['api_base']}/prompt",
    json={"prompt": workflow},
    timeout=30,
)
resp.raise_for_status()
prompt_id = resp.json()["prompt_id"]
print(f"  Prompt ID: {prompt_id}")

# 2. 轮询等待
print(f"\n[2/4] 等待生成...")
start = time.time()
history = None
while time.time() - start < COMFYUI_CONFIG["timeout"]:
    r = requests.get(f"{COMFYUI_CONFIG['api_base']}/history/{prompt_id}", timeout=30)
    r.raise_for_status()
    data = r.json()
    if prompt_id in data:
        history = data[prompt_id]
        break
    elapsed = int(time.time() - start)
    print(f"  ⏳ 等待中... {elapsed}s", end="\r")
    time.sleep(2)

if history is None:
    print("\n  ❌ 生成超时")
    sys.exit(1)

print(f"\n  ✅ 生成完成，耗时 {int(time.time() - start)}s")

# 3. 提取文件名
print(f"\n[3/4] 获取图像...")
images = []
for node_id, node_output in history.get("outputs", {}).items():
    if "images" in node_output:
        for img in node_output["images"]:
            images.append(img)

if not images:
    print("  ❌ 没有生成图像")
    print(f"  History: {json.dumps(history, indent=2)[:500]}")
    sys.exit(1)

filename = images[0]["filename"]
print(f"  文件名: {filename}")

# 4. 下载到本地
print(f"\n[4/4] 下载图像...")
r = requests.get(
    f"{COMFYUI_CONFIG['api_base']}/view",
    params={"filename": filename, "type": "output"},
    timeout=30,
)
if r.status_code == 200:
    output_dir = Path(COMFYUI_CONFIG["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    dest = output_dir / filename
    with open(dest, "wb") as f:
        f.write(r.content)
    print(f"  ✅ 已保存: {dest}")
    print(f"  文件大小: {dest.stat().st_size / 1024:.1f} KB")
else:
    print(f"  ❌ 下载失败: {r.status_code}")

print(f"\n{'=' * 60}")
print("✅ 测试通过！ComfyUI 图像生成正常工作")
print(f"{'=' * 60}")
