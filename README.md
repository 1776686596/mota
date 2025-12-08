# 📊 SciPlot-Copilot

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-Apache%202.0-green.svg)
![AI Powered](https://img.shields.io/badge/AI-Powered-purple.svg)

**🚀 AI 驱动的下一代科研可视化与逻辑梳理平台**

*融合大语言模型智慧，一键生成 Nature 级科研图表，智能梳理复杂实验逻辑。让数据说话，让逻辑可见。*

[快速开始](#-快速开始) • [功能特性](#-核心功能) • [使用示例](#-使用示例) • [技术架构](#-技术架构) • [贡献指南](#-贡献)

</div>

---

## ✨ 核心功能

### 📈 智能绘图工作室

用自然语言描述你想要的图表，AI 自动生成专业级可视化代码。

- **自然语言绘图**：用中文描述需求，AI 自动生成 matplotlib/seaborn 代码
- **多种图表类型**：支持散点图、折线图、柱状图、箱线图、热力图、小提琴图、直方图等
- **Nature 级样式**：内置多种顶刊风格模板（Nature、Science、Cell、PNAS 等）
- **AI 智能推荐**：根据数据特征自动推荐最适合的图表类型和设计方案
- **实时预览**：即时查看图表效果，支持多种格式导出（PNG、PDF、SVG、JPG）
- **代码透明**：完整展示生成的 Python 代码，方便学习和二次修改

### 🧠 逻辑思维导图

将实验流程文本智能转换为可视化的逻辑关系图。

- **智能逻辑梳理**：AI 分析实验步骤，自动提取关键节点和关系
- **交互式编辑**：支持拖拽、添加、删除节点，自由调整布局
- **多种布局算法**：层次布局、环形布局、网格布局
- **丰富导出格式**：支持 PNG/JPG/SVG 图片、JSON、Mermaid、Python 代码、GraphML

### 💬 AI 对话助手

与 AI 进行自然语言对话，获取数据分析建议和科研问题解答。

- **上下文感知**：AI 自动理解当前加载的数据特征
- **多轮对话**：支持连续对话，保持上下文记忆
- **快捷问题**：内置常用问题模板，一键获取分析建议
- **专业知识**：涵盖统计方法选择、图表设计、科研写作等领域

### 🔬 统计分析工具

提供全面的统计分析功能，满足科研数据分析需求。

| 功能类别 | 支持的方法 |
|---------|-----------|
| **假设检验** | 单样本 t 检验、独立样本 t 检验、配对样本 t 检验、单因素方差分析 (ANOVA)、Mann-Whitney U 检验、Shapiro-Wilk 正态性检验 |
| **回归分析** | 线性回归、多元回归，自动计算 R²、RMSE 等指标，可视化回归线 |
| **相关性分析** | Pearson、Spearman、Kendall 相关系数矩阵，热力图可视化 |
| **描述统计** | 均值、中位数、标准差、偏度、峰度等，分布直方图和箱线图 |

### 🔧 数据预处理

强大的数据清洗和转换工具，为分析做好准备。

- **缺失值处理**：均值/中位数/众数填充、前值/后值填充、删除缺失行、自定义值填充
- **数据转换**：数据类型转换、标准化、归一化、对数转换、独热编码
- **数据筛选**：按条件筛选行、选择保留列、支持多种比较运算符
- **数据采样**：随机采样、头部/尾部数据、等间隔采样、分层采样
- **实时对比**：显示处理前后的数据变化（行数、列数、缺失值、内存占用）

### 💾 项目管理

保存和恢复工作进度，生成专业分析报告。

- **保存项目**：保存数据集、绘图历史、对话记录、逻辑图、配置信息
- **加载项目**：随时恢复之前的工作进度，支持合并到当前项目
- **导出报告**：生成 Markdown 格式的分析报告，包含数据概览、统计分析、图表记录

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- 支持 OpenAI 兼容 API 的 LLM 服务

### 安装步骤

#### 方式一：使用安装脚本（推荐）

```bash
# 克隆项目
git clone https://github.com/your-repo/sciplot-copilot.git
cd sciplot-copilot

# 运行安装脚本
chmod +x setup.sh
./setup.sh
```

#### 方式二：手动安装

```bash
# 克隆项目
git clone https://github.com/your-repo/sciplot-copilot.git
cd sciplot-copilot

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 启动应用

```bash
# 激活虚拟环境（如果尚未激活）
source venv/bin/activate

# 启动应用
streamlit run app.py
```

应用将在浏览器中自动打开，默认地址：`http://localhost:8501`

### 配置 API

在侧边栏的「⚙️ API 配置」中设置：

| 配置项 | 说明 | 示例 |
|-------|------|------|
| **API Base URL** | LLM 服务地址 | `https://api.openai.com/v1` |
| **API Key** | 你的 API 密钥 | `sk-xxx...` |
| **模型** | 使用的模型名称 | `gpt-4`、`gpt-3.5-turbo` |

> 💡 支持所有 OpenAI 兼容的 API 服务，包括 OpenAI、Azure OpenAI、通义千问、智谱 AI 等。

---

## 📖 使用示例

### 示例 1：智能绑定数据绘图

```
请用 iris 数据集绘制一个散点图，x轴是花瓣长度，y轴是花瓣宽度，按物种着色
```

### 示例 2：自定义 Nature 风格图表

```
绘制一个 Nature 风格的柱状图，展示不同类别的平均值，添加误差棒，使用蓝色系配色
```

### 示例 3：实验逻辑梳理

```
1. 首先将样品 A 与试剂 B 混合，在 50°C 下搅拌 2 小时
2. 冷却至室温后，进行离心分离
3. 上清液用于 HPLC 分析，沉淀物经洗涤干燥后进行 XRD 表征
```

### 示例 4：统计分析

```
对不同组别进行独立样本 t 检验，比较均值差异是否显著
```

### 示例 5：数据预处理

```
使用中位数填充缺失值，然后对数值列进行标准化处理
```

---

## 🎨 支持的图表类型

| 图表类型 | 描述 | 适用场景 |
|---------|------|----------|
| 📊 散点图 | 展示两变量关系 | 相关性分析、聚类可视化 |
| 📈 折线图 | 展示趋势变化 | 时间序列、连续数据 |
| 📊 柱状图 | 比较分类数据 | 分组对比、频率统计 |
| 📦 箱线图 | 展示数据分布 | 统计分析、异常值检测 |
| 🔥 热力图 | 展示矩阵数据 | 相关性矩阵、混淆矩阵 |
| 🎻 小提琴图 | 展示分布密度 | 分布对比、密度估计 |
| 📊 直方图 | 展示频率分布 | 数据分布、正态性检验 |

---

## 🏗️ 技术架构

### 项目结构

```
sciplot-copilot/
├── app.py                 # 主入口文件
├── requirements.txt       # Python 依赖
├── setup.sh              # 安装脚本
├── start.sh              # 启动脚本
├── config.example.json   # 配置文件示例
│
├── core/                 # 核心模块
│   ├── __init__.py
│   ├── config_manager.py # 配置管理
│   ├── data_loader.py    # 数据加载器
│   ├── llm_service.py    # LLM 服务封装
│   ├── logic_graph.py    # 逻辑图处理
│   └── sandbox.py        # 代码沙箱执行
│
├── ui/                   # UI 组件
│   ├── __init__.py
│   ├── chat_tab.py       # AI 对话标签页
│   ├── dashboard.py      # 数据仪表盘
│   ├── data_explorer.py  # 数据探索器
│   ├── data_preprocessing.py  # 数据预处理
│   ├── logic_graph_tab.py     # 逻辑图标签页
│   ├── logic_graph_helpers.py # 逻辑图辅助函数
│   ├── plot_tab.py       # 绘图标签页
│   ├── project_manager.py # 项目管理
│   ├── sidebar.py        # 侧边栏
│   ├── statistics_tab.py # 统计分析标签页
│   └── styles.py         # 样式定义
│
├── utils/                # 工具模块
│   ├── __init__.py
│   ├── font_config.py    # 字体配置
│   └── session.py        # Session 状态管理
│
├── data/                 # 示例数据集
│   ├── iris.csv          # 鸢尾花数据集
│   ├── penguins.csv      # 企鹅数据集
│   ├── tips.csv          # 餐厅小费数据集
│   ├── diamonds.csv      # 钻石数据集
│   └── ...               # 更多科研数据集
│
└── tests/                # 测试文件
    ├── __init__.py
    └── test_core.py
```

### 技术栈

| 类别 | 技术 |
|------|------|
| **前端框架** | Streamlit |
| **可视化库** | Matplotlib、Seaborn |
| **AI 引擎** | OpenAI 兼容 API |
| **数据处理** | Pandas、NumPy |
| **统计分析** | SciPy、Scikit-learn、Statsmodels |
| **流程图组件** | streamlit-flow-component、NetworkX |

---

## 📦 内置数据集

| 数据集 | 行数 | 列数 | 描述 | 适用场景 |
|-------|------|------|------|----------|
| `iris.csv` | 150 | 5 | 鸢尾花数据集 | 分类分析、散点图 |
| `penguins.csv` | 344 | 7 | 企鹅数据集 | 多变量分析、分组比较 |
| `tips.csv` | 244 | 7 | 餐厅小费数据 | 回归分析、分类比较 |
| `diamonds.csv` | 53940 | 10 | 钻石数据集 | 大数据可视化、价格预测 |
| `cell_viability.csv` | - | - | 细胞活力测试 | 科研场景测试 |
| `enzyme_activity.csv` | - | - | 酶活性分析 | 科研场景测试 |
| `material_test.csv` | - | - | 材料测试数据 | 科研场景测试 |
| `xrd_analysis.csv` | - | - | XRD 分析数据 | 科研场景测试 |

---

## 🔒 隐私与安全

- ✅ 所有数据处理在本地完成
- ✅ API 密钥仅用于调用 LLM 服务，不会存储到服务器
- ✅ 不会上传或存储你的数据
- ✅ 代码在安全沙箱中执行

---

## 🧪 运行测试

```bash
# 激活虚拟环境
source venv/bin/activate

# 运行测试
python tests/test_core.py
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 开源协议

本项目采用 [Apache License 2.0](LICENSE) 开源协议。

---

## 📮 联系我们

如有问题或建议，欢迎通过以下方式联系：

- 提交 [GitHub Issue](https://github.com/your-repo/sciplot-copilot/issues)
- 发送邮件至：mota@daisheng.xyz

---

<div align="center">

**让科研可视化更简单、更智能！** 🎉

Made with ❤️ by SciPlot-Copilot Team

</div>