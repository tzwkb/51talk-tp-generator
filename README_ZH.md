# 51Talk ESL Lesson Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)

[English](README.md) | 中文

## 概览

51Talk ESL 教案和课件生成工具，可生成面向沙特成人学习者的 HTML/PDF 课件，并带 Web 界面。

## 文档对齐说明

本 README_ZH.md 与英文 README.md 使用同一项目事实，但采用中文读者更容易扫描的结构。命令、路径、配置键和示例数据保持原样。

## 主要能力

- 生成单课、整单元和自动运行模式的 ESL 教案。
- 提供 CLI 和 Web 两套使用流程。
- 保留内容合规和 QA 检查说明。

## 主要能力

- 生成完整 ESL lesson slide deck。
- 支持 HTML 和 PDF 输出。
- 包含 Web 界面以便操作和预览。

## 使用方式

按下方依赖、配置和 Web/脚本入口说明运行。

## 注意事项

该仓库以生产 51Talk 教学计划和课件为核心，不是通用 CMS。

## 命令与配置参考

以下命令、路径和配置键保持原样，复制时请以实际环境为准。

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
