# 51Talk Lesson Generator — API 文档

> 版本：v1.0.0  
> 服务地址：`http://localhost:8000`（开发）  
> Swagger UI：`http://localhost:8000/docs`

---

## 基础约定

- 所有接口前缀为 `/api`
- 静态文件（课件预览、下载）通过 `/static/outputs/{path}` 访问
- CORS 已开启，前端可直接调用
- 目前无需认证

---

## 1. 健康检查

### GET `/api/health`

**响应 (200)**
```json
{"status": "ok"}
```

---

## 2. AI 级别分析

### POST `/api/analyze-level`

根据用户自然语言描述，AI 推荐 CEFR 级别。

**请求体**
```json
{
  "description": "students who never learned English, want to ask directions at airport"
}
```

**响应 (200)**
```json
{
  "level": "A1",
  "reason": "Airport directions involve basic vocabulary and simple sentences, suitable for beginners."
}
```

---

## 3. 单元规划对话

### POST `/api/unit/plan-chat`

多轮单元规划聊天。首次调用创建 session，后续调用需带上 `session_id`。

### 3.1 首次请求

**请求体**
```json
{
  "session_id": null,
  "level": "A1",
  "unit_desc": "airport directions for absolute beginners"
}
```

### 3.2 后续请求

**请求体**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_input": "proceed"
}
```

**响应 (200)**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "ai_reply": "Great! I will create a 6-lesson unit about airport directions...",
  "ready_to_generate": false
}
```

**字段说明**
| 字段 | 类型 | 说明 |
|---|---|---|
| `session_id` | string | 首次为 `null`，后端创建并返回；后续必须带上 |
| `level` | string | 首次必填，CEFR 级别 A1–C1 |
| `unit_desc` | string | 首次必填，单元描述 |
| `user_input` | string | 后续必填，用户回复（如 `proceed` / `ok` / `start`） |
| `ai_reply` | string | AI 回复内容 |
| `ready_to_generate` | bool | `true` 时可调用 `/api/unit/generate` |

---

## 4. 生成完整单元

### POST `/api/unit/generate`

根据已准备好的 session，生成整个单元（大纲 + 所有课件）。

**请求体**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**返回格式**：`text/event-stream` (SSE)

### SSE 事件流

```
event: progress
data: {"event":"start","total":6,"unit_name":"Airport Directions"}

event: progress
data: {"event":"progress","lesson":1,"total":6,"name":"Greetings","status":"generating"}

event: log
data: {"line":"[1/3] Generating outline (A1 level)..."}

event: log
data: {"line":"  جاري إنشاء المخطط (مستوى A1)..."}

event: progress
data: {"event":"progress","lesson":1,"total":6,"name":"Greetings","status":"done"}

event: progress
data: {"event":"progress","lesson":2,"total":6,"name":"Checking In","status":"generating"}

...（逐课推进）...

event: complete
data: {
  "event": "complete",
  "unit_id": "Unit_A1_0424_1538_Airport_Directions",
  "unit_name": "Airport Directions",
  "level": "A1",
  "success": 6,
  "total": 6,
  "files": [
    {"name": "unit_outline.json", "path": "/static/outputs/Unit_A1_0424_1538_.../unit_outline.json", "type": "json"},
    {"name": "L1_Greetings_A1.html", "path": "/static/outputs/Unit_A1_0424_1538_.../L1_Greetings_A1.html", "type": "html"},
    {"name": "L1_Greetings_A1.pdf", "path": "/static/outputs/Unit_A1_0424_1538_.../L1_Greetings_A1.pdf", "type": "pdf"}
  ]
}
```

### 事件类型说明

| event | 说明 | data 字段 |
|---|---|---|
| `start` | 开始生成 | `total`, `unit_name` |
| `progress` | 单课进度 | `lesson`, `total`, `name`, `status` (`generating`/`done`/`failed`) |
| `log` | 原始 CLI 日志（双语） | `line` |
| `complete` | 全部完成 | `unit_id`, `unit_name`, `level`, `success`, `total`, `files` |
| `error` | 生成失败 | `message` |

### 前端接入示例 (JS)

```javascript
const evtSource = new EventSource("http://localhost:8000/api/unit/generate", {
  method: "POST",
  body: JSON.stringify({ session_id: "..." }),
  headers: { "Content-Type": "application/json" }
});

evtSource.addEventListener("progress", (e) => {
  const data = JSON.parse(e.data);
  console.log(`Lesson ${data.lesson}/${data.total}: ${data.status}`);
});

evtSource.addEventListener("log", (e) => {
  const data = JSON.parse(e.data);
  console.log(data.line);  // 原始双语日志
});

evtSource.addEventListener("complete", (e) => {
  const data = JSON.parse(e.data);
  console.log("Done! Files:", data.files);
  evtSource.close();
});
```

---

## 5. 生成单课

### POST `/api/lesson/generate`

快速生成单课，无需 session。

**请求体**
```json
{
  "level": "A1",
  "blueprint": "Lesson: Airport Directions\nVocabulary: gate, terminal, customs\nFunctional Language: Where is... / How do I get to...\nTopic: Airport"
}
```

**返回格式**：SSE，事件流与 `/api/unit/generate` 相同，但 `total: 1`。

---

## 6. 列出历史单元

### GET `/api/units`

返回 `output/` 目录下所有已生成的单元，按时间倒序。

**响应 (200)**
```json
[
  {
    "id": "Unit_A1_0424_1538_Airport_Directions",
    "name": "Airport Directions",
    "level": "A1",
    "lessons_count": 6,
    "created_at": "2026-04-24T15:38:00",
    "files": [
      {"name": "unit_outline.json", "path": "/static/outputs/Unit_A1_0424_1538_.../unit_outline.json", "type": "json"},
      {"name": "L1_Greetings_A1.html", "path": "/static/outputs/Unit_A1_0424_1538_.../L1_Greetings_A1.html", "type": "html"}
    ]
  }
]
```

---

## 7. 单元文件列表

### GET `/api/units/{unit_id}/files`

**路径参数**
- `unit_id` — 单元文件夹名，如 `Unit_A1_0424_1538_Airport_Directions`

**响应 (200)**
```json
{
  "unit_id": "Unit_A1_0424_1538_Airport_Directions",
  "files": [
    {"name": "unit_outline.json", "path": "/static/outputs/.../unit_outline.json", "type": "json"},
    {"name": "L1_Greetings_A1.html", "path": "/static/outputs/.../L1_Greetings_A1.html", "type": "html"},
    {"name": "L1_Greetings_A1.pdf", "path": "/static/outputs/.../L1_Greetings_A1.pdf", "type": "pdf"}
  ]
}
```

---

## 8. 静态文件访问

### GET `/static/outputs/{path}`

直接访问课件文件，用于：
- **HTML 预览**：`<iframe src="/static/outputs/Unit_A1_.../L1_Greetings_A1.html">`
- **PDF 下载**：`<a href="/static/outputs/Unit_A1_.../L1_Greetings_A1.pdf" download>`
- **JSON 下载**：直接 GET

---

## 错误码

| 状态码 | 场景 |
|---|---|
| 400 | session 未 ready、缺少必填参数 |
| 404 | session 不存在、单元文件夹不存在 |
| 500 | AI 生成失败、内部错误（SSE 中通过 `event: error` 返回） |
