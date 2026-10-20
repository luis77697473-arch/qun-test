# 视觉与声音圣经 · Production Bible

> 目的：保证 39 个镜头、多种生成工具产出的素材，看起来像**同一部电影**。
> 规则只有一条：**所有提示词必须原样粘贴下面的"锁定描述"，一个词都不改。**

---

## 一、画幅与技术规格

| 项 | 规格 |
|---|---|
| 最终画幅 | 2.39:1（3840×1608 或 1920×804） |
| 生成画幅 | 16:9（Veo / Grok 原生），构图时主体放在**中间 75% 高度带**，后期上下裁切 |
| 帧率 | 24 fps（全片统一，生成时就指定 24fps） |
| 生成原声 | **全部丢弃**。Veo 自带的音频每段风格都不一样，会破坏声音的连贯性，所有声音统一在后期做 |
| 文字 | **AI 一律不生成任何文字**。HUD、片名、印章、字幕全部后期叠加（AI 生成的文字一定会乱码） |

## 二、调色板

```
墨世界      墨黑 #14110F   宣纸 #EDE6D6   靛蓝 #2B4A6F   朱砂 #C2362B
3D 世界     钢灰 #5E6B73   深青 #0E2A30   HUD 青 #5FF2E6  警告琥珀 #FFB23F
融合（终章） 晨光金 #F2C27B 叠加在以上两套色板之上
```

靛蓝 = 阿婆 / 稻草人。朱砂 = 小禾 / 印章 / 署名。这两个颜色在 3D 世界里**只能出现在稻草人和小禾身上**。

## 三、角色锁定描述（每次原样粘贴）

### 稻草人 SCARECROW
```
[SCARECROW] an old handmade rice-straw scarecrow tied to a weathered bamboo cross-pole
with three small carved holes near the top, wearing a faded, patched indigo-blue
Chinese cotton farmer's jacket and a wide torn conical straw hat; its face is pale
burlap with a single hand-brushed black ink smile that tilts crookedly to the left;
the whole figure is rendered as a living Chinese ink-wash painting — visible brushstroke
edges, ink softly bleeding into the air, rice-paper texture on its surface
```

### 无人机 07 DRONE-07
```
[DRONE-07] a small, old agricultural drone the size of a hawk, four rotors, matte
off-white ceramic shell covered in scratches and dried mud, the number "07" stencilled
in faded black on its side, one single large round camera lens with a thin hairline
crack across it, one slender articulated manipulator arm folded underneath; it moves
and tilts its body like a curious bird
```

### 阿婆 GRANDMOTHER（仅墨世界）
```
[GRANDMOTHER] an elderly Hani woman in her sixties from Yunnan, kind face with deep
lines, dark cloth head-wrap, sleeves rolled up, trousers rolled to the knee, standing
in a rice paddy; painted entirely in traditional Chinese ink wash on rice paper,
loose expressive brushwork, indigo-blue jacket as the only color
```

### 小禾 XIAO HE（墨世界童年 / 终镜老年）
```
[XIAO-HE-CHILD] a seven-year-old girl with two short braids tied with a cinnabar-red
ribbon, simple cotton clothes, barefoot; painted in traditional Chinese ink wash,
the red ribbon is the only color besides ink
[XIAO-HE-OLD] a tiny distant figure of an elderly woman with grey hair tied with a
faded cinnabar-red ribbon, walking slowly uphill on a mountain path
```

### 麻雀 SPARROWS
```
[SPARROWS-3D] photoreal Eurasian tree sparrows, chestnut caps, black cheek spots
[SPARROWS-INK] Eurasian tree sparrows painted with quick Chinese ink-wash brushstrokes
```

## 四、世界锁定描述

```
[STYLE-3D] photoreal cinematic CG, anamorphic lens, 2.39:1 framing with subject in the
central band, cold desaturated steel-grey and deep teal palette, volumetric mist,
mirror-like flooded rice paddies, shot on ARRI Alexa 65, 24fps, film grain

[STYLE-INK] traditional Chinese ink-wash painting (shuimo) come to life, on warm
off-white rice paper with visible fibre texture, black ink with grey washes, generous
negative space, wet ink bleeding and blooming, only accent colors indigo blue and
cinnabar red, hand-painted feeling, gentle paper grain, 24fps

[STYLE-FUSION] photoreal CG landscape whose edges dissolve into Chinese ink-wash
brushstrokes, warm golden dawn light over steel and teal, ink and metal coexisting

[VALLEY-NOW] Yuanyang valley in Yunnan transformed into a vast automated farm:
perfectly rectangular flooded rice paddies stepping down the mountains like a giant
circuit board, thin white sensor towers, sea of clouds below the peaks, no humans

[VALLEY-PAST] Hani rice terraces of Yuanyang, curved terraces following the mountain
contours like fingerprints, mist, small mud-walled mushroom-roofed houses
```

## 五、一致性工作流（最重要）

1. **先出定妆图，再出视频。** 用 Gemini（Nano Banana）或 Grok Imagine 为稻草人、07、阿婆、小禾各出 4 张定妆图（正面、侧面、3/4、特写），挑一张作为**唯一参考图**，以后所有镜头都用这张。
2. **视频一律走"图生视频"。** Veo 3.1 用参考图 / 首帧（ingredients 或 first frame），Grok Imagine 用 image-to-video。不要用纯文字生成角色镜头。
3. **场景同理。** 先出一张 `VALLEY-NOW` 的主场景图和一张 `VALLEY-PAST` 的主场景图，作为所有大远景的首帧。
4. **连续镜头用尾帧接首帧。** S10→S11、S25→S26→S27 这些连在一起的镜头，用上一段的最后一帧作为下一段的首帧。
5. **每个镜头至少出 4 版，挑 1 版。** 预算按 39 镜 × 4 版 ≈ 160 次生成来算。
6. **工具分工：**
   - **Veo**：写实 3D 大场面（S07–S09、S20–S24、S30、S33、S37），带物理效果的镜头（水、雨、坠落）。
   - **Grok Imagine**：水墨镜头（S02、S14–S18）、角色特写、风格化的过渡镜头。
   - 同一场戏尽量用**同一个工具**，避免质感跳变。

## 六、HUD 设计规范（后期叠加）

- 字体：等宽字体 JetBrains Mono / 中文用思源黑体 Light
- 颜色：HUD 青 #5FF2E6，透明度 85%；警告用琥珀 #FFB23F
- 动效：逐字打出，每字 1–2 帧；出现前先闪一帧扫描线
- 中英双语，英文在前
- 系统名：**禾·OS**（"禾"既指稻禾，也是小禾的名字。系统其实是以她命名的，这个彩蛋不点破）

## 七、声音设计

### 7.1 主题旋律"守望"（全片唯一动机）

五声音阶 D 宫，四个音：**D – E – A – G**，最后一个音拖长。

| 出现位置 | 音色 | 含义 |
|---|---|---|
| S11 | 风过竹孔，断续不成调 | 种子 |
| S17 | 竹哨完整吹出，阿婆跟着哼 | 来源 |
| S26 | 台风中竹哨反复尖啸 | 稻草人的"呐喊" |
| S29 | 哈尼多声部合唱 + 管弦乐 | 高潮 |
| S35 | 无人机 07 的电子"哔"声 | 机器学会了 |
| S39 | 竹哨 + 电子哔声，**第一次构成和声** | 人与机器 |

### 7.2 配乐分段（给 muse 或任何 AI 音乐工具的提示词）

| 段落 | 时间 | 提示词 |
|---|---|---|
| M1 序幕 | 0:00–0:42 | `cinematic opening, deep sub-bass drone, sparse granular synth pulses, a single guqin note at the start, building tension, stops abruptly at the end, 70 bpm, no drums, no vocals` |
| M2 秩序 | 0:42–1:30 | `vast minimalist electronic score, layered analog synth pads rising in perfect fifths, cold and majestic, like Jóhann Jóhannsson, slow, D minor pentatonic, no vocals` |
| M3 墨忆 | 1:30–2:16 | `intimate solo guqin and bamboo flute in D pentatonic, warm and nostalgic, distant Hani polyphonic folk voices humming softly, very sparse, rubato` |
| M4 风暴 | 2:16–3:32 | `epic orchestral storm cue, taiko and low brass hits, string ostinato, sudden one-second silence at 0:20, then massive build, climax with large ethnic choir singing a 4-note pentatonic motif D E A G, Hans Zimmer scale` |
| M5 守望 | 3:32–4:44 | `quiet resolution, solo felt piano and guqin, the 4-note motif D E A G played gently, soft strings swell at the end, hopeful, ends on a sustained D` |

**生成之后**：所有段落统一调到 D 调、统一混响，在剪辑里用交叉淡化接起来。如果 muse 不能精确控制旋律，"守望"四个音就单独录制或用 MIDI 做（竹笛 / 合唱 / 电子哔声三个版本），叠在配乐上。

### 7.3 音效清单（关键点）

- S01 墨滴入水：`单滴水声 + 混响尾巴拉长到 3 秒`
- S08 无人机群：`上万旋翼叠加，处理成一个和弦嗡鸣`，不要写实的噪音
- S22 电磁冲击：`电流爆音 → 全频段静音 1 秒`（**真正的数字静音，连底噪都不要**）
- S23 坠机雨：`金属落水声，慢放，加次低频`
- S26 竹哨：真实竹笛录音，加风噪
- S35 墨笔触麻布：`毛笔摩擦粗布的近场声`，全片最近的一个声音

### 7.4 唯一一句台词（配音稳定性）

只有阿婆一句话，所以不存在多段配音不一致的问题。

- 首选：真人录音。找一位云南口音的老年女性，用**普通话带云南口音**念，录 10 遍，挑一条。
- 次选：TTS 生成 10 版，挑一版，**全片只用这一条，不再重新生成**。
- 处理：轻微压缩 + 低通 8kHz + 微量房间混响，让它像一段记忆，而不是在耳边说话。
