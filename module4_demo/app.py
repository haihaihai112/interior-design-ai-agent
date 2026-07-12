"""
Module 4: 室内设计 AI Agent —— Gradio 端到端 Demo（UI 全面优化版）

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
    process_text = f"""
### 🔍 意图识别
**检测到风格**: {result.get('detected_style') or '未识别（使用通用模板）'}
**检测到房间类型**: {result.get('detected_room', '未知')}

### 📚 RAG 知识库检索
{result.get('rag_context', '无检索结果')}

### 🤖 LLM 原始输出
```
{result.get('raw_llm_response', '无')[:800]}
```
"""

    # 构建提示词展示
    prompt_text = f"""### ✅ 正向提示词
```
{result.get('positive_prompt', '')}
```

### ❌ 反向提示词
```
{result.get('negative_prompt', '')}
```

### ⚙️ 生成参数
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
            process_text += f"\n\n### ⚠️ 图像生成\n{img_result['error']}"
    elif enable_image_gen:
        process_text += "\n\n### ⚠️ 图像生成\nComfyUI 未运行或生成失败"

    yield process_text, prompt_text, analysis, image


# ==================== Gradio UI ====================

CUSTOM_CSS = """
/* ===== 全局风格：温暖、安静、有呼吸感的室内设计调性 ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&display=swap');

.gradio-container {
    max-width: 1480px !important;
    margin: 0 auto !important;
    background: #F8F6F3 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ===== 顶部横幅 ===== */
.header-section {
    background: linear-gradient(165deg, #2D2A24 0%, #3D3830 50%, #4A443C 100%);
    border-radius: 20px;
    padding: 40px 48px 36px;
    margin: 16px 0 24px;
    position: relative;
    overflow: hidden;
}
.header-section::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(200,180,160,0.06) 0%, transparent 70%);
    border-radius: 50%;
}
.header-section::after {
    content: '';
    position: absolute;
    bottom: -30%;
    left: 20%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(180,200,180,0.04) 0%, transparent 70%);
    border-radius: 50%;
}
.header-section h1 {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2.2em;
    font-weight: 600;
    color: #F5F0EB;
    margin: 0 0 8px;
    letter-spacing: -0.02em;
    position: relative;
}
.header-section .subtitle {
    font-size: 1em;
    color: #C4BAB0;
    font-weight: 300;
    margin: 0 0 6px;
    position: relative;
}
.header-section .style-tags {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 16px;
    position: relative;
}
.header-section .style-tag {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.8em;
    font-weight: 400;
    background: rgba(245,240,235,0.1);
    color: #C4BAB0;
    border: 1px solid rgba(245,240,235,0.12);
    letter-spacing: 0.02em;
}

/* ===== 输入区 ===== */
.input-panel {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
    height: 100%;
}
.input-panel label {
    font-weight: 600 !important;
    font-size: 0.9em !important;
    color: #2D2A24 !important;
    margin-bottom: 6px !important;
}
.input-panel textarea {
    border-radius: 12px !important;
    border: 1.5px solid #E8E3DD !important;
    background: #FAF9F7 !important;
    font-size: 0.95em !important;
    line-height: 1.6 !important;
    color: #2D2A24 !important;
    padding: 14px 16px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
    resize: vertical !important;
}
.input-panel textarea:focus {
    border-color: #B8A89A !important;
    box-shadow: 0 0 0 3px rgba(184,168,154,0.15) !important;
}

/* ===== 主按钮 ===== */
.primary-btn {
    background: #2D2A24 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 32px !important;
    font-weight: 500 !important;
    font-size: 0.95em !important;
    color: #F5F0EB !important;
    transition: all 0.2s !important;
    box-shadow: none !important;
}
.primary-btn:hover {
    background: #3D3830 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(45,42,36,0.2) !important;
}
.primary-btn:active {
    transform: translateY(0);
}

/* ===== 复选框 ===== */
.checkbox-row {
    display: flex;
    align-items: center;
    gap: 8px;
}
.checkbox-row label {
    font-size: 0.85em !important;
    color: #6B6560 !important;
}

/* ===== 输出卡片 ===== */
.output-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
    margin-bottom: 16px;
}

/* ===== Tabs ===== */
.tabs-container {
    margin-bottom: 16px;
}
.tabs-container .tab-nav {
    border-bottom: 1.5px solid #EDE9E4 !important;
    margin-bottom: 0 !important;
    padding: 0 4px !important;
}
.tabs-container button {
    font-size: 0.85em !important;
    font-weight: 500 !important;
    color: #8A847E !important;
    padding: 10px 20px !important;
    border: none !important;
    background: transparent !important;
    border-bottom: 2px solid transparent !important;
    margin-bottom: -1.5px !important;
    transition: all 0.2s !important;
}
.tabs-container button.selected {
    color: #2D2A24 !important;
    border-bottom-color: #2D2A24 !important;
    background: transparent !important;
}
.tabs-container button:hover {
    color: #2D2A24 !important;
    background: transparent !important;
}
.tab-content {
    background: transparent !important;
    padding: 16px 4px !important;
    border: none !important;
}

/* ===== Markdown 输出（Agent 推理、提示词） ===== */
.markdown-output {
    font-size: 0.9em !important;
    line-height: 1.7 !important;
    color: #3D3830 !important;
}
.markdown-output h3 {
    font-size: 1em !important;
    font-weight: 600 !important;
    color: #2D2A24 !important;
    margin-top: 20px !important;
    margin-bottom: 8px !important;
    padding-bottom: 6px;
    border-bottom: 1px solid #EDE9E4;
}
.markdown-output h3:first-child {
    margin-top: 0 !important;
}
.markdown-output p {
    margin: 4px 0 !important;
}
.markdown-output strong {
    color: #2D2A24 !important;
    font-weight: 600 !important;
}
.markdown-output code {
    background: #F4F1ED !important;
    border-radius: 6px !important;
    padding: 2px 8px !important;
    font-size: 0.85em !important;
    color: #4A443C !important;
}
.markdown-output pre {
    background: #F4F1ED !important;
    border: 1px solid #E8E3DD !important;
    border-radius: 10px !important;
    padding: 16px !important;
    margin: 8px 0 !important;
    overflow-x: auto !important;
}
.markdown-output pre code {
    background: none !important;
    padding: 0 !important;
    font-size: 0.82em !important;
    line-height: 1.5 !important;
}

/* ===== 图像 ===== */
.image-output {
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
    border: 1px solid #EDE9E4 !important;
}

/* ===== 示例按钮 ===== */
.examples-section {
    margin-top: 20px !important;
}
.examples-section .examples-title {
    font-size: 0.8em !important;
    color: #8A847E !important;
    font-weight: 500 !important;
    margin-bottom: 8px !important;
}
.gr-sample-btn {
    background: #FFFFFF !important;
    border: 1.5px solid #EDE9E4 !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    font-size: 0.82em !important;
    color: #3D3830 !important;
    line-height: 1.4 !important;
    transition: all 0.2s !important;
}
.gr-sample-btn:hover {
    border-color: #B8A89A !important;
    background: #FAF9F7 !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04) !important;
}

/* ===== 状态栏 ===== */
.status-bar {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 12px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    margin-top: 12px;
    font-size: 0.8em !important;
    color: #6B6560 !important;
    line-height: 1.6 !important;
}

/* ===== 设计分析卡片 ===== */
.analysis-section {
    background: linear-gradient(135deg, #FAF9F7 0%, #F6F3EF 100%) !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    border: 1px solid #EDE9E4 !important;
    margin-top: 16px !important;
}
.analysis-section label {
    font-weight: 600 !important;
    font-size: 0.85em !important;
    color: #2D2A24 !important;
}

/* ===== 等待提示 ===== */
.waiting-text {
    color: #8A847E !important;
    font-size: 0.9em !important;
    font-style: italic !important;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
    .header-section {
        padding: 28px 24px;
    }
    .header-section h1 {
        font-size: 1.6em;
    }
    .input-panel {
        padding: 16px;
    }
}

/* ===== 滚动条美化 ===== */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: #D5CFC8;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #B8A89A;
}

/* ===== 去除 Gradio 默认多余装饰 ===== */
.gr-form, .gr-box {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}
.gr-panel {
    border: none !important;
}
footer {
    display: none !important;
}
"""

with gr.Blocks(css=CUSTOM_CSS, title="室内设计 AI Agent", theme=gr.themes.Soft()) as demo:
    # ===== 顶部横幅 =====
    gr.HTML("""
    <div class="header-section">
        <h1>Atelier · 室内设计智能体</h1>
        <p class="subtitle">LoRA 微调 + RAG 知识库 + Agent 编排 + ComfyUI 渲染 —— 端到端 AI 设计生成</p>
        <div class="style-tags">
            <span class="style-tag">侘寂风</span>
            <span class="style-tag">法式奶油风</span>
            <span class="style-tag">极简无主灯</span>
        </div>
    </div>
    """)

    with gr.Row(equal_height=False):
        # ===== 左侧面板：输入区 =====
        with gr.Column(scale=3, min_width=320):
            with gr.Column(elem_classes="input-panel"):
                gr.HTML("""
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                    <span style="font-size:1.1em;">✏️</span>
                    <span style="font-weight:600;font-size:0.9em;color:#2D2A24;">设计需求</span>
                </div>
                """)
                user_input = gr.Textbox(
                    label="",
                    placeholder="例如：设计一个20平米的侘寂风客厅，需要带落地窗，空间要有呼吸感...",
                    lines=5,
                )

                with gr.Row():
                    enable_image = gr.Checkbox(
                        label="🖼 启用图像生成（需要 ComfyUI 运行中）",
                        value=True,
                    )
                    submit_btn = gr.Button("🎨 开始设计", elem_classes="primary-btn")

            # 设计分析
            analysis_output = gr.Markdown(
                elem_classes="analysis-section",
                label=None,
                value="",
            )

        # ===== 右侧面板：输出区 =====
        with gr.Column(scale=5, min_width=480):
            with gr.Column(elem_classes="tabs-container"):
                with gr.Tabs():
                    with gr.TabItem("🔬 Agent 推理过程"):
                        process_output = gr.Markdown(
                            elem_classes="markdown-output",
                            value="<span class='waiting-text'>输入设计需求后点击「开始设计」...</span>",
                        )
                    with gr.TabItem("🎯 生成提示词"):
                        prompt_output = gr.Markdown(
                            elem_classes="markdown-output",
                            value="<span class='waiting-text'>等待生成...</span>",
                        )

            image_output = gr.Image(
                label=None,
                type="filepath",
                height=400,
                elem_classes="image-output",
                show_label=False,
            )

    # ===== 示例 =====
    gr.HTML("""
    <div class="examples-section">
        <div class="examples-title">💡 试试这些示例</div>
    </div>
    """)
    gr.Examples(
        examples=[
            ["设计一个20平米的侘寂风客厅，带落地窗，空间要有呼吸感，低矮家具，亚麻材质"],
            ["设计一个15平米的法式奶油风卧室，要有拱门元素，奶油色床品，石膏线装饰"],
            ["设计一个30平米的极简无主灯客厅，微水泥墙面，磁吸轨道灯，干净利落"],
            ["设计一个10平米的侘寂风书房，原木书架，纸灯，留白充足"],
        ],
        inputs=user_input,
        label=None,
    )

    # ===== 状态栏 =====
    comfyui_status = "🟢 ComfyUI 已连接" if check_comfyui_available() else "🔴 ComfyUI 未运行"
    gr.HTML(f"""
    <div class="status-bar">
        <strong>系统状态</strong> &nbsp;·&nbsp; {comfyui_status}
        &nbsp;·&nbsp; ComfyUI: <code>{COMFYUI_CONFIG['api_base']}</code>
        &nbsp;·&nbsp; 知识库: ChromaDB (bge-small-zh)
        &nbsp;·&nbsp; LLM: DeepSeek / Ollama
    </div>
    """)

    # ===== 事件绑定 =====
    submit_btn.click(
        fn=process_design_request,
        inputs=[user_input, enable_image],
        outputs=[process_output, prompt_output, analysis_output, image_output],
    )


if __name__ == "__main__":
    from config import COMFYUI_CONFIG as _cfg
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        allowed_paths=[_cfg["output_dir"]],
    )
