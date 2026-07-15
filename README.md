# 🏠 室内设计风格多模态智能体与 LoRA 微调系统

> 从业务数据集 → LoRA 微调 → RAG 知识库 → Agent 编排 → Web 展示，完整打通 AI 室内设计生产链路。项目已按“模型运营实习生”岗位方向补强：覆盖酷家乐 / Coohom 方案 brief、模型素材库标签、海外趋势内容发布。

---

## 📁 项目结构

```
interior-design-ai-agent/
├── config.py                          # 全局配置（LLM、ComfyUI、LoRA、路径）
├── .env                               # API Key 环境变量（不提交）
├── requirements.txt                   # Python 依赖
├── README.md                          # 本文件
│
├── outputs/                           # 生成效果图
│
├── module1_lora/                      # 模块一：LoRA 微调
│   ├── data_prep.py                   #   数据采集、清洗、打标脚本
│   └── train_config.toml              #   kohya_ss 训练配置文件
│
├── module2_rag/                       # 模块二：RAG 知识库
│   ├── design_knowledge/              #   设计规范文档
│   │   ├── wabi_sabi.md               #     侘寂风规范
│   │   ├── french_cream.md            #     法式奶油风规范
│   │   ├── lighting_standards.md      #     灯光色温标准
│   │   ├── material_pbr.md            #     材质 PBR 参数
│   │   ├── coohom_workflow.md         #     酷家乐 / Coohom 方案图流程
│   │   ├── asset_library_taxonomy.md  #     家居模型素材库标签体系
│   │   └── overseas_trends_content.md #     海外趋势与内容发布参考
│   ├── build_knowledge_base.py        #   文档切片 + 向量化 + 存入 ChromaDB
│   └── query_knowledge.py             #   查询接口
│
├── module3_agent/                     # 模块三：Agent 编排
│   ├── agent_pipeline.py              #   主控管道（需求→RAG→LLM→图像）
│   ├── prompt_templates.py            #   Prompt 工程模板
│   └── comfyui_client.py              #   ComfyUI API 客户端
│
└── module4_demo/                      # 模块四：Web 展示
    └── app.py                         #   Gradio 网页界面（UI 全面优化版）
```

## 🧠 使用模型一览

| 用途 | 模型 | 说明 |
|------|------|------|
| **LLM 推理** | `deepseek-chat` (DeepSeek API) | 意图识别 + Prompt 生成 + 设计分析，支持切换 Ollama 本地模型 |
| **嵌入向量化** | `BAAI/bge-small-zh-v1.5` | 中文文本嵌入，将设计规范文档向量化存入 ChromaDB |
| **图像生成** | `majicmixRealistic_v7.safetensors` (SD 1.5) | ComfyUI 加载的写实风格 checkpoint，512×768~768×512 分辨率输出 |
| **LoRA（可选）** | 自定义训练（LyCORIS，Rank=32） | 支持针对特定设计风格进行 LoRA 微调增强 |

---

## 🎯 岗位 JD 对齐亮点

这个项目可以作为“模型运营实习生”岗位的定向作品集来展示：

| JD 关键词 | 项目对应能力 | 可展示产物 |
|-----------|--------------|------------|
| 使用 AI 建模软件建模 | LoRA 数据准备 + ComfyUI/SD 效果图生成 | 风格化效果图、英文 Prompt、参数记录 |
| 扩充酷家乐模型库 | 素材库标签体系 + 风格/材质/空间分类 | `asset_tags`、Coohom 英文关键词、质量备注 |
| 使用酷家乐工具做方案/效果图 | Coohom 执行 brief + 灯光/相机/材质说明 | 可交给酷家乐落地的英文 brief |
| 关注海外设计趋势 | RAG 知识库加入海外趋势与内容渠道 | 风格趋势、社媒标签、内容选题 |
| 发布模型/工具内容 | Agent 自动生成图文文案和短视频脚本 | 标题、正文、Hashtags、视频脚本 |
| 英语书面沟通 | 英文 Prompt + 英文 Coohom brief | 面向海外团队的结构化交付 |

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd interior-design-ai-agent
pip install -r requirements.txt --break-system-packages
```

### 2. 配置 API Key

创建 `.env` 文件（参考 `.env.example`）：

```env
LLM_API_BASE=https://api.deepseek.com/v1
LLM_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LLM_MODEL=deepseek-chat
```

或用本地 Ollama 替代，编辑 `config.py` 取消对应注释。

### 3. 构建 RAG 知识库（只需运行一次）

```bash
python module2_rag/build_knowledge_base.py
```

首次运行会自动下载 `bge-small-zh-v1.5` 嵌入模型（约 100MB）。

### 4. 启动 Agent（命令行）

```bash
python module3_agent/agent_pipeline.py "设计一个20平米的侘寂风客厅，带落地窗，空间要有呼吸感"
```

如果 ComfyUI 未运行，Agent 仍然会输出完整的提示词和设计分析。

### 5. 启动 Web 界面

```bash
python module4_demo/app.py
```

浏览器打开 `http://127.0.0.1:7860`。

---

## 🌐 Web UI 界面说明

UI 经过全新设计，采用温暖、安静、有呼吸感的视觉语言：

- **深棕渐变顶部横幅** — 品牌标题 "Atelier · 室内设计智能体" + 风格标签
- **左侧白色卡片式输入面板** — 5 行文本框 + 复选框 + 设计分析区
- **右侧多标签页输出** — "Agent 推理过程" / "生成提示词" / "Coohom Brief" / "素材标签" / "发布内容" 切换
- **图片输出** — 圆角阴影展示
- **示例快捷入口** — 4 个预设设计需求一键填充
- **状态栏** — 实时显示 ComfyUI 连接状态和系统信息

---

## 📐 四个模块详解

### 模块一：LoRA 微调

1. **准备数据**：收集 50-200 张目标风格的高清效果图
2. **运行预处理**：`python module1_lora/data_prep.py --input_dir ./raw --output_dir ./training_data --style wabisabi`
3. **配置 kohya_ss**：用 `train_config.toml` 中的参数（Rank=32, LR=1e-4）
4. **训练**：在 4090/云端 3090 上跑通 LoRA 训练
5. **可视化对比**：基础模型 vs 加了 LoRA 的效果对比图 + loss 曲线

### 模块二：RAG 知识库

- 7 份设计与运营知识文档（风格规范、灯光标准、材质 PBR、Coohom 流程、素材库标签、海外趋势内容）
- 使用 `bge-small-zh-v1.5` 中文嵌入模型
- ChromaDB 本地向量数据库
- 文档自动切片（512 tokens/chunk，64 overlap）

### 模块三：Agent 编排

- **意图识别**：自动检测风格类型和房间类型
- **RAG 检索**：查询设计知识库获取专业规范
- **LLM 推理**：DeepSeek/Qwen 生成高质量英文 Prompt
- **ComfyUI 调用**：通过 REST API 提交生成任务
- **LoRA 绑定**：自动在提示词中注入 LoRA 触发词
- **Coohom Brief**：输出可用于酷家乐 / Coohom 的英文执行说明
- **素材库运营**：输出风格、空间、材质、颜色和检索关键词
- **内容运营**：输出社媒标题、正文、标签和短视频脚本

### 模块四：Web Demo

**展示给面试官的点**：你有产品化的思维，不只是跑脚本。

- Gradio 网页界面，左侧输入 → 右侧出图
- 实时展示 Agent 推理过程和中间产物
- 可切换查看：推理过程 / 生成提示词 / Coohom Brief / 素材标签 / 发布内容 / 设计分析
- 响应式设计，适配桌面和移动端
- 自定义设计语言：温暖色调、卡片布局、圆角阴影

### 面试展示建议

1. 先用 Web Demo 输入一个海外业务场景友好的需求，例如“20 平米法式奶油风卧室，面向海外公寓客户，需要可在 Coohom 中复现”。
2. 展示生成的效果图和英文 Prompt，说明 AI 出图能力。
3. 切到 **Coohom Brief**，说明它能指导后续酷家乐 / Coohom 建模和出图。
4. 切到 **素材标签**，说明你理解模型素材库需要可检索、可复用、可运营。
5. 切到 **发布内容**，说明你能把模型和工具能力转成图文/短视频内容。

---

## ⚙️ 依赖与硬件要求

| 组件 | 最低要求 | 推荐配置 |
|------|---------|---------|
| LoRA 训练 | GPU 8GB 显存 | RTX 3090/4090 (24GB) |
| RAG 知识库 | CPU 即可 | 任意 |
| Agent 推理 | 无（调 API） | DeepSeek API / Ollama 本地 |
| ComfyUI 推理 | GPU 8GB 显存 | RTX 3060+ |
| Gradio Web | CPU 即可 | 任意 |

---

## 问题

**Q: 没有 GPU 能跑吗？**
A: 模块二（RAG）和模块四（Web）不需要 GPU。模块一的 LoRA 训练和模块三的图像生成需要 GPU，但可以用云端 GPU。

**Q: 不用 ComfyUI 可以用 Automatic1111 吗？**
A: 可以，修改 `module3_agent/comfyui_client.py` 中的 API 调用为 A1111 的 `/sdapi/v1/txt2img` 接口即可。

**Q: 知识库文档太少怎么办？**
A: 往 `module2_rag/design_knowledge/` 目录添加更多 `.md` 文件，然后重新运行 `build_knowledge_base.py`。

---

## 📄 License

MIT — 自由使用、修改、分发。
