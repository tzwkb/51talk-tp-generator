# Recent Units 文件浏览页开发说明

## 一、项目架构

本项目采用**前后端分离**架构：

```
┌─────────────┐      HTTP API      ┌─────────────┐
│   浏览器     │  <─────────────>   │  FastAPI    │
│  (前端)      │    REST + SSE      │  (Python)   │
└─────────────┘                    └─────────────┘
```

- **后端**：Python FastAPI (`api.py`)，提供数据接口
- **前端**：纯静态 HTML 文件，无构建打包步骤

---

## 二、技术栈（极简，无构建工具）

| 技术 | 用途 | 引入方式 |
|------|------|----------|
| **HTML5** | 页面结构 | 原生 `.html` 文件 |
| **Tailwind CSS** | 样式框架 | CDN 链接 `<script src="https://cdn.tailwindcss.com">` |
| **Phosphor Icons** | 图标库 | CDN 链接 `<script src="https://unpkg.com/@phosphor-icons/web">` |
| **原生 JavaScript** | 交互逻辑 | `<script>` 标签内直接编写 |
| **Fetch API** | 向后端请求数据 | 浏览器内置 `fetch()` |

### 为什么不用 Vue/React？

本项目追求**零配置、零构建**，保存文件刷新浏览器即可生效，无需 `npm install` 或 `webpack/vite`。

---

## 三、后端 API（已存在，直接复用）

后端提供了两个关键接口：

### 1. 获取 Unit 列表
```
GET /api/units
```
返回所有 Unit 的摘要信息（名称、级别、文件列表等）。

### 2. 获取单个 Unit 的全部文件
```
GET /api/units/{unit_id}/files
```
返回指定 Unit 目录下的**所有文件**（不限于 JSON/HTML/PDF）。

**响应示例**：
```json
{
  "unit_id": "Unit_A1_0424_1145_MyUnit",
  "files": [
    {"name": "L1_Greeting_A1.json", "path": "/static/outputs/...", "type": "json"},
    {"name": "L1_Greeting_A1.html", "path": "/static/outputs/...", "type": "html"},
    {"name": "L1_Greeting_A1.pdf",  "path": "/static/outputs/...", "type": "pdf"},
    {"name": "unit_outline.json",   "path": "/static/outputs/...", "type": "json"}
  ]
}
```

---

## 四、unit.html 实现详解

### 4.1 页面作用

当用户在 Dashboard 点击某个 Unit 卡片时，浏览器跳转至此页面，**展示该 Unit 下的所有文件列表**，并支持点击打开。

### 4.2 URL 传参

页面通过 URL 查询参数接收 Unit ID：
```
/unit.html?id=Unit_A1_0424_1145_MyUnit
```

JavaScript 读取参数：
```javascript
const params = new URLSearchParams(window.location.search);
const unitId = params.get('id');
```

### 4.3 数据加载流程

```javascript
async function loadUnitFiles() {
    // 1. 调用后端 API
    const res = await fetch(`${API_BASE}/api/units/${encodeURIComponent(unitId)}/files`);
    const data = await res.json();
    
    // 2. 按文件名分类
    const lessons = data.files.filter(f => f.name.match(/^L\d+_/));
    const outline = data.files.filter(f => f.name === 'unit_outline.json');
    const others  = data.files.filter(f => !f.name.match(/^L\d+_/) && f.name !== 'unit_outline.json');
    
    // 3. 渲染到页面
    container.innerHTML = renderGroup('Lessons', lessons) 
                        + renderGroup('Unit Outline', outline)
                        + renderGroup('Other Files', others);
}
```

### 4.4 文件分类逻辑

| 类别 | 匹配规则 | 示例 |
|------|----------|------|
| **Lessons** | 文件名以 `L数字_` 开头 | `L1_Greeting_A1.html` |
| **Unit Outline** | 文件名等于 `unit_outline.json` | `unit_outline.json` |
| **Other Files** | 其余所有文件 | `_debug/` 下的调试文件 |

### 4.5 图标映射

根据文件后缀名显示不同图标：
```javascript
const iconMap = {
    json: 'ph-file-json',
    html: 'ph-file-html',
    pdf:  'ph-file-pdf',
    txt:  'ph-file-text',
    unknown: 'ph-file'
};
```

### 4.6 样式要点（Tailwind CSS）

| 类名 | 作用 |
|------|------|
| `bg-card` / `rounded-xl` / `border` | 白色卡片、圆角、边框 |
| `hover:shadow-md` | 鼠标悬停时阴影加深 |
| `flex items-center gap-3` | 水平排列、垂直居中、间距 |
| `truncate` | 文件名过长时自动截断 |
| `grid gap-3` | 网格布局、元素间距 |

---

## 五、index.html 修改说明

### 5.1 原行为

点击 Unit 卡片 → 直接 `window.open()` 打开第一个 HTML 文件。

```javascript
const firstFile = (u.files || []).find(f => f.type === 'html') || (u.files || [])[0];
const cardClick = firstFile ? `onclick="window.open('${firstFile.path}', '_blank')"` : '';
```

### 5.2 新行为

点击 Unit 卡片 → 跳转到 `unit.html?id=Unit_xxx`。

```javascript
const cardClick = `onclick="window.location.href='/unit.html?id=${encodeURIComponent(u.id)}'"`;
```

**chips 保持不变**：用户仍可点击卡片底部的 `json` / `html` / `pdf` 小标签直接打开单个文件。

---

## 六、整体数据流

```
用户点击卡片
    ↓
浏览器跳转 /unit.html?id=Unit_A1_xxxx
    ↓
unit.html 加载
    ↓
JS 读取 URL 中的 id 参数
    ↓
fetch('/api/units/Unit_A1_xxxx/files')
    ↓
后端扫描 output/Unit_A1_xxxx/ 目录
    ↓
返回文件列表 JSON
    ↓
JS 分类渲染 → Lessons / Unit Outline / Other Files
```

---

## 七、为什么这样设计？

| 设计决策 | 原因 |
|----------|------|
| 无前端框架 | 减少依赖，保存即生效 |
| CDN 引入 Tailwind | 无需配置构建工具，类名即样式 |
| URL 传参 | 无需状态管理，刷新不丢失 |
| 后端分类扫描 | 前端只做展示，业务逻辑在后端 |
| 保留 chips 直接打开 | 高频操作（看 HTML）无需多跳一步 |

---

## 八、如果要继续学习

1. **Tailwind CSS**：搜索 "Tailwind CSS 中文文档"，重点学习 `flex`、`grid`、`hover:`、`responsive` 前缀
2. **Fetch API**：搜索 "JavaScript fetch 教程"，学习 `async/await` 和错误处理
3. **FastAPI 静态文件**：搜索 "FastAPI StaticFiles"，理解 `app.mount("/", StaticFiles(html=True))` 的作用
4. **Phosphor Icons**：访问 `phosphoricons.com`，所有图标以 `ph-` 为前缀，如 `ph-file-pdf`
