"""
模块四：Gradio 端到端 Demo —— 室内设计 AI Agent 网页界面

启动方式：
    python app.py

然后在浏览器打开 http://127.0.0.1:7860

功能：
    - 左侧：输入设计需求（中文）
    - 右侧：展示生成效果（提示词 + 设计分析 + 图片）
    - 中间展示 Agent 推理过程
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import gradio as gr
from config import COMFYUI_CONFIG
from module3_agent.agent_pipeline import run_agent
from module3_agent.comfyui_client import check_comfyui_available


def process_design_request(user_input: str, enable_image_gen: bool = True):
    """
    Gradio 回调函数：处理用户输入，返回 Agent 的完整输出。
    """
    if not user_input or not user_input.strip():
        yield "请输入设计需求", "", "", None
        return

    # 先展示思考中状态
    yield "🤔 正在分析需求...", "", "", None

    # 运行 Agent
    result = run_agent(user_input, generate=enable_image_gen)

    # 构建过程展示
    process_text = f"""## 🔍 意图识别
- **检测到风格**: {result.get('detected_style') or '未识别（使用通用模板）'}
- **检测到房间类型**: {result.get('detected_room', '未知')}

## 📚 RAG 知识库检索
{result.get('rag_context', '无检索结果')}

## 🤖 LLM 原始输出
```
{result.get('raw_llm_response', '无')[:800]}
```
"""

    # 构建提示词展示
    prompt_text = f"""## ✅ 正向提示词
```
{result.get('positive_prompt', '')}
```

## ❌ 反向提示词
```
{result.get('negative_prompt', '')}
```

## ⚙️ 生成参数
- **CFG Scale**: {result['params'].get('cfg_scale', 7.0)}
- **Steps**: {result['params'].get('steps', 30)}
- **Sampler**: {result['params'].get('sampler', 'euler_ancestral')}
"""

    # 设计分析
    analysis = result.get("analysis", "")

    # 图像
    image = None
    if enable_image_gen and result.get("image"):
        img_result = result["image"]
        if img_result.get("success") and img_result.get("image_path"):
            image = img_result["image_path"]
        elif img_result.get("error"):
            process_text += f"\n\n## ⚠️ 图像生成\n{img_result['error']}"
    elif enable_image_gen:
        process_text += "\n\n## ⚠️ 图像生成\nComfyUI 未运行或生成失败"

    yield process_text, prompt_text, analysis, image


# ==================== Gradio UI ====================

# 自定义 CSS
CUSTOM_CSS = """
.gradio-container {
    max-width: 1400px !important;
    margin: 0 auto !important;
}
.header-text {
    text-align: center;
    margin-bottom: 20px;
}
.header-text h1 {
    font-size: 2em;
    font-weight: 700;
    margin-bottom: 8px;
}
.header-text p {
    color: #666;
    font-size: 1.1em;
}
"""

with gr.Blocks(css=CUSTOM_CSS, title="室内设计 AI Agent") as demo:
    gr.HTML("""
    <div class="header-text">
        <h1>🏠 室内设计风格多模态智能体</h1>
        <p>LoRA 微调 + RAG 知识库 + Agent 编排 + ComfyUI 渲染 —— 端到端 AI 设计生成</p>
        <p style="font-size:0.9em; color:#999;">
            支持风格：侘寂风 | 法式奶油风 | 极简无主灯
        </p>
    </div>
    """)

    with gr.Row():
        with gr.Column(scale=1):
            user_input = gr.Textbox(
                label="📝 设计需求（中文）",
                placeholder="例如：设计一个20平米的侘寂风客厅，需要带落地窗，空间要有呼吸感...",
                lines=4,
            )
            with gr.Row():
                enable_image = gr.Checkbox(
                    label="🖼 启用图像生成（需要 ComfyUI 运行中）",
                    value=True,
                )
                submit_btn = gr.Button("🎨 开始设计", variant="primary", size="lg")

            # 设计分析
            analysis_output = gr.Markdown(
                label="📊 设计分析",
                value="等待输入...",
            )

        with gr.Column(scale=2):
            with gr.Tabs():
                with gr.TabItem("🔬 Agent 推理过程"):
                    process_output = gr.Markdown(
                        value="等待输入设计需求...",
                    )
                with gr.TabItem("🎯 生成提示词"):
                    prompt_output = gr.Markdown(
                        value="等待生成...",
                    )

            image_output = gr.Image(
                label="🖼 生成效果图",
                type="filepath",
                height=400,
            )

    # 绑定事件
    submit_btn.click(
        fn=process_design_request,
        inputs=[user_input, enable_image],
        outputs=[process_output, prompt_output, analysis_output, image_output],
    )

    # 示例
    gr.Examples(
        examples=[
            ["设计一个20平米的侘寂风客厅，带落地窗，空间要有呼吸感，低矮家具，亚麻材质"],
            ["设计一个15平米的法式奶油风卧室，要有拱门元素，奶油色床品，石膏线装饰"],
            ["设计一个30平米的极简无主灯客厅，微水泥墙面，磁吸轨道灯，干净利落"],
            ["设计一个10平米的侘寂风书房，原木书架，纸灯，留白充足"],
        ],
        inputs=user_input,
        label="💡 试试这些示例",
    )

    # 状态栏
    comfyui_status = "🟢 ComfyUI 已连接" if check_comfyui_available() else "🔴 ComfyUI 未运行"
    gr.Markdown(
        f"---\n"
        f"**系统状态**: {comfyui_status} | "
        f"ComfyUI 地址: `{COMFYUI_CONFIG['api_base']}` | "
        f"知识库: ChromaDB (bge-small-zh) | "
        f"LLM: DeepSeek/Ollama"
    )


if __name__ == "__main__":
    from config import COMFYUI_CONFIG as _cfg
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,  # 改为 True 可以生成公网链接
        allowed_paths=[_cfg["output_dir"]],  # 允许 Gradio 访问 outputs/ 目录
    )
