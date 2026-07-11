"""
模块三：Prompt 工程模板

设计思路：
    不是简单拼接，而是分层构造：
    1. 风格层 (Style)   → RAG 检索到的风格规范
    2. 空间层 (Space)   → 房间类型、面积、布局
    3. 材质层 (Material) → RAG 检索到的材质参数
    4. 灯光层 (Lighting) → RAG 检索到的灯光标准
    5. 技术层 (Technical) → 分辨率、渲染质量、负面提示词

每一层独立构造，最后由 LLM 融合为一段高质量英文 Prompt。
"""

# ==================== Agent 系统提示词 ====================

AGENT_SYSTEM_PROMPT = """你是一位资深的室内设计 AI 渲染专家。你的任务是根据用户的中文需求描述，生成一段高质量的 Stable Diffusion 英文提示词。

## 你的工作流程
1. 仔细理解用户的需求（风格、空间、面积、特殊要求）
2. 参考提供的设计规范知识（RAG 检索结果）
3. 生成以下内容：
   - 正向提示词（英文，80-150 词）
   - 反向提示词（英文，30-50 词）
   - 推荐参数（CFG Scale, Steps, Sampler）
   - 设计分析（中文，为什么这样生成）

## 提示词撰写原则
- 主体在前：房间类型、风格、视角（interior design, living room, wide angle）
- 材质居中：具体材质描述比抽象形容词更有效
- 灯光在后：色温、光源类型、光照方向
- 技术收尾：渲染引擎、分辨率、质量标签
- 使用逗号分隔，不加句号

## 输出格式（严格遵守）
```
[POSITIVE]
正向提示词内容...

[NEGATIVE]
反向提示词内容...

[PARAMS]
CFG: 7.0, Steps: 30, Sampler: euler_ancestral

[ANALYSIS]
设计分析（中文）...
```
"""

# ==================== 提示词生成模板 ====================

PROMPT_GENERATION_TEMPLATE = """## 用户需求
{user_input}

## 设计知识库参考（RAG 检索结果）
{rag_context}

## 使用的 LoRA 信息
LoRA 名称: {lora_name}
触发词: {trigger_words}
权重: {lora_strength}

请根据以上信息，生成 Stable Diffusion 提示词。记得在正向提示词中包含触发词。"""


# ==================== 预设风格模板（作为 RAG 的补充） ====================

STYLE_PRESETS = {
    "wabisabi": {
        "positive_boost": "wabisabi style, japandi interior, natural materials, muted earth tones, "
                          "imperfect beauty, handmade pottery, linen fabric, matte surfaces, "
                          "warm ambient lighting, shoji screen, asymmetrical composition",
        "negative_boost": "glossy surfaces, modern furniture, bright saturated colors, "
                          "ornate decorations, polished marble, gold fixtures, plastic materials",
        "cfg_scale": 7.0,
        "steps": 30,
    },
    "french_cream": {
        "positive_boost": "french cream style, elegant parisian apartment, arched doorways, "
                          "herringbone wood floor, plaster moldings, curved furniture, "
                          "velvet upholstery, brass fixtures, soft warm lighting, floral arrangement",
        "negative_boost": "industrial style, exposed brick, concrete walls, minimal cold design, "
                          "harsh fluorescent lighting, cluttered space, dark gloomy atmosphere",
        "cfg_scale": 7.0,
        "steps": 30,
    },
    "minimalist": {
        "positive_boost": "minimalist interior, clean lines, open space, track lighting, "
                          "neutral color palette, uncluttered, functional design, "
                          "hidden storage, large windows, natural light, microcement walls",
        "negative_boost": "ornate decorations, clutter, excessive furniture, busy patterns, "
                          "dark corners, heavy curtains, frilly textiles, baroque elements",
        "cfg_scale": 7.0,
        "steps": 30,
    },
}

# ==================== 空间类型模板 ====================

SPACE_TEMPLATES = {
    "客厅": "living room, spacious, seating area, sofa, coffee table, entertainment center",
    "卧室": "bedroom, cozy, bed with headboard, nightstands, soft textiles, relaxation space",
    "餐厅": "dining room, dining table, chairs, pendant lighting, warm atmosphere",
    "厨房": "kitchen, countertops, cabinetry, cooking area, clean and functional",
    "书房": "home office, study room, bookshelves, desk, reading nook, focused environment",
    "卫生间": "bathroom, vanity, mirror, shower, spa-like atmosphere, clean tiles",
}

# ==================== 通用负面提示词 ====================

BASE_NEGATIVE_PROMPT = (
    "ugly, blurry, low quality, distorted, bad anatomy, watermark, text, "
    "signature, cropped, jpeg artifacts, overexposed, underexposed, "
    "fisheye, lens flare, chromatic aberration, oversaturated"
)
