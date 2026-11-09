[English](README.md) | 简体中文

# simulation-explainer-video

一个用于制作**仿真驱动型讲解视频**的 agent skill + 渲染引擎：图灵机在屏幕上真实运行，天平实时累加求和，选择树只长出一条绿色路径——而不是给幻灯片配上旁白。

这套方法逆向自漫士沉思录（卢睿）的讲解视频：他的 P 与 NP 一集里，一台真正的图灵机运行了五分钟，作为整集的核心论证。拆解方法本身——不只是画面风格——记录在 `docs/METHOD.md` 中。

**背后的故事：**[Muse Amazed Me Again — With One-Shot Imitation Learning](https://lianggou.github.io/2026/11/08/muse-amazed-me-again-explainer-video.html)——一篇博客，讲一次演示（漫士的那支视频）如何变成这个 skill 包，以及模仿学习自身的数学对这个结果说了什么。**观看[上下对比视频](https://github.com/LiangGou/simulation-explainer-video/blob/main/examples/turing-machine-np/output/comparison-v1.mp4)**：原版在上、仿制版在下，逐镜头对齐。

## 方法，五句话

1. 先把题目拆成节拍；在动手制作之前，把每个节拍的主题、转场和旁白全部锁定在剧本里。
2. 每个节拍配一台**能真正运行的仿真**——计算出的状态驱动每一处画面；数字永远不是手敲上去的。
3. 全片一个舞台、一套配色；论点句以标题卡落地，而不是藏在字幕里。
4. 定义永远迟到：先演示 → 再给生活比喻 → 再跑完整实例 → 最后才下定义。
5. 音频最后做；交付前用双模型 ASR 核验每一个说出口的数字。

## 快速上手（给 agent）

把这个仓库 clone 到你的 agent 的 skills 文件夹（或任意位置），然后让你的 agent 读 **`SKILL.md`**——完整的方法、制作流程、引擎 API 和完成标准都在里面。把示例 episode 从头到尾渲染一遍：

```bash
pip install -r requirements.txt        # Pillow（+ 可选的 faster-whisper，用于 QA）
python3 -m engine.synth examples/turing-machine-np     # 旁白 -> timeline.json（需要 TTS 插件，见 docs/adapters.md）
python3 -m engine.build examples/turing-machine-np stills   # QA 静帧——逐张读
python3 -m engine.build examples/turing-machine-np          # 完整渲染 -> turing-segment-v1.mp4
python3 -m engine.qa asr examples/turing-machine-np         # 双模型 ASR 数字核验
python3 -m engine.qa frame0 examples/turing-machine-np/turing-segment-v1.mp4
```

（示例里已经提交了 `timeline.json`，所以 `engine.build` 可以直接运行；只有改了剧本才需要重跑 `engine.synth`。）

开始你自己的 episode：把 `templates/episode/` 复制到 `examples/<你的题目>/`，用 `templates/script-template.md` 写剧本、用 `templates/shot-spec-template.md` 写分镜规格，填好 `episode.py`，再跑同样的命令。

## 架构（三层）

- **`engine/`** —— 只有机制，不认识任何题目：帧循环、缓动、辉光渲染、舞台 + 配色、字幕烧录、时间轴、ffmpeg 组装、TTS/ASR 适配器接口、QA 工具链。
- **`engine/archetypes/`** —— 在多个 episode 中反复出现的参数化仿真模式：`tape_machine`（纸带机）、`weighted_mix`（加权混合）、`branching_tree`（分支树）、`accumulator_scale`（累加天平）、`containment_stage`（包含关系舞台）、`title_card`（标题卡）。每个模式只吃数据和配置；没有任何 episode 内容。
- **Episode**（`examples/<题目>/`）—— 每个题目新生成的内容：剧本、仿真定义（用本集数据实例化的模式）、分镜编排胶水。一个 episode 就是一个文件夹，其中的 `episode.py` 暴露 `SEGMENTS`、`SUBS`、`SCENES`、`ORDER`、`PADS`、`PROBES`——引擎以同一套方式渲染任何这样的文件夹。

生长纪律：只抽象已经在两个 episode 中重复出现过的形状；只用过一次的形状留在 episode 层；第三次出现时，它才毕业进入模式层。详见 `docs/DESIGN.md`。

## 仓库结构

```
SKILL.md                  技能本体：方法、流程、引擎 API、完成标准
docs/METHOD.md            拆解方法详解
docs/DESIGN.md            三层架构 + 生长纪律
docs/adapters.md          TTS / ASR 适配器接口（附 Muse 实现示例）
engine/                   帧管线、舞台、时间轴、字幕、合成、组装、QA
engine/archetypes/        六个仿真模式
templates/                剧本 + 分镜规格模板、episode 起始骨架
examples/turing-machine-np/   完整示例 episode（剧本、规格、仿真、静帧）
```

## 环境要求

- Python 3.10+ 与 [Pillow](https://pypi.org/project/Pillow/)
- PATH 中有 `ffmpeg` / `ffprobe`
- 一个用于旁白的 TTS 插件（任意 CLI；通过 `SEV_TTS_CMD` / `SEV_TTS_BIN` 配置——见 `docs/adapters.md`）。参考环境使用 Muse 内置 TTS 的 Aria 音色。
- 可选：`faster-whisper`，用于 ASR 数字核验工具链。
- 字体：舞台默认解析 Noto CJK / DejaVu；可用 `SEV_FONT_*` 环境变量逐个覆盖字体角色。

## 示例作品

`examples/turing-machine-np/` 是一个完整的 episode：P 与 NP 故事中的图灵机一拍——一台真正运行的奇偶校验机（δ 规则表、步数计数器、黑板高亮全部由执行结果驱动），一台带实时求和天平的等分划分机（结局 254 = 254），一棵只有一条绿色路径的分支选择树，19 对 9216 的算账收尾，以及作为标志性画面的 P ⊆ NP 平台。它的 README 把每一个节拍映射回引擎与模式层。渲染成片就在这个仓库里：仿制版 [`output/turing-segment-v1.mp4`](examples/turing-machine-np/output/turing-segment-v1.mp4)（4 分 34.5 秒，1280×720），以及与漫士原版的[上下对比视频](examples/turing-machine-np/output/comparison-v1.mp4)（4 分 47 秒）——两个视频都能在各自的 GitHub 页面上直接播放。

## 许可证

MIT——见 `LICENSE`。
