"""
模块一：业务数据集整理与 LoRA 微调 —— 数据准备脚本

使用方式：
    python data_prep.py --input_dir ./raw_images --output_dir ./training_data --style "wabisabi"

功能：
    1. 批量重命名图像文件
    2. 可选：调用 BLIP/DeepDanbooru 自动打标（需要额外安装）
    3. 生成 kohya_ss 所需的 .txt 标签文件
    4. 输出数据集统计报告
"""

import os
import sys
import argparse
from pathlib import Path
from PIL import Image
import json

# kohya_ss / sd-scripts 要求的图像格式
VALID_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}


def parse_args():
    parser = argparse.ArgumentParser(description="LoRA 训练数据准备工具")
    parser.add_argument("--input_dir", type=str, required=True, help="原始图像目录")
    parser.add_argument("--output_dir", type=str, required=True, help="输出目录（kohya_ss 训练用）")
    parser.add_argument("--style", type=str, default="interior",
                        help="风格标签，会写入所有图像的 caption 中")
    parser.add_argument("--resolution", type=int, default=1024,
                        help="目标分辨率（短边），超出会等比缩放")
    parser.add_argument("--no_caption", action="store_true",
                        help="跳过人工 caption 生成，使用占位标签")
    return parser.parse_args()


def validate_and_report(input_dir: Path) -> dict:
    """扫描图像文件夹，返回统计信息"""
    stats = {"total": 0, "valid": 0, "skipped": [], "resolutions": []}

    for ext in VALID_EXTENSIONS:
        for f in input_dir.glob(f"*{ext}"):
            stats["total"] += 1
            try:
                with Image.open(f) as img:
                    w, h = img.size
                    stats["resolutions"].append((w, h))
                    stats["valid"] += 1
            except Exception as e:
                stats["skipped"].append((f.name, str(e)))

    return stats


def resize_if_needed(img_path: Path, output_path: Path, target_short: int):
    """等比缩放，短边对齐到 target_short"""
    with Image.open(img_path) as img:
        img = img.convert("RGB")
        w, h = img.size
        short = min(w, h)

        if short <= target_short:
            img.save(output_path)
            return

        ratio = target_short / short
        new_w = int(w * ratio)
        new_h = int(h * ratio)
        # 确保是 64 的倍数（SDXL 最佳实践）
        new_w = (new_w // 64) * 64
        new_h = (new_h // 64) * 64
        img = img.resize((new_w, new_h), Image.LANCZOS)
        img.save(output_path)


def generate_caption(style: str, index: int, filename: str) -> str:
    """
    生成训练用 caption 标签文件。
    如果不是用自动打标，至少写入触发词和风格标签。
    """
    # 触发词 —— LoRA 推理时使用这些词来激活
    trigger_phrases = {
        "wabisabi": "wabisabi style, japandi interior, natural materials, muted tones",
        "french_cream": "french cream style, elegant interior, curved lines, warm beige palette",
        "minimalist": "minimalist interior, track lighting, clean lines, open space",
        "interior": "interior design, professional rendering, high quality",
    }

    trigger = trigger_phrases.get(style, trigger_phrases["interior"])
    # 基础标签 + 文件名中的信息
    base = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ")
    return f"{trigger}, {base}"


def main():
    args = parse_args()
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # ----- 1. 扫描 -----
    print(f"[1/4] 扫描图像目录: {input_dir}")
    stats = validate_and_report(input_dir)
    print(f"  找到 {stats['total']} 个文件，有效 {stats['valid']} 个，跳过 {len(stats['skipped'])} 个")

    if stats["valid"] == 0:
        print("❌ 没有找到有效图像，退出。")
        sys.exit(1)

    if stats["valid"] < 50:
        print(f"⚠️  警告：仅 {stats['valid']} 张图像。LoRA 训练建议至少 50 张，100-200 张效果更佳。")

    # 分辨率分布
    if stats["resolutions"]:
        avg_w = sum(r[0] for r in stats["resolutions"]) / len(stats["resolutions"])
        avg_h = sum(r[1] for r in stats["resolutions"]) / len(stats["resolutions"])
        print(f"  平均分辨率: {avg_w:.0f} x {avg_h:.0f}")

    # ----- 2. 处理图像 -----
    print(f"\n[2/4] 处理图像 (目标短边: {args.resolution}px)...")
    image_dir = output_dir / "image"
    image_dir.mkdir(exist_ok=True)

    idx = 0
    for ext in VALID_EXTENSIONS:
        for f in sorted(input_dir.glob(f"*{ext}")):
            try:
                new_name = f"{args.style}_{idx:04d}{ext}"
                dest = image_dir / new_name

                resize_if_needed(f, dest, args.resolution)

                # 生成对应的 .txt caption 文件
                caption = generate_caption(args.style, idx, f.name)
                caption_path = image_dir / f"{args.style}_{idx:04d}.txt"
                with open(caption_path, "w", encoding="utf-8") as cf:
                    cf.write(caption.strip())

                idx += 1
                if idx % 20 == 0:
                    print(f"  已处理 {idx} 张...")

            except Exception as e:
                print(f"  ⚠ 跳过 {f.name}: {e}")

    print(f"  共处理 {idx} 张图像，每张配有一个 .txt 标签文件")

    # ----- 3. 生成训练配置引导 -----
    print(f"\n[3/4] 生成数据统计...")
    report = {
        "style": args.style,
        "image_count": idx,
        "resolution_target": args.resolution,
        "output_dir": str(output_dir),
        "kohya_ss_image_dir": str(image_dir),
        "recommended_repeats": max(1, 200 // max(idx, 1)),
        "recommended_epochs": 10,
    }

    report_path = output_dir / "dataset_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"  报告已保存: {report_path}")
    print(f"  建议设置: repeats={report['recommended_repeats']}, epochs={report['recommended_epochs']}")

    # ----- 4. 提示下一步 -----
    print(f"\n[4/4] ✅ 数据准备完成！")
    print(f"  训练图像目录: {image_dir}")
    print(f"  下一步:")
    print(f"    1. 检查图像质量，剔除模糊/水印/低质量图像")
    print(f"    2. 手动修正部分 .txt caption 文件（可选）")
    print(f"    3. 用 train_config.toml 配置 kohya_ss 进行训练")


if __name__ == "__main__":
    main()
