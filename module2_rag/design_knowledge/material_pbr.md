# 常用室内材质 PBR 参数速查

## 什么是 PBR
PBR（Physically Based Rendering，基于物理的渲染）通过 Albedo（固有色）、Roughness（粗糙度）、Metallic（金属度）三个核心参数定义材质外观。在 SD/ComfyUI 的提示词中，正确描述这些参数能显著提升渲染真实度。

## 木材
- 白橡木：roughness 0.6-0.7, metallic 0.0, albedo #D2B48C
- 胡桃木：roughness 0.5-0.6, metallic 0.0, albedo #6B4226
- 柚木：roughness 0.5-0.7, metallic 0.0, albedo #A0764A
- 提示词关键词："oak wood texture", "matte wood grain", "natural wood surface"

## 石材
- 大理石（白色）：roughness 0.1-0.2, metallic 0.0, albedo #F0F0F0
- 花岗岩：roughness 0.3-0.5, metallic 0.0, albedo #808080
- 石灰石：roughness 0.6-0.8, metallic 0.0, albedo #C8C0B8
- 提示词关键词："marble surface", "honed stone finish", "natural stone texture"

## 金属
- 黄铜（拉丝）：roughness 0.3-0.4, metallic 1.0, albedo #D4A54A
- 不锈钢（拉丝）：roughness 0.2-0.3, metallic 1.0, albedo #C0C0C0
- 哑光黑铁：roughness 0.6-0.8, metallic 1.0, albedo #3A3A3A
- 提示词关键词："brushed brass", "matte black metal", "stainless steel"

## 墙面涂料
- 微水泥：roughness 0.6-0.8, metallic 0.0, albedo #E8E5DF
- 硅藻泥：roughness 0.8-0.9, metallic 0.0, albedo #F0EDE8
- 哑光乳胶漆：roughness 0.9-1.0, metallic 0.0
- 提示词关键词："microcement wall", "matte painted wall", "textured plaster finish"

## 织物
- 亚麻：roughness 0.9, metallic 0.0, 表面带自然褶皱
- 天鹅绒：roughness 0.4-0.5（低角度高反光）, metallic 0.0
- 棉麻混纺：roughness 0.8, metallic 0.0
- 提示词关键词："linen fabric texture", "velvet upholstery", "natural fiber textile"

## 玻璃与镜面
- 透明玻璃：roughness 0.0-0.05, metallic 0.0, 带折射
- 磨砂玻璃：roughness 0.2-0.4, metallic 0.0
- 镜面：roughness 0.0, metallic 0.0, 高反射率
- 提示词关键词："frosted glass", "clear glazing", "reflective surface"

## SD/ComfyUI 材质提示词通用模板
```
[材质名称], [表面处理] surface, [粗糙度形容词] texture, physical based rendering, 
architectural visualization, 8k resolution, detailed material
```
示例："brushed brass fixtures, matte surface, fine grain texture, physical based rendering"
