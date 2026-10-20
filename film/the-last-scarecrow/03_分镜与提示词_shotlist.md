# 分镜表与生成提示词 · Shot List & Prompts

> 用法：提示词中的 `[SCARECROW]`、`[STYLE-3D]` 等标签，**生成前替换为《02 视觉与声音圣经》里对应的锁定描述原文**。
> 所有提示词末尾统一追加：`no text, no letters, no subtitles, no watermark, 24fps`
> 工具：**V** = Veo（3.1，图生视频优先） · **G** = Grok Imagine · **P** = 纯后期（不生成）
> 文件命名：`shots/S07.mp4`、`shots/S18a.mp4` …… 与 `assemble.sh` 对应

---

## 序幕 · 启动（0:00 – 0:42）

| # | 时间 | 时长 | 景别 / 镜头 / 运动 | 工具 | 后期叠加 | 转场 |
|---|---|---|---|---|---|---|
| S01 | 0:00 | 6s | 黑场 → 微距，100mm 微距，固定 | G | — | 黑场淡入 |
| S02 | 0:06 | 8s | 微距 → 大远景，持续后拉 | G | — | 连续 |
| S03 | 0:14 | 8s | 俯视地形，缓慢旋转 | G | HUD 开机 + `GEMINI · VEO ✓` | **匹配剪辑**（墨线→青线） |
| S04 | 0:22 | 8s | 机舱内，横移 | V | `GROK IMAGINE ✓` | 硬切 |
| S05 | 0:30 | 6s | 纯 HUD 画面 | P | `OPUS 5.5 ✓` → `⚠ 1 ANOMALY` | 硬切，**声音骤停** |
| S06 | 0:36 | 6s | 宣纸俯拍，固定 | G | 片名 + 扫描线数字化 | 切黑 |

**S01** `[STYLE-INK] extreme macro shot, slow motion, a single drop of black ink falls from above into perfectly still clear water against a pure black background, the moment of impact, a tiny crown splash, ink begins to bloom`

**S02** `[STYLE-INK] black ink blooming and swirling in water, the ink clouds slowly form mountain ridges, mist and curved rice terraces, camera continuously pulls back to reveal an entire ink-wash mountain valley, [VALLEY-PAST], meditative`

**S03**（先生成一段干净的地形镜头，HUD 文字后期加）`a glowing teal wireframe topographic 3D model of a mountain valley floating in darkness, contour lines pulsing gently, holographic, slow rotation, deep teal and black, minimal, futuristic agricultural control interface aesthetic`
> 剪辑点：S02 最后一帧的山脊线与 S03 第一帧的等高线**位置对齐**（后期用 0.5 秒交叉溶解 + 青色辉光过渡）。

**S04** `[STYLE-3D] inside a vast dark drone hangar inside a sensor tower, thousands of small white agricultural drones hanging on charging racks in endless rows, their indicator lights turning on row by row from teal to white like a field waking up, slow lateral dolly`

**S05** 纯后期：黑底 HUD。最后一行琥珀色 `⚠ 1 ANOMALY DETECTED` 闪三下，第三下时声音全部切断。

**S06** `[STYLE-INK] top-down view of a blank sheet of warm rice paper, a calligraphy brush enters frame and paints five bold Chinese characters in black ink, wet ink glistening`
> 实际做法：书法字用真人书写或字体动画（汉仪尚巍手书 / 方正字迹），AI 只出纸和笔的运动。扫描线数字化效果在 AE / Resolve Fusion 里完成：右半边笔画用 mosaic + edge detect + 青色描边。

---

## 第一章 · 秩序（0:42 – 1:30）

| # | 时间 | 时长 | 景别 / 镜头 / 运动 | 工具 | 后期叠加 | 转场 |
|---|---|---|---|---|---|---|
| S07 | 0:42 | 8s | 极大远景航拍，24mm，缓慢前推 | V | — | 切黑淡入 |
| S08 | 0:50 | 8s | 大远景，仰拍，35mm | V | — | 硬切 |
| S09 | 0:58 | 6s | 极低角度，16mm 超广角 | V | — | 硬切 |
| S10 | 1:04 | 8s | 正俯拍，垂直缓降 | V | — | 硬切 |
| S11 | 1:12 | 6s | 中景，50mm，缓慢环绕 15° | G | — | 连续（S10 尾帧作首帧） |
| S12 | 1:18 | 6s | 无人机 POV，长焦 200mm | V | 准星 + 识别信息 | 硬切 |
| S13 | 1:24 | 6s | 特写，85mm，浅景深 | V | — | **袖子填满画面 → 墨** |

**S07** `[STYLE-3D] [VALLEY-NOW] epic extreme wide aerial shot at dawn, the perfectly geometric flooded paddies mirror the pale sky, layers of mountains fade into fog, slow forward drone push, majestic, silent, inhumanly perfect`

**S08** `[STYLE-3D] [VALLEY-NOW] ten thousand small white agricultural drones rise from hangar doors into the dawn sky, at first like a flock of birds, then snapping into precise geometric wave formations, spraying fine mist over the paddies, sunbeams cutting through the mist creating thousands of light shafts, low angle looking up`

**S09** `[STYLE-3D] extreme low angle at water level, a giant four-legged autonomous harvesting machine strides through a flooded rice paddy, each step sending perfectly even ripples, a single small sparrow flutters away in panic from near its foot, scale contrast, 16mm wide lens`

**S10** `[STYLE-3D] [VALLEY-NOW] perfect top-down overhead shot slowly descending, an endless grid of rectangular rice paddies, and in the exact center one circular patch of old, messy, unkempt rice, in its middle stands [SCARECROW], the only hand-painted ink element in the photoreal world`

**S11**（首帧 = S10 尾帧或稻草人定妆图）`[SCARECROW] standing in the middle of a small patch of old wild rice, three [SPARROWS-3D] perched on its outstretched arms, wind ruffles the jacket sleeves, its ink edges softly bleed into the morning air, behind it the photoreal geometric paddies stretch to the horizon, medium shot, slow 15-degree orbit, [STYLE-3D]`

**S12** `telephoto 200mm view through a machine camera, slightly digital and desaturated, centered on [SCARECROW] in the distance, a sparrow hops into the center of frame, brief digital glitch distortion`
> 后期：准星锁定动画 + 识别信息逐字打出。麻雀跳进准星那一帧，加 4 帧噪点故障。

**S13** `[DRONE-07] hovering in close-up, shallow depth of field, its cracked lens aperture contracts then opens, it tilts its whole body sideways like a curious bird studying something, background softly blurred scarecrow and paddies, [STYLE-3D]`
> 转场：S13 最后 1 秒接一个**插入镜头**：靛蓝袖子在风里飘起填满画面（G 生成 2s），然后袖子的布纹溶解成墨的笔触，进入 S14。

---

## 第二章 · 墨忆（1:30 – 2:16）

全部用 G 生成，同一个工具，保证水墨质感统一。

| # | 时间 | 时长 | 景别 / 运动 | 后期 | 转场 |
|---|---|---|---|---|---|
| S14 | 1:30 | 8s | 大远景，横移 | 宣纸纹理叠加 | 墨溶入 |
| S15 | 1:38 | 8s | 中景，固定 | 同上 | 硬切 |
| S16 | 1:46 | 6s | 大特写，固定 | 同上 | 硬切 |
| S17 | 1:52 | 8s | 中远景，缓推 | 字幕：阿婆台词 | 硬切 |
| S18a/b | 2:00 | 5s+5s | 远景延时，固定机位 | 结尾 3D 网格爬入 | 墨晕转场 |
| S19 | 2:10 | 6s | 特写，墨 → 3D 匹配剪辑 | `T-00:47:12` | **匹配剪辑** |

**S14** `[STYLE-INK] [VALLEY-PAST] a line of villagers bent over transplanting rice seedlings in a curved terrace, their reflections forming one continuous line in the water, mist drifting, slow lateral pan, peaceful, forty years ago`

**S15** `[STYLE-INK] [GRANDMOTHER] and [XIAO-HE-CHILD] on a terrace ridge binding rice straw into a scarecrow body, the grandmother carves small holes into a bamboo pole with a knife, then takes off her own indigo jacket and dresses the scarecrow in it, the girl watches curiously, medium shot`

**S16** `[STYLE-INK] extreme close-up, the small hand of [XIAO-HE-CHILD] holding a calligraphy brush paints a smile on a burlap scarecrow face, her hand trembles and the smile tilts crookedly to the left, wet black ink`

**S17** `[STYLE-INK] dozens of [SPARROWS-INK] land all over the newly made scarecrow wearing the indigo jacket, [XIAO-HE-CHILD] waves her arms to chase them away, [GRANDMOTHER] gently holds the girl's hand and sits her down on the terrace ridge beside her, wind blowing through the rice, slow push in, tender`

**S18a** `[STYLE-INK] time-lapse on rice paper, seasons flow over the same terraces — green, gold, white snow — the figures of villagers dissolve into loose brushstrokes and blow away like ash, the houses empty, the scarecrow in the indigo jacket remains standing, static camera`

**S18b** `[STYLE-INK] a young woman with a cinnabar-red ribbon in her hair carrying a suitcase walks down a mountain road and looks back once, then the faint figure of an elderly woman beside the scarecrow slowly fades into the paper, only the scarecrow remains; from the edges of the paper, straight glowing teal grid lines creep inward like frost, swallowing the curved terraces`

**S19**（两段：墨的版本 3s + 3D 的版本 3s，构图完全一致）
- 墨：`[STYLE-INK] close-up, an old woman's hand painted in ink rests gently on the indigo sleeve of the scarecrow`
- 3D：`[STYLE-3D] close-up, the slender mechanical manipulator arm of [DRONE-07] rests gently on the indigo sleeve of [SCARECROW] at exactly the same spot, the sky darkening, wind rising`

---

## 第三章 · 风暴（2:16 – 3:32）

| # | 时间 | 时长 | 景别 / 镜头 / 运动 | 工具 | 后期 | 转场 |
|---|---|---|---|---|---|---|
| S20 | 2:16 | 8s | 极大远景，固定 | V | `⚠ TYPHOON CAT-5` | 硬切 |
| S21 | 2:24 | 6s | 水面低角度，手持晃动 | V | — | 硬切 |
| S22 | 2:30 | 6s | 大远景 | V | HUD 全部熄灭 | **静音 1 秒** |
| S23 | 2:36 | 8s | 大远景，升格 120fps 慢动作 | V | — | 闪电白帧 |
| S24 | 2:44 | 6s | 极大远景航拍 | V | — | 硬切 |
| S25 | 2:50 | 6s | 中景，跟拍 | V | — | 硬切 |
| S26 | 2:56 | 8s | 大特写，缓推 | G | — | 连续 |
| S27a/b | 3:04 | 5s+5s | 正俯拍，缓升 | G | 墨线辉光 | 连续 |
| S28 | 3:14 | 6s | 大特写，镜头反射 | V | `● REC 录制中` | 硬切 |
| S29 | 3:20 | 6s | 中景，低角度 | G | — | 硬切 |
| S30 | 3:26 | 6s | 极大远景 | V | — | 淡入白 |

**S20** `[STYLE-3D] [VALLEY-NOW] a colossal typhoon wall of black clouds rolls over the mountain ridge toward the valley, lightning flickering inside the cloud base, below it thousands of drones hold a defensive grid formation in the sky, ominous, extreme wide`

**S21** `[STYLE-3D] water-level low angle, torrential rain smashes the mirror-like paddies, the geometric fields churn into waves of mud, handheld shake, violent wind, dark`

**S22** `[STYLE-3D] lightning strikes a tall white sensor tower in the valley, a spherical blue electromagnetic shockwave expands across the whole valley, every light on every machine goes dark at once, extreme wide`

**S23** `[STYLE-3D] slow motion, ten thousand white drones lose power simultaneously and fall from the stormy sky like metal rain into the flooded paddies, lit only by flashes of lightning, epic, haunting, extreme wide`

**S24** `[STYLE-3D] extreme wide aerial, the rectangular stepped paddies collapse one after another down the mountainside like dominoes, walls breaking, torrents of mud and water rushing downhill, storm, rain`

**S25** `[STYLE-3D] [DRONE-07] tumbles through the storm wind, spinning, and crashes into the mud at the foot of [SCARECROW], a few [SPARROWS-3D] huddle under the scarecrow's straw hat sheltering from the rain, tracking shot`

**S26** `extreme close-up of the burlap face of [SCARECROW] in heavy rain, the crooked black ink smile begins to run down like tears, then the ink of its whole body starts to dissolve into the rain, ink-wash dissolving into photoreal rainwater, slow push in, heartbreaking`

**S27a** `top-down view, black ink flows out from the base of [SCARECROW] into the flooded paddies, instead of dispersing it moves like living roots, like an invisible brush painting by itself, drawing long curved lines along the mountain contours, [STYLE-FUSION] in a storm`

**S27b** `top-down view slowly rising, wherever the curved black ink lines pass, ink-wash terrace walls rise from the mud and hold back the rushing muddy water, the straight photoreal grid collapses while the curved ink lines grow across the mountainside, the ghostly Hani terraces reappear, magical, epic`
> 后期：墨线加微弱暖白辉光；S27b 可以叠一层 S14 的墨梯田，透明度 20%，作为"祖先的幽灵"。

**S28** `extreme close-up of the cracked camera lens of [DRONE-07] lying in mud, the lens reflects glowing curved ink lines spreading across the dark valley, raindrops on the lens, a tiny red recording light blinks on`

**S29** `low angle, the straw body of the scarecrow is almost entirely washed away, only a few strands remain, but the faded indigo jacket and torn straw hat still hang on the bamboo cross-pole, sparrows still sheltering under the hat, storm raging behind, heroic silhouette, [STYLE-FUSION]`

**S30** `[STYLE-FUSION] extreme wide, the typhoon passes away over the far ridge, the valley half ruined, but across the mountainside a gigantic faint-glowing ink-wash terrace pattern holds the water like a painting laid on the earth, first light breaking`

---

## 第四章 · 守望（3:32 – 4:44）

| # | 时间 | 时长 | 景别 / 镜头 / 运动 | 工具 | 后期 | 转场 |
|---|---|---|---|---|---|---|
| S31 | 3:32 | 8s | 大特写 → 中景 | V | 重启 HUD | 白场淡入 |
| S32 | 3:40 | 8s | 纯图形 | P | 地形对比数据 | 硬切 |
| S33 | 3:48 | 8s | 极大远景，缓升 | V | — | 硬切 |
| S34 | 3:56 | 8s | 中景，环绕 | V | — | 硬切 |
| S35a/b | 4:04 | 5s+5s | 大特写，固定，微距 | V | — | 连续 |
| S36 | 4:14 | 6s | 中景 | V | 功能字段改写 | 硬切 |
| S37 | 4:20 | 10s | 极大远景，升降上摇（慢放 80%） | V | — | 化成宣纸 |
| S38 | 4:30 | 6s | 宣纸 | P | 朱砂印章 ×2 | — |
| S39 | 4:36 | 8s | 宣纸 → 黑 | P | 献词 | 黑场 |

**S31** `[STYLE-FUSION] quiet dawn after the storm, water dripping, extreme close-up of [DRONE-07] lying in shallow water, its cracked lens flickers and lights up, it slowly lifts itself, pull back to medium shot`

**S32** 纯后期：两张地形线框图叠加。网格梯田标红闪烁 `87% FAILURE`，墨的等高线标青常亮 `0% FAILURE`，然后一条连线从等高线拉到 `SOURCE: OBJECT 0x01`。

**S33** `[STYLE-FUSION] [VALLEY-NOW] extreme wide rising shot, thousands of white drones rise again but this time they fly in loose, organic, flowing murmurations like flocks of sparrows instead of grids, they follow the glowing curved ink lines and begin rebuilding curved terraces along the mountain contours, the edges of the photoreal world softening into ink wash`

**S34** `[STYLE-FUSION] [DRONE-07] and several other drones carry bundles of fresh golden rice straw and rebuild the body of the scarecrow on the bamboo cross-pole, then carefully place the old faded indigo jacket and torn straw hat back on it, the burlap face is blank, slow orbit, tender`

**S35a** `[STYLE-FUSION] extreme close-up macro, the manipulator arm of [DRONE-07] dips its tip into a small puddle of black ink on the ground, lifts it, and pauses in mid-air hesitating in front of a blank burlap face, ink dripping`

**S35b** `[STYLE-FUSION] extreme close-up macro, the trembling manipulator tip of [DRONE-07] paints a smile in black ink on the blank burlap face, its arm wobbles and the smile tilts crookedly to the left, wet ink soaking into the fibre`
> 剪辑：S35b 结束后插 0.5 秒 S16（小禾画笑）的**同构图闪回**，再切回机器画的笑。这是全片情绪的最高点。

**S36** `[STYLE-FUSION] medium shot, sparrows return one by one and perch on the arms of the rebuilt [SCARECROW] with its new crooked ink smile, one sparrow hesitates, then lands on top of [DRONE-07] hovering beside it, the drone holds perfectly still`

**S37** `[STYLE-FUSION] epic extreme wide crane up shot at golden sunrise, the reborn valley with curved terraces glowing like mirrors, drones and sparrows flying together in the same sky, the frame is half photoreal and half Chinese ink painting blending seamlessly, the scarecrow stands small in the center, on a distant mountain path [XIAO-HE-OLD], the camera holds and does not push in`

**S38 / S39** 纯后期，见剧本。印章用朱砂 #C2362B，盖章音效用真实木印落纸声。

---

## 镜头语言总结（导演阐述）

1. **线条即立场。** 3D 世界只用直线构图（对称、正俯、网格），墨世界只用曲线（S 形、对角、留白）。到了终章，构图开始兼用两者。
2. **三次匹配剪辑撑起结构。** 墨线变青线（S02→S03，人被机器接管），墨手变机械手（S19，机器接替人守望），机器画的笑变小禾画的笑（S35，机器继承人）。三次剪辑讲的是同一件事的三个阶段。
3. **镜头离稻草人越来越近。** 序幕在太空般的高度，第一章是航拍，风暴里到特写，最后是 S35 的微距。观众是一步一步"走近"这个无用之物的。
4. **终镜不推近。** S37 里老年小禾只是远远一个影子，我们不给她特写。给不给答案的权利留给观众，这是戛纳式的克制。
5. **一秒钟的静默。** S22 的绝对静音是全片节奏的分水岭，前面是秩序，后面是失控。
