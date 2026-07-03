# 51Talk ESL Lesson Generator

中文 | [English](README.md)


## 概览

51Talk ESL 教案和课件生成工具，可生成面向沙特成人学习者的 HTML/PDF 课件，并带 Web 界面。

## 主要能力

- 生成完整 ESL lesson slide deck。
- 支持 HTML 和 PDF 输出。
- 包含 Web 界面以便操作和预览。

## 使用方式

按下方依赖、配置和 Web/脚本入口说明运行。

## 状态

该仓库仍按当前 README 的说明维护或使用。

## 注意事项

该仓库以生产 51Talk 教学计划和课件为核心，不是通用 CMS。

## 命令与配置参考

以下代码块从主 README 保留；命令、路径和配置键不翻译，复制时请以实际环境为准。

```bash
# Core dependencies
pip install openai playwright openpyxl
playwright install chromium

# Web interface dependencies
pip install -r requirements-web.txt
```

```bash
# Interactive mode
python main.py

# Auto runner (non-interactive, random topic + QA)
python auto_runner.py

# QA only (test existing unit)
python qa_tester.py [unit_folder_path]
```

```bash
python api.py
```

## 详细技术说明

主 README 保留了原始技术细节、历史说明、完整命令和文件结构。本文件作为中文版本维护核心说明；需要逐项核对命令时，请参照主 README 的代码块和路径。
