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

## 对应技术覆盖

### 环境要求

- Python 运行环境。
- 项目依赖按仓库中的 `requirements.txt` 或现有安装说明安装。
- Web 模式和 CLI 模式共用同一套课程生成逻辑。

### 快速开始

- CLI 模式用于从终端生成单课或整单元教案。
- Web 模式用于通过浏览器填写课程信息并生成内容。
- Auto Runner 用于批量或自动化运行既定课程生成流程。

### 运行模式

| 模式 | 用途 |
|---|---|
| 单课模式 | 生成一节课的教案、活动和课堂流程。 |
| 整单元模式 | 按单元结构批量生成多课内容。 |
| Auto Runner | 自动读取配置并连续执行生成任务。 |

### 内容合规与 QA

仓库保留内容审核红线、QA 检查和输出目录约定。生成结果应先经过合规和格式检查，再进入交付或人工审校。

## 补充流程说明

### CLI 模式

CLI 模式适合批量生成或在终端内快速验证课程。用户从 `main.py` 进入菜单后选择单课或整单元模式，按提示输入课程、级别、主题和输出位置。生成内容应写入 `output/`，便于后续检查和归档。

### Web 模式

Web 模式适合非技术用户。它把课程参数、单元结构和生成动作包装到浏览器界面中，减少直接操作命令行的成本。Web 流程仍应复用同一套内容生成、合规检查和 QA 逻辑。

### API 与自动化

仓库中的 API endpoint 说明用于把生成逻辑接入 Web 页面或自动化脚本。Auto Runner 适合在已有配置的情况下连续执行多个课程任务。

### 文件结构

`main.py`、`auto_runner.py`、Web 入口、配置文件、提示词和 `output/` 构成主要工作面。新增模式或提示词时，应同步更新 CLI、Web 和 QA 说明，避免三套入口行为不一致。

## 英文章节对应说明

### Features

对应中文的“主要能力”和“运行模式”。该项目的重点是把课程信息、教学目标和活动结构转成可交付教案。

### Requirements / Quick Start

对应中文的“环境要求”和“快速开始”。安装依赖后，用户可从 CLI 或 Web 入口启动。

### CLI Mode / Web Mode / API Endpoints

对应中文的“CLI 模式”“Web 模式”和“API 与自动化”。这三类入口应共享生成逻辑，只是面向不同使用者。

### File Structure / Content Compliance / QA System

对应中文的“文件结构”“内容合规与 QA”。内容审核红线、输出目录和 QA 检查是交付前必须确认的边界。

### Troubleshooting

排障时优先检查依赖安装、输入课程信息、输出目录权限、API/Web 入口参数，以及内容合规检查是否阻断生成。

## 交付检查清单

- 课程级别、单元、课次和主题是否与输入一致。
- 输出是否写入预期目录，文件名是否可追踪到课程或批次。
- 生成内容是否符合中东青少内容审核红线。
- CLI、Web 和 Auto Runner 入口是否使用同一套提示词和配置。
- QA 系统是否覆盖格式、缺字段、敏感内容和明显教学流程错误。
- 需要人工审校的内容是否已标记，避免把模型输出直接当作最终交付。

## 维护注意

新增课程模式时，应同步更新 CLI 菜单、Web 页面、API endpoint、Auto Runner 配置和 README。只改其中一个入口会造成文档与实际行为不一致。
