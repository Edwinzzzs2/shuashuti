# 爱刷题 (AiShuaTi)

一个轻量级的移动端优先的在线刷题 Web 应用。支持 PWA，可添加到手机主屏幕离线使用。

## ✨ 特性

- **多题型支持**：支持单选、多选、判断题。
- **多种练习模式**：
  - **顺序练习**：按题库顺序刷题。
  - **随机练习**：随机抽取题目。
  - **错题模式**：自动记录错题，专门攻克薄弱点。
- **PWA 支持**：
  - 支持添加到手机主屏幕，像原生 App 一样使用。
  - 离线缓存，无网络也能刷题。
- **极致体验**：
  - 移动端优先的 UI 设计，适配刘海屏。
  - 快速响应，无多余加载。
  - 支持题目解析显示。

## 🚀 快速开始

### 1. 准备题库

本项目包含一个 Python 脚本 `py-timuToJson/parse_choice_111.py`，用于将特定格式的文本题库转换为 JSON。

**题库文本格式要求 (例如 `tiku.txt`)：**

```text
一、判断题
1、这是判断题内容。（√）
2、这是另一个判断题。（×）

二、单选题
1. 这是一个单选题？（A）
A. 选项一
B. 选项二
C. 选项三
D. 选项四

三、多选题
1. 这是一个多选题？（ABC）
A. 选项一
B. 选项二
C. 选项三
D. 选项四
```
*注意：脚本依赖“一、判断题”、“二、单选题”、“三、多选题”等标题来识别题目类型。*

**转换命令：**

```bash
# 进入脚本目录
cd py-timuToJson

# 运行转换 (请修改路径为实际路径)
python parse_choice_111.py -i "../json/tiku.txt" -o "../json/tiku.json" -p "2024Q1"
```
*   `-i`: 输入的文本文件路径。
*   `-o`: 输出的 JSON 文件路径。
*   `-p`: 题目前缀 ID（用于区分不同题库的题目）。

### 2. 导入题库

首页点击「导入题库」可以直接导入 PDF 或 JSON 文件：

- **PDF 导入**：适合从题库 PDF 自动解析题目，要求 PDF 文本包含“一、判断题 / 二、单选题 / 三、多选题”等分节标题。
- **JSON 导入**：适合导入已经转换好的题库文件，例如 `json/202601.json`、`json/202602.json` 这种题目数组。

JSON 支持直接使用题目数组：

```json
[
  {
    "id": "2026Q1-J1",
    "title": "冬季施工场地必须做好排水措施，防止现场结冰。",
    "type": "judge",
    "option": ["正确", "错误"],
    "answer": "A",
    "analysis": ""
  }
]
```

也支持带外层对象的格式，题目数组字段可以是 `questions`、`data` 或 `items`：

```json
{
  "questions": [
    {
      "id": "demo-S1",
      "title": "这是一个单选题？",
      "type": "single",
      "option": ["选项一", "选项二", "选项三", "选项四"],
      "answer": "A",
      "analysis": ""
    }
  ]
}
```

题目字段要求：

- `title`：题干。
- `type`：题型，支持 `judge`、`single`、`multi`。
- `option`：选项数组，判断题通常为 `["正确", "错误"]`。
- `answer`：答案，判断题使用 `A/B`，选择题使用选项字母，例如 `A` 或 `ABC`。

### 3. 配置内置题库

生成的 JSON 文件（例如 `202601.json`）需要放入 `json/` 目录。
然后修改 `index.html` 中的代码，将题库文件名指向新的 JSON 文件（如果需要动态加载不同题库，可能需要修改 `index.html` 的逻辑，目前默认为加载 `202601.json`）。

### 4. 运行项目

由于项目使用了 PWA (Service Worker) 和 Fetch API 加载本地 JSON，**不能**直接双击 HTML 文件打开，必须通过 HTTP 服务器运行。

**方式 A：使用 Python (推荐)**

```bash
# 在项目根目录下运行
python -m http.server 8000
```
然后浏览器访问：`http://localhost:8000`

**方式 B：使用 VS Code Live Server**
1. 在 VS Code 中安装 "Live Server" 插件。
2. 右键点击 `index.html`，选择 "Open with Live Server"。

## 📱 手机端安装 (PWA)

1. 确保手机和电脑在同一局域网，或者将项目部署到公网服务器（需支持 HTTPS，本地调试 localhost 除外）。
2. 使用手机浏览器（推荐 Safari 或 Chrome）访问地址。
3. **iOS (Safari)**：点击底部“分享”按钮 -> 选择“添加到主屏幕”。
4. **Android (Chrome)**：点击右上角菜单 -> 选择“安装应用”或“添加到主屏幕”。

## 🛠️ 技术栈

- **核心**：HTML5, CSS3, JavaScript
- **框架**：Vue.js 2.x (CDN)
- **UI 组件**：View Design (iView) (CDN)
- **PWA**：Service Worker, Web App Manifest
- **工具**：Python 3 (题库处理)

## 📝 目录结构

```
aishuati/
├── css/                # 样式文件
├── js/                 # 脚本文件 (Vue, iView 等)
├── json/               # 题库 JSON 文件
├── py-timuToJson/      # 题库格式转换工具
├── icons/              # PWA 图标
├── index.html          # 首页 (题库列表)
├── type.html           # 模式选择页
├── timu.html           # 答题页
├── service-worker.js   # PWA 离线缓存脚本
├── manifest.webmanifest # PWA 配置文件
└── README.md           # 项目说明
```

## 📄 License

MIT License
