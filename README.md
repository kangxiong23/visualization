# 2026年厄尔尼诺事件：赤道太平洋海温与地转流可视化分析

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://visualization-mzoyeqwa6qmat2u3yi4wf7.streamlit.app/)

## 📌 项目简介

本项目针对 2026 年春季厄尔尼诺快速发展期（4–6 月），基于高分辨率海表温度（OISST）和地转流数据，系统分析赤道太平洋（170°W–120°W, 5°S–5°N）海温异常的空间传播规律、地转流的响应特征以及海温与流速之间的耦合关系。

项目创新性地采用 **HSV 颜色编码** 将洋流矢量场转化为热力图，同时表达方向与强度，并基于 **Streamlit** 构建交互式 Web 应用，支持动态参数调节与多维度探索。

---

## ✨ 功能特色

- **📈 时间序列分析**：展示 ONI 月值指数与自定义周平均 SSTA，弥补官方指数滞后性
- **🗺️ Hovmöller 图**：展示海温异常在经度–时间平面上的传播特征，支持交互式纬度切换
- **🌊 洋流方向与强度热力图**：基于 HSV 颜色编码，直观展示矢量场方向与流速大小
- **📐 流速剖面分析**：纬向剖面用于流轴定位，经向剖面用于流轴处流速经向分布分析
- **🔗 海温–流速耦合回归**：散点图 + 线性回归，定量评估 SSTA 对纬向流速的驱动作用

---

## 📂 数据说明

本项目使用以下公开数据集：

| 数据集 | 来源 | 时间范围 | 空间范围 |
|--------|------|----------|----------|
| ONI 指数 | NOAA CPC | 1950–2026 | Niño3.4 区域 |
| OISST 海温 | NOAA NCEI v2.1 | 2026-04-01 – 2026-06-09 | 全球（裁剪至研究区域） |
| 地转流 | NOAA ERDDAP (miamicurrents) | 2026-04-01 – 2026-06-09 | 120°E–290°E, 5°S–5°N |

> ⚠️ **数据文件较大**（海温约 1GB），未包含在本仓库中。请从以下方式获取：
> - 手动下载：按照论文第 2 章所述方法从 NOAA 官网下载
> - 云存储：通过公开 URL 下载（待上传后补充链接）

将数据文件放置于 `data/raw/` 对应子目录下即可运行。

---

## 🛠️ 技术栈

- **Python 3.12**
- **Streamlit** – 交互式 Web 框架
- **Xarray + NetCDF4** – 多维科学数据处理
- **Matplotlib** – 静态图表绘制
- **Pandas + NumPy** – 数据处理与统计分析
- **SciPy** – 线性回归与统计检验

---

## 🚀 本地运行

1. **克隆仓库**

```bash
git clone https://github.com/你的用户名/你的仓库名.git
cd 你的仓库名
```

2. **创建虚拟环境并安装依赖**

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

3. **准备数据**

按照论文第 2 章的方法，将三个数据集放入 `data/raw/` 对应子目录：

```
data/raw/
├── ENSO/
│   ├── oni.ascii.txt
│   └── weekly_ssta.txt      # 运行 calc_oni.py 生成
├── SST/
│   └── sst_2026_04_06_combined.nc
└── currents/
    └── currents_2026_04_06_full_lon_extended.nc
```

4. **运行应用**

```bash
streamlit run app.py
```

应用将在 http://localhost:8501 启动。

---

## 📄 论文与成果

本项目配套课程论文《2026年厄尔尼诺事件下赤道太平洋海温与地转流的时空演变及其耦合关系分析》，详细阐述了研究背景、数据方法、建模过程与结果讨论。

---
