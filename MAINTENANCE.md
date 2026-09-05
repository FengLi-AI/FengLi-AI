# 浅色 GitHub 个人主页

采用用户确认的 Figma 浅色画板（1360 × 720），保留原字体轮廓、颜色、桌面线条和排版。

## 内容与文件

- `README.md`：GitHub 主页入口，引用独立 SVG 文件。
- `assets/profile-light.svg`：主视觉及自动循环动画，无 JavaScript、外部字体或外部图片依赖。
- `assets/profile-light-static.svg`：静态备份。
- `source/profile-body.html`：个人介绍、文字社交链接、代表作表格和关注方向。
- `source/content.json`：软件名称、画面英文标签、真实入口地址、动画速度配置。
- `source/figma-light.svg`：原画板导出，保留为视觉基线。
- `source/text-outlines.json`：软件词条和英文标签的字体轮廓，不包含字体文件。
- `build.py`：从源文件生成 README、动效图和本地预览。
- `source/outline-text.swift`：macOS CoreText 字体转轮廓工具。
- `index.html`：本地预览，使用 `<img>` 载入与 GitHub 相同的 SVG。

## 修改已有名称、顺序与速度

编辑 `source/content.json` 后，在此目录运行：

```sh
python3 build.py
```

软件名称必须有对应的 `source/text-outlines.json` 轮廓。删除、排序、链接更新和速度修改不需要重新操作 Figma。

## 新增软件词条

使用安装了原字体的 Mac 导出新轮廓。每个任务指定文本、字体文件和字号，例如：

```json
[{"text":"RAG","font":"/path/to/Humnst777 BlkCn BT Black.ttf","size":26.0}]
```

将任务保存为未提交的 `outline-jobs.local.json`，运行：

```sh
swift source/outline-text.swift outline-jobs.local.json > new-outlines.local.json
```

将新词条记录合并进 `source/text-outlines.json`，在 `source/content.json` 中加入该词条，再重新生成。公开仓库只保存轮廓，不上传字体文件。

## 动效与链接边界

SVG 自带屏幕行显现、光标闪烁、按键起伏、灵感冒出、弧形文字旋转、星星浮动与斜向滚动带。系统设置减少动态效果时，CSS 会停止动画并保留静态内容。

整张主图只链接个人网站。原图中的社交名称已改成 PROMPT ENGINEERING 和 AGENT LOOP，独立社交入口放在下方个人介绍的文字链接中。公众号使用用户提供的公开文章，通过文章作者进入公众号；不得使用带登录 token 的后台地址。

GitHub README 不执行自定义 JS，因此没有悬停放大和复制微信号功能。GitHub 外围主题不受画面控制。

## 发布与核验

本仓库名必须与用户名一致：`FengLi-AI/FengLi-AI`。个人网站仓库 `FengLi-AI.github.io` 是另一个项目。

发布前查看生成文件差异；发布后检查 GitHub 主页的实际图片、动画、文字链接，以及手机下的表格显示。
