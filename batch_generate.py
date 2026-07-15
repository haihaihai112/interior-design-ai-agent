"""
批量生成 15 张高质量室内设计效果图（用于作品集）
每个场景独立调用 Agent → LLM 生成 Prompt → ComfyUI 出图
"""
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import COMFYUI_CONFIG
from module3_agent.agent_pipeline import run_agent

# ==================== 15 个精选设计场景 ====================
# 覆盖 5 种风格 × 多种房间类型，保证作品集多样性

DESIGNS = [
    # ── 侘寂风 (Wabi-Sabi) ──
    {
        "desc": "设计一个25平米的侘寂风客厅，带落地窗和亚麻沙发，手工陶器装饰，暖色纸灯，原木茶几，空间留白充足有呼吸感",
        "style": "侘寂风",
        "room": "客厅",
    },
    {
        "desc": "设计一个18平米的侘寂风卧室，低矮地台床，微水泥墙面，亚麻床品，藤编衣柜，一束干枝在陶罐里，清晨柔光",
        "style": "侘寂风",
        "room": "卧室",
    },
    {
        "desc": "设计一个12平米的侘寂风书房兼茶室，原木大书架，矮茶桌，两个蒲团，纸灯笼，窗外有竹影，安静禅意",
        "style": "侘寂风",
        "room": "书房",
    },

    # ── 法式奶油风 (French Cream) ──
    {
        "desc": "设计一个30平米的法式奶油风客厅，石膏线天花，鱼骨拼木地板，丝绒弧形沙发，黄铜吊灯，拱门连通阳台，温暖优雅",
        "style": "法式奶油风",
        "room": "客厅",
    },
    {
        "desc": "设计一个20平米的法式奶油风主卧，奶油色软包床头，珍珠白床品，水晶壁灯，石膏雕花天花板，法式双开窗白色纱帘",
        "style": "法式奶油风",
        "room": "卧室",
    },
    {
        "desc": "设计一个15平米的法式奶油风餐厅，圆餐桌配四把藤编椅，黄铜吊灯，角落有鲜花，墙上挂装饰画，温馨浪漫",
        "style": "法式奶油风",
        "room": "餐厅",
    },

    # ── 极简无主灯 (Minimalist) ──
    {
        "desc": "设计一个35平米的极简无主灯客厅，微水泥墙面地面一体化，磁吸轨道灯和线性灯带，灰色模块化沙发，隐藏式收纳柜，极致干净",
        "style": "极简风",
        "room": "客厅",
    },
    {
        "desc": "设计一个18平米的极简无主灯卧室，悬浮床带底部灯带，深灰与米色搭配，电动遮光帘，床头墙面嵌入式灯带，酒店式高级感",
        "style": "极简风",
        "room": "卧室",
    },
    {
        "desc": "设计一个10平米的极简无主灯书房，白色一体式书桌书柜，背发光灯带，人体工学椅，百叶窗引入自然光，干净克制",
        "style": "极简风",
        "room": "书房",
    },

    # ── 现代轻奢 (Modern Luxury) ──
    {
        "desc": "设计一个40平米的现代轻奢客厅，大理石电视背景墙，深棕色真皮沙发，金色金属线条装饰，水晶吊灯，灰镜墙面延伸空间，高端大气",
        "style": "现代轻奢",
        "room": "客厅",
    },
    {
        "desc": "设计一个22平米的现代轻奢主卧，香槟金色床头背景硬包，丝绒床尾凳，大理石床头柜，水晶台灯，步入式衣帽间玻璃门",
        "style": "现代轻奢",
        "room": "卧室",
    },
    {
        "desc": "设计一个16平米的现代轻奢餐厅，大理石餐桌，绒面餐椅，金色吊灯，酒柜展示墙带背光，桌面精致餐具和鲜花布置",
        "style": "现代轻奢",
        "room": "餐厅",
    },

    # ── 北欧自然风 (Scandinavian Natural) ──
    {
        "desc": "设计一个25平米的北欧自然风客厅，浅橡木地板，灰白色布艺沙发，绿植角落，藤编吊灯，大窗户采光极佳，温暖治愈",
        "style": "北欧风",
        "room": "客厅",
    },
    {
        "desc": "设计一个15平米的北欧风儿童卧室，原木上下铺床，彩色几何地毯，墙面浅蓝色，玩具收纳架，窗前学习桌，活泼温馨",
        "style": "北欧风",
        "room": "卧室",
    },
    {
        "desc": "设计一个12平米的北欧风开放式厨房，小白砖墙面，原木台面，白色橱柜配黄铜拉手，窗台种香草，阳光透过百叶窗洒入",
        "style": "北欧风",
        "room": "厨房",
    },
]

OUTPUT_LOG = Path(COMFYUI_CONFIG["output_dir"]) / "batch_results.json"


def main():
    print("=" * 70)
    print("🏠 批量生成 15 张室内设计效果图（作品集用）")
    print(f"📁 输出目录: {COMFYUI_CONFIG['output_dir']}")
    print("=" * 70)

    results = []
    success_count = 0

    for i, design in enumerate(DESIGNS, 1):
        print(f"\n{'─' * 60}")
        print(f"📸 [{i}/15] {design['style']} · {design['room']}")
        print(f"   需求: {design['desc'][:80]}...")
        print(f"{'─' * 60}")

        try:
            # Step 1: Agent 生成 Prompt（含 LLM 调用）
            print(f"   🧠 LLM 生成提示词中...")
            result = run_agent(design["desc"], generate=True)

            if result.get("error"):
                print(f"   ❌ Agent 错误: {result['error']}")
                results.append({"index": i, "design": design, "error": result["error"]})
                continue

            design_info = {
                "index": i,
                "style": design["style"],
                "room": design["room"],
                "description": design["desc"],
                "positive_prompt": result.get("positive_prompt", ""),
                "negative_prompt": result.get("negative_prompt", ""),
                "params": result.get("params", {}),
                "analysis": result.get("analysis", ""),
                "coohom_brief": result.get("coohom_brief", ""),
                "asset_tags": result.get("asset_tags", ""),
                "social_copy": result.get("social_copy", ""),
            }

            # Step 2: 图像生成结果
            image_info = result.get("image")
            if image_info and image_info.get("success"):
                success_count += 1
                print(f"   ✅ 图片已保存: {Path(image_info['image_path']).name}")
                design_info["image_path"] = image_info["image_path"]
                design_info["status"] = "success"
            elif image_info and image_info.get("error"):
                print(f"   ⚠️ 图像生成失败: {image_info['error']}")
                design_info["status"] = "image_failed"
                design_info["image_error"] = image_info["error"]
            else:
                print(f"   ⚠️ 未生成图像")
                design_info["status"] = "no_image"

            results.append(design_info)

        except Exception as e:
            print(f"   ❌ 异常: {e}")
            results.append({"index": i, "design": design, "error": str(e)})

        # 间隔一下，避免 ComfyUI 排队过长
        if i < len(DESIGNS):
            print(f"   ⏳ 等待 5 秒后继续...")
            time.sleep(5)

    # 保存结果日志
    with open(OUTPUT_LOG, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print(f"🎉 批量生成完成！")
    print(f"   成功: {success_count}/{len(DESIGNS)}")
    print(f"   结果日志: {OUTPUT_LOG}")
    print(f"   图片目录: {COMFYUI_CONFIG['output_dir']}")
    print("=" * 70)

    # 列出所有生成的图片
    output_dir = Path(COMFYUI_CONFIG["output_dir"])
    pngs = sorted(output_dir.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    print(f"\n📁 最近生成的图片:")
    for p in pngs[:20]:
        size_kb = p.stat().st_size / 1024
        print(f"   {p.name} ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
