# HTML 按钮与 JavaScript 的对接原理（零基础）

本文假设你完全不懂前端开发，从最底层解释：用户在网页上点了一个按钮，浏览器怎么知道该执行哪段代码。

---

## 一、核心概念：事件（Event）

浏览器的世界里，用户做的每一件事都是**事件**：

| 用户动作 | 事件名称 |
|---------|---------|
| 点击鼠标 | `click` |
| 鼠标移上去 | `mouseenter` |
| 键盘按下 | `keydown` |
| 表单提交 | `submit` |
| 页面加载完成 | `load` |

**按钮对接 JS 的本质：告诉浏览器——当 `click` 事件发生时，执行这段 JS 代码。**

---

## 二、方法一：onclick 属性（项目中最常用）

### 2.1 最基本的形式

```html
<button onclick="alert('Hello')">点我</button>
```

**拆解：**

| 部分 | 含义 |
|------|------|
| `<button>` | HTML 标签：这是一个按钮 |
| `onclick=` | HTML 属性：当"点击"事件发生时 |
| `"alert('Hello')"` | 要执行的 JS 代码 |

用户点击按钮 → 浏览器看到 `onclick` → 执行 `"alert('Hello')"` → 弹出提示框。

### 2.2 调用函数（项目中的真实写法）

代码一多就不能全塞在 `onclick` 里，于是把代码包成**函数**，`onclick` 只负责调用函数名。

```html
<!-- HTML 部分 -->
<button onclick="saveSettings()">Save</button>

<!-- JS 部分（在同一个 HTML 文件的 <script> 标签里） -->
<script>
function saveSettings() {
    const url = document.getElementById('set-base-url').value;
    alert('你要保存的地址是：' + url);
}
</script>
```

**执行流程：**

```
用户点击 Save 按钮
    │
    ▼
浏览器看到 onclick="saveSettings()"
    │
    ▼
去 <script> 里找名叫 saveSettings 的函数
    │
    ▼
执行函数体内的代码
    │
    ▼
弹出 alert
```

### 2.3 传参数进去

```html
<button onclick="deleteFile('unit_outline.json')">删除</button>

<script>
function deleteFile(filename) {
    console.log('正在删除：' + filename);
}
</script>
```

点击按钮时，浏览器会把 `'unit_outline.json'` 传给 `deleteFile` 函数。

### 2.4 阻止事件冒泡（项目中的 chips）

看这段代码：

```html
<div onclick="window.location.href='/unit.html?id=123'">
    <!-- 卡片整体可点击 -->
    <span onclick="event.stopPropagation(); window.open('/file.html')">html</span>
</div>
```

**问题：** 点击 `html` 小标签时，浏览器会先执行标签的 `onclick`，然后**继续往上冒泡**，执行外层 `div` 的 `onclick`。结果是：新标签页打开了 `file.html`，**同时**当前页面也跳转到了 `unit.html`。

**解决：** `event.stopPropagation()` 告诉浏览器："到此为止，别往上传了。"

| 代码 | 作用 |
|------|------|
| `event` | 浏览器自动传入的参数，代表这个点击事件的详细信息 |
| `.stopPropagation()` | "阻止传播"，事件不再向上层元素传递 |

---

## 三、方法二：addEventListener（更专业，但项目里没用）

虽然本项目全用 `onclick`，但业界更常用 `addEventListener`：

```html
<button id="save-btn">Save</button>

<script>
// 找到按钮
const btn = document.getElementById('save-btn');

// 给它绑定点击事件
btn.addEventListener('click', function() {
    alert('保存成功');
});
</script>
```

**两种方法的区别：**

| | `onclick` | `addEventListener` |
|--|-----------|-------------------|
| 写法 | 直接写在 HTML 标签上 | 写在 `<script>` 里 |
| 绑定多个函数 | 后面的覆盖前面的 | 可以绑定多个，都会执行 |
| 适合谁 | 简单页面、快速开发 | 大型项目、专业开发 |
| 本项目使用情况 | ✅ 全部使用 | ❌ 未使用 |

---

## 四、方法三：a 标签（链接伪装成按钮）

在 `unit.html` 里，文件卡片不是用 `<button>`，而是用 `<a>`：

```html
<a href="/static/outputs/Unit_A1_xxx/L1.html" target="_blank">
    <div>文件名</div>
    <span>View</span>
</a>
```

`<a>` 标签天生就是"点击跳转"，不需要写 `onclick`。浏览器会自动根据 `href` 属性决定跳到哪里。

| 属性 | 作用 |
|------|------|
| `href="/static/outputs/..."` | 点击后打开这个地址 |
| `target="_blank"` | 在新标签页打开 |

---

## 五、项目中所有按钮的完整清单

### index.html

```html
<!-- 1. 打开 Wizard 页面 -->
<button onclick="goWizard()">Start Wizard</button>

<!-- 2. 打开 Quick 页面 -->
<button onclick="goQuick()">Quick Generate</button>

<!-- 3. 打开设置弹窗 -->
<button onclick="toggleSettingsModal()">⚙️</button>

<!-- 4. 关闭弹窗 -->
<button onclick="toggleSettingsModal()">Cancel</button>

<!-- 5. 保存设置（调用接口） -->
<button onclick="saveSettings()">Save</button>

<!-- 6. Recent Unit 卡片 -->
<div onclick="window.location.href='/unit.html?id=xxx'">
    <span onclick="event.stopPropagation(); window.open('/file.html')">html</span>
</div>
```

### wizard.html

```html
<!-- 7. 分析级别 -->
<button onclick="analyzeLevel()">Analyze</button>

<!-- 8. 开始生成（SSE 流式） -->
<button onclick="startGeneration()">Generate</button>
```

---

## 六、常见问题

### Q1：函数名写错了怎么办？

```html
<button onclick="saveSetting()">Save</button>  <!-- 少了个 s -->

<script>
function saveSettings() {  // 函数名是 saveSettings
    ...
}
</script>
```

点击按钮后，浏览器控制台会报错：`saveSetting is not defined`。按钮没反应。

### Q2：JS 写在 HTML 的哪里？

必须放在 `<script>` 标签里，通常放在 `</body>` 之前：

```html
<!DOCTYPE html>
<html>
<head>...</head>
<body>
    <button onclick="foo()">按钮</button>
    
    <!-- JS 代码放这里 -->
    <script>
        function foo() {
            alert('OK');
        }
    </script>
</body>
</html>
```

如果 `<script>` 放在 `<button>` 前面，点击时函数还没定义，也会报错。

### Q3：`onclick` 里的引号怎么写？

HTML 属性用双引号包裹，里面的 JS 字符串就用单引号：

```html
<!-- ✅ 正确：外层双引号，内层单引号 -->
<button onclick="alert('Hello')">点我</button>

<!-- ❌ 错误：内外都是双引号，浏览器会混乱 -->
<button onclick="alert("Hello")">点我</button>
```

### Q4：为什么有的按钮点完页面会刷新？

如果按钮在 `<form>` 表单里，且没有写 `type="button"`，浏览器默认认为是"提交表单"，会导致页面刷新。

```html
<!-- ✅ 正确：显式声明这是普通按钮，不是提交按钮 -->
<button type="button" onclick="save()">Save</button>

<!-- ❌ 错误：在 form 里不写 type，点完页面会刷新 -->
<button onclick="save()">Save</button>
```

本项目没有使用 `<form>` 标签，所以不存在这个问题。

---

## 七、一句话总结

> **HTML 按钮通过 `onclick="函数名()"` 这个属性，告诉浏览器：用户点击时，去 `<script>` 标签里找到同名函数并执行。**

这就是按钮和 JS 对接的全部原理。
