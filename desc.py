import streamlit as st
import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from pathlib import Path

# ================== 全局变量配置 ==================
ONI_FILEPATH = "data/oni.ascii.txt"
SST_FILEPATH = "data/sst_2026_04_06_combined.nc"
CURRENTS_FILEPATH = "data/currents_2026_04_06_full_lon_extended.nc"

# 研究区域（Niño3.4 区域）
LON_MIN, LON_MAX = 190.0, 240.0   # 170°W-120°W
LAT_MIN, LAT_MAX = -5.0, 5.0

# ================== 设置中文字体 ==================
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Microsoft YaHei', 'WenQuanYi Micro Hei']
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="描述性统计分析", layout="wide")
st.title("数据集描述性统计分析")
st.markdown("本页面展示海温、洋流和ONI指数的基本统计特征，包括均值、中位数、标准差、极值以及分布图形。")

# ================== 数据加载（缓存） ==================
@st.cache_data
def load_oni_data(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    records = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('SEAS'):
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        season, year, total, anom = parts[0], int(parts[1]), float(parts[2]), float(parts[3])
        season_map = {
            'DJF': '01-15', 'JFM': '02-15', 'FMA': '03-15', 'MAM': '04-15',
            'AMJ': '05-15', 'MJJ': '06-15', 'JJA': '07-15', 'JAS': '08-15',
            'ASO': '09-15', 'SON': '10-15', 'OND': '11-15', 'NDJ': '12-15'
        }
        date_str = f"{year}-{season_map[season]}"
        date = pd.to_datetime(date_str)
        records.append({'date': date, 'anom': anom})
    df = pd.DataFrame(records)
    return df.set_index('date')

@st.cache_data
def load_sst_data(filepath):
    ds = xr.open_dataset(filepath)
    ds = ds.squeeze()
    return ds

@st.cache_data
def load_currents_data(filepath):
    ds = xr.open_dataset(filepath)
    # 检查坐标名，确保兼容
    if 'longitude' not in ds.coords and 'lon' in ds.coords:
        ds = ds.rename({'lon': 'longitude'})
    if 'latitude' not in ds.coords and 'lat' in ds.coords:
        ds = ds.rename({'lat': 'latitude'})
    return ds

# 加载数据
oni_df = load_oni_data(ONI_FILEPATH)
ds_sst = load_sst_data(SST_FILEPATH)
ds_cur = load_currents_data(CURRENTS_FILEPATH)

# 研究区域裁剪
ssta_region = ds_sst['anom'].sel(lon=slice(LON_MIN, LON_MAX), lat=slice(LAT_MIN, LAT_MAX))

# 洋流数据：确保经度在0-360范围内，且裁剪
if ds_cur.longitude.min() < 0:
    lon_360 = np.where(ds_cur.longitude < 0, ds_cur.longitude + 360, ds_cur.longitude)
    ds_cur = ds_cur.assign_coords(longitude=('longitude', lon_360)).sortby('longitude')
u_region = ds_cur['u_current'].sel(longitude=slice(LON_MIN, LON_MAX), latitude=slice(LAT_MIN, LAT_MAX))
v_region = ds_cur['v_current'].sel(longitude=slice(LON_MIN, LON_MAX), latitude=slice(LAT_MIN, LAT_MAX))

# 转换为numpy数组并去除NaN
ssta_vals = ssta_region.values.flatten()
ssta_vals = ssta_vals[~np.isnan(ssta_vals)]

u_vals = u_region.values.flatten()
u_vals = u_vals[~np.isnan(u_vals)]

v_vals = v_region.values.flatten()
v_vals = v_vals[~np.isnan(v_vals)]

# 检查是否全部为NaN
if len(u_vals) == 0:
    st.error("洋流数据 u_current 全为 NaN，请检查数据文件或区域范围。")
    st.stop()
if len(v_vals) == 0:
    st.error("洋流数据 v_current 全为 NaN，请检查数据文件或区域范围。")
    st.stop()

# ================== 描述性统计指标计算 ==================
# 海温距平
ssta_mean = np.mean(ssta_vals)
ssta_median = np.median(ssta_vals)
ssta_std = np.std(ssta_vals)
ssta_min = np.min(ssta_vals)
ssta_max = np.max(ssta_vals)
ssta_q25 = np.percentile(ssta_vals, 25)
ssta_q75 = np.percentile(ssta_vals, 75)

# 洋流 u_current（带符号）
u_mean = np.mean(u_vals)
u_median = np.median(u_vals)
u_std = np.std(u_vals)
u_min = np.min(u_vals)
u_max = np.max(u_vals)

# 洋流 v_current（带符号）
v_mean = np.mean(v_vals)
v_median = np.median(v_vals)
v_std = np.std(v_vals)
v_min = np.min(v_vals)
v_max = np.max(v_vals)

# 可选：流速绝对值统计（用于分析流速大小）
u_abs_vals = np.abs(u_vals)
v_abs_vals = np.abs(v_vals)
u_abs_mean = np.mean(u_abs_vals)
v_abs_mean = np.mean(v_abs_vals)

# ONI 指数 (2020-2026)
oni_recent = oni_df.loc['2020':'2026']
oni_mean = oni_recent['anom'].mean()
oni_median = oni_recent['anom'].median()
oni_std = oni_recent['anom'].std()
oni_min = oni_recent['anom'].min()
oni_max = oni_recent['anom'].max()

# ================== 展示统计指标 ==================
st.header("1. 统计指标概览")

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("海温距平 (SSTA)")
    st.write(f"均值: {ssta_mean:.3f} °C")
    st.write(f"中位数: {ssta_median:.3f} °C")
    st.write(f"标准差: {ssta_std:.3f} °C")
    st.write(f"最小值: {ssta_min:.3f} °C")
    st.write(f"最大值: {ssta_max:.3f} °C")
    st.write(f"25%分位数: {ssta_q25:.3f} °C")
    st.write(f"75%分位数: {ssta_q75:.3f} °C")

with col2:
    st.subheader("纬向流速 (u_current)")
    st.write(f"均值: {u_mean:.4f} m/s")
    st.write(f"中位数: {u_median:.4f} m/s")
    st.write(f"标准差: {u_std:.4f} m/s")
    st.write(f"最小值: {u_min:.4f} m/s")
    st.write(f"最大值: {u_max:.4f} m/s")
    st.write(f"绝对值均值: {u_abs_mean:.4f} m/s (流速大小)")

with col3:
    st.subheader("北向流速 (v_current)")
    st.write(f"均值: {v_mean:.4f} m/s")
    st.write(f"中位数: {v_median:.4f} m/s")
    st.write(f"标准差: {v_std:.4f} m/s")
    st.write(f"最小值: {v_min:.4f} m/s")
    st.write(f"最大值: {v_max:.4f} m/s")
    st.write(f"绝对值均值: {v_abs_mean:.4f} m/s (流速大小)")

st.markdown("---")
st.subheader("ONI 指数 (2020–2026)")
col_on1, col_on2 = st.columns(2)
col_on1.write(f"均值: {oni_mean:.3f} °C")
col_on1.write(f"中位数: {oni_median:.3f} °C")
col_on1.write(f"标准差: {oni_std:.3f} °C")
col_on2.write(f"最小值: {oni_min:.3f} °C")
col_on2.write(f"最大值: {oni_max:.3f} °C")
col_on2.write(f"2026年4月值: {oni_recent.loc['2026-04-15', 'anom']:.3f} °C")

# ================== 分布图形 ==================
st.header("2. 数据分布可视化")
st.markdown("以下图形展示了各变量的分布形态及异常检测。所有图形尺寸为 10×5 英寸。")

# 2.1 海温距平直方图
fig1, ax1 = plt.subplots(figsize=(10, 5))
ax1.hist(ssta_vals, bins=50, edgecolor='black', alpha=0.7, color='royalblue')
ax1.axvline(ssta_mean, color='red', linestyle='--', label=f'均值 = {ssta_mean:.2f}°C')
ax1.axvline(ssta_median, color='green', linestyle='--', label=f'中位数 = {ssta_median:.2f}°C')
ax1.set_xlabel("海温距平 (°C)")
ax1.set_ylabel("频数")
ax1.set_title("Nino3.4 区域 SSTA 直方图")
ax1.legend()
ax1.grid(alpha=0.3)
st.pyplot(fig1)
plt.close()
st.caption("图3-4 SSTA 直方图，红色虚线为均值，绿色虚线为中位数，分布接近正态。")

# 2.2 海温距平空间箱线图（按经度分组）
lon_bins = np.linspace(LON_MIN, LON_MAX, 6)
lon_labels = [f"{int(lon_bins[i])}-{int(lon_bins[i+1])}°E" for i in range(5)]
ssta_lon_grouped = []
for i in range(5):
    lon_slice = slice(lon_bins[i], lon_bins[i+1])
    data_sub = ssta_region.sel(lon=lon_slice).values.flatten()
    data_sub = data_sub[~np.isnan(data_sub)]
    ssta_lon_grouped.append(data_sub)
fig2, ax2 = plt.subplots(figsize=(10, 5))
bp = ax2.boxplot(ssta_lon_grouped, labels=lon_labels, patch_artist=True,
                 boxprops=dict(facecolor='lightblue'), medianprops=dict(color='red'))
ax2.set_xlabel("经度范围")
ax2.set_ylabel("海温距平 (°C)")
ax2.set_title("不同经度带上 SSTA 的箱线图")
ax2.grid(alpha=0.3, axis='y')
st.pyplot(fig2)
plt.close()
st.caption("图3-1 按经度分组的 SSTA 箱线图，东太平洋正距平更明显。")

# 2.3 洋流 u_current 直方图
fig3, ax3 = plt.subplots(figsize=(10, 5))
ax3.hist(u_vals, bins=50, edgecolor='black', alpha=0.7, color='seagreen')
ax3.axvline(u_mean, color='red', linestyle='--', label=f'均值 = {u_mean:.2f} m/s')
ax3.axvline(u_median, color='green', linestyle='--', label=f'中位数 = {u_median:.2f} m/s')
ax3.axvline(0, color='gray', linestyle='-', linewidth=0.8, label='0 m/s')
ax3.set_xlabel("纬向流速 (m/s)")
ax3.set_ylabel("频数")
ax3.set_title("纬向流速 u_current 直方图")
ax3.legend()
ax3.grid(alpha=0.3)
st.pyplot(fig3)
plt.close()
st.caption("图3-2 u_current 直方图，负值（西向流）略占优势，但正值（东向流）已出现。")

# 2.4 u_current 与 v_current 散点密度图
fig4, ax4 = plt.subplots(figsize=(10, 6))  # 高度稍大保持美观，但宽10高5比例也可，这里用10x6也行，但按你要求可改为10x5
# 为了严格10x5，调整
fig4, ax4 = plt.subplots(figsize=(10, 5))
hb = ax4.hexbin(u_vals, v_vals, gridsize=80, cmap='viridis', mincnt=1)
ax4.set_xlabel("u_current (m/s)")
ax4.set_ylabel("v_current (m/s)")
ax4.set_title("纬向流速 vs 北向流速 密度图")
ax4.axhline(0, color='gray', linestyle='--', linewidth=0.5)
ax4.axvline(0, color='gray', linestyle='--', linewidth=0.5)
cbar = plt.colorbar(hb, ax=ax4, label='网格内点数')
st.pyplot(fig4)
plt.close()
st.caption("图3-5 u_current 与 v_current 散点密度图，大部分点集中在零点附近。")

# 2.5 ONI 时间序列折线图
oni_recent = oni_recent.sort_index()
fig5, ax5 = plt.subplots(figsize=(10, 5))
ax5.plot(oni_recent.index, oni_recent['anom'], marker='o', linewidth=1.5, markersize=3, color='darkred')
ax5.axhline(0.5, color='orange', linestyle='--', label='厄尔尼诺阈值 (+0.5°C)')
ax5.axhline(-0.5, color='blue', linestyle='--', label='拉尼娜阈值 (-0.5°C)')
ax5.set_ylabel("海温距平 (°C)")
ax5.set_xlabel("时间")
ax5.set_title("ONI 指数时间序列 (2020-2026)")
ax5.legend()
ax5.grid(alpha=0.3)
st.pyplot(fig5)
plt.close()
st.caption("图3-3 ONI 指数时间序列，2026年4月达到厄尔尼诺阈值。")

# ================== 侧边栏说明 ==================
st.sidebar.markdown("## 说明")
st.sidebar.info(
    "本页面基于以下数据集：\n"
    "- ONI 指数 (1950-2026)\n"
    "- OISST 海温距平 (2026-04-01 至 2026-06-09)\n"
    "- 地转流 u/v (2026-04-01 至 2026-06-09)\n\n"
    "研究区域：170°W–120°W, 5°S–5°N (Niño3.4 区)\n\n"
    "**流速统计说明**：均值、中位数等保留了正负号，以反映净流向；同时提供了绝对值均值，表示平均流速大小（不考虑方向）。"
)
st.sidebar.markdown("---")
st.sidebar.caption("所有图形尺寸统一为 10×5 英寸。")