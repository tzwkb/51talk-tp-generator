# 按钮与接口对接原理详解

本文用项目里**真实存在的 3 个例子**，从零讲解前端按钮如何调用后端接口。

---

## 预备知识：前后端怎么找到对方

```
浏览器地址栏：http://localhost:8000/
                        │
                        ▼
              FastAPI 后端运行在 8000 端口
                        │
                        ▼
              前端 HTML 也是它提供的
```

前端通过 `window.location.origin` 获取当前地址（如 `http://localhost:8000`），所有 API 请求都发到这个地址。

```javascript
const API_BASE = window.location.origin;  // "http://localhost:8000"
```

---

## 例子 1：Settings 保存按钮（最典型：点按钮 → 发数据 → 存配置）

### 第 1 步：用户看到什么

页面底部有个 **Save** 按钮：

```html
<button onclick="saveSettings()" class="bg-primary text-white rounded-lg">Save</button>
```

- `onclick="saveSettings()"`：点击时执行 JavaScript 函数 `saveSettings()`

### 第 2 步：JS 收集表单数据

```javascript
async function saveSettings() {
    // 从输入框读取用户填的内容
    const payload = {
        ai_base_url:  document.getElementById('set-base-url').value || null,
        ai_temperature: parseFloat(document.getElementById('set-temp').value) || null,
        output_dir:   document.getElementById('set-output-dir').value || null,
        output_html:  document.querySelector('[onclick*="export_html"]').getAttribute('data-on') === 'true',
        output_pdf:   document.querySelector('[onclick*="export_pdf"]').getAttribute('data-on') === 'true',
    };
    const apiKey = document.getElementById('set-api-key').value.trim();
    if (apiKey) payload.ai_api_key = apiKey;

    // ... 第 3 步
}
```

| 代码 | 作用 |
|------|------|
| `document.getElementById('set-base-url')` | 找到 ID 为 `set-base-url` 的输入框 |
| `.value` | 读取输入框里的文字 |
| `parseFloat(...)` | 把字符串转成数字（温度 0.7） |
| `|| null` | 如果为空，传 `null` 而不是空字符串 |

### 第 3 步：JS 发送 POST 请求

```javascript
try {
    const res = await fetch(`${API_BASE}/api/settings`, {
        method: 'POST',                           // ← 告诉后端：我要提交数据
        headers: { 'Content-Type': 'application/json' },  // ← 数据格式是 JSON
        body: JSON.stringify(payload)             // ← 把 JS 对象转成 JSON 字符串
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    toggleSettingsModal();  // 保存成功，关闭弹窗
} catch (e) {
    alert('Failed to save settings: ' + e.message);
}
```

| 参数 | 含义 |
|------|------|
| `method: 'POST'` | HTTP 方法，表示"提交/创建" |
| `headers` | 告诉后端：我发的是 JSON |
| `body: JSON.stringify(...)` | 把 `{ai_base_url: "...", ...}` 变成 `'{"ai_base_url":"...",...}'` |
| `await` | 等后端回复后再继续执行 |
| `res.ok` | HTTP 状态码 200-299 为 true，否则为 false |

### 第 4 步：后端接收并处理

后端用 **FastAPI** 框架，Python 代码：

```python
from pydantic import BaseModel
from typing import Optional

# 定义数据格式（自动校验）
class SettingsUpdateRequest(BaseModel):
    ai_base_url: Optional[str] = None
    ai_api_key: Optional[str] = None
    ai_temperature: Optional[float] = None
    output_dir: Optional[str] = None
    output_html: Optional[bool] = None
    output_pdf: Optional[bool] = None

# 注册接口地址
@app.post("/api/settings")
async def update_settings(req: SettingsUpdateRequest):
    # req 就是前端发来的 JSON，已经自动解析好了
    if req.ai_base_url is not None:
        config.AI_BASE_URL = req.ai_base_url
    if req.ai_api_key is not None:
        config.AI_API_KEY = req.ai_api_key
    if req.output_dir is not None:
        config.OUTPUT_DIR = req.output_dir
    # ... 更新其他字段
    
    # FastAPI 自动返回 HTTP 200（空 JSON）
    return {"status": "ok"}
```

| 概念 | 作用 |
|------|------|
| `BaseModel` | 定义"数据应该长什么样"，FastAPI 自动校验 |
| `Optional[str]` | 这个字段可以是字符串，也可以不传 |
| `@app.post("/api/settings")` | 声明：POST 请求发到 `/api/settings` 时，执行这个函数 |
| `req.ai_base_url` | 直接读取前端发来的 `ai_base_url` 值 |

### 完整流程图

```
用户点击 Save 按钮
    │
    ▼
浏览器执行 saveSettings()
    │
    ▼
JS 读取各输入框的值，组装成 payload 对象
    │
    ▼
fetch POST http://localhost:8000/api/settings
    │        Body: {"ai_base_url":"...","output_pdf":true,...}
    ▼
FastAPI 接收 → Pydantic 自动校验格式
    │
    ▼
更新 config.py 里的变量
    │
    ▼
返回 HTTP 200
    │
    ▼
JS 收到响应 → 关闭弹窗
```

---

## 例子 2：Recent Units 加载（页面打开自动获取）

### 第 1 步：页面加载时自动执行

```javascript
// index.html 底部
loadUnits();  // 页面一打开就调用
```

### 第 2 步：JS 发送 GET 请求

```javascript
async function loadUnits() {
    const res = await fetch(`${API_BASE}/api/units`);  // GET 请求，默认就是 GET
    const units = await res.json();  // 把返回的 JSON 字符串转成 JS 对象/数组
    
    // 用数组生成 HTML 卡片
    container.innerHTML = units.map(u => {
        return `<div class="bg-card rounded-2xl p-6...">${u.name}</div>`;
    }).join('');
}
```

| 代码 | 作用 |
|------|------|
| `fetch(.../api/units)` | 发 GET 请求（不写 method 默认就是 GET） |
| `await res.json()` | 后端返回的是 JSON 文本，转成 JS 数组 |
| `units.map(...)` | 把每个 unit 对象转成一段 HTML |
| `.join('')` | 把所有 HTML 片段拼成一个大字符串 |

### 第 3 步：后端扫描目录返回

```python
@app.get("/api/units")
async def list_units():
    out = Path(config.OUTPUT_DIR)
    units = []
    for d in sorted(out.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if d.is_dir() and d.name.startswith("Unit_"):
            # 读取 unit_outline.json 获取名称
            outline = json.loads((d / "unit_outline.json").read_text())
            
            # 收集目录下的文件
            files = []
            for f in sorted(d.iterdir()):
                if f.is_file() and f.suffix in (".json", ".html", ".pdf"):
                    files.append({"name": f.name, "path": f"/static/outputs/{d.name}/{f.name}"})
            
            units.append({
                "id": d.name,
                "name": outline.get("overarching_objective", d.name),
                "level": outline.get("level", ""),
                "lessons_count": len(outline.get("lessons", [])),
                "files": files,
            })
    return units
```

后端直接扫描硬盘上的 `output/` 目录，把每个 `Unit_xxx` 文件夹的信息打包成 JSON 数组返回。

---

## 例子 3：Wizard 生成按钮（流式响应：SSE）

这是最复杂的。普通接口是"一问一答"，而 AI 生成需要时间，前端需要**实时看到进度**。

### 技术：SSE（Server-Sent Events）

后端不是一次性返回结果，而是像水管一样，**一行一行地推送数据**到前端。

### 第 1 步：前端发送 POST，但用 ReadableStream 读取

```javascript
async function startGeneration() {
    const response = await fetch(`${API_BASE}/api/unit/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
    });
    
    // 关键：拿到响应体作为一个"可读流"
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
        const { done, value } = await reader.read();  // 等待后端推送下一行
        if (done) break;
        
        const chunk = decoder.decode(value);  // 二进制 → 字符串
        const lines = chunk.split('\n');
        
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.slice(6));  // 去掉 "data: " 前缀
                
                if (data.type === 'progress') {
                    updateProgressBar(data.lesson, data.total);
                } else if (data.type === 'log') {
                    appendLog(data.message);
                } else if (data.type === 'complete') {
                    showResult(data.files);
                } else if (data.type === 'error') {
                    showError(data.message);
                }
            }
        }
    }
}
```

### 第 2 步：后端开线程，用 Queue 推送事件

```python
import queue

@app.post("/api/unit/generate")
async def generate_unit(req: GenerateUnitRequest):
    q = queue.Queue()
    
    def _worker():  # 在工作线程里执行（不阻塞主线程）
        try:
            # ... 生成 unit ...
            q.put(("progress", {"event": "start", "total": 10}))
            
            for lesson in lessons:
                q.put(("progress", {"event": "progress", "lesson": n, "status": "generating"}))
                generate_lesson(level, lesson, outline, unit_dir)
                q.put(("progress", {"event": "progress", "lesson": n, "status": "done"}))
            
            q.put(("complete", result))
        except Exception as e:
            q.put(("error", str(e)))
    
    threading.Thread(target=_worker, daemon=True).start()
    return StreamingResponse(_sse_event_generator(q), media_type="text/event-stream")
```

### 第 3 步：Queue → SSE 格式转换器

```python
async def _sse_event_generator(q: queue.Queue):
    while True:
        event_type, data = q.get()  # 阻塞等待事件
        if event_type is None:
            break
        
        # SSE 格式：每行以 "data: " 开头，两个换行结束一条消息
        yield f"data: {json.dumps({'type': event_type, **data})}\n\n"
```

### SSE 数据格式

后端推送的原始文本长这样：

```
data: {"type": "progress", "lesson": 1, "total": 10, "status": "generating"}

data: {"type": "log", "message": "Generating outline..."}

data: {"type": "complete", "files": [...]}

```

前端按行读取，解析 `data: ` 后面的 JSON。

---

## 四种 HTTP 方法的区别

| 方法 | 用途 | 项目中的例子 |
|------|------|-------------|
| **GET** | 获取数据 | `/api/units` 获取 Unit 列表 |
| **POST** | 提交数据/创建资源 | `/api/settings` 保存配置、`/api/unit/generate` 开始生成 |
| **PUT** | 更新资源（完整替换） | 本项目未使用 |
| **DELETE** | 删除资源 | 本项目未使用 |

---

## 数据格式：JSON

前后端之间传递的数据全是 **JSON 格式**。

### JS 对象 → JSON 字符串（前端发请求时）

```javascript
const obj = { name: "Unit1", level: "A1" };
const json = JSON.stringify(obj);
// 结果：'{"name":"Unit1","level":"A1"}'
```

### JSON 字符串 → JS 对象（前端收响应时）

```javascript
const json = '{"name":"Unit1","level":"A1"}';
const obj = JSON.parse(json);
// 结果：{ name: "Unit1", level: "A1" }
console.log(obj.level);  // "A1"
```

### Python 字典 → JSON 字符串（后端返回时）

```python
import json
data = {"name": "Unit1", "level": "A1"}
json_str = json.dumps(data)
# 结果：'{"name": "Unit1", "level": "A1"}'
```

FastAPI 会自动帮你做 `json.dumps()`，直接 `return data` 即可。

---

## 总结：按钮对接接口的通用公式

```
HTML 按钮
    onclick="函数名()"
        │
        ▼
JavaScript 函数
    1. 收集数据（读输入框、开关状态）
    2. 调用 fetch(url, {method, headers, body})
    3. 等待响应 await res.json()
    4. 更新页面（显示结果、改文字、弹提示）
        │
        ▼
FastAPI 后端
    @app.get/post("/api/xxx")
    async def 函数名(req: PydanticModel):
        # 处理数据
        return 结果
```

这就是"按钮和接口对接"的全部秘密。
