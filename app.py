import streamlit as st
import pandas as pd
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import datetime
from scipy import stats
from pathlib import Path

# ================== 全局变量配置 ==================
ONI_FILEPATH = "data/oni.ascii.txt"
SST_FILEPATH = "data/sst_2026_04_06_combined.nc"
CURRENTS_FILEPATH = "data/currents_2026_04_06_full_lon_extended.nc"
WEEKLY_SSTA_FILEPATH = "data/weekly_ssta.txt"

ONI_YEARS_START = 2020
ONI_YEARS_END = 2026

LON_MIN = 190.0
LON_MAX = 240.0
LAT_MIN = -5.0
LAT_MAX = 5.0

HOV_START_DATE = datetime(2026, 4, 1)
HOV_END_DATE = datetime(2026, 5, 31)

PROFILE_LON_SLICE = slice(int(LON_MIN), int(LON_MAX))

# ================== 设置中文字体 ==================
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans', 'Microsoft YaHei', 'WenQuanYi Micro Hei']
plt.rcParams['axes.unicode_minus'] = False

# ================== 自定义 CSS 美化 ==================
st.markdown("""
<style>
    /* 整体背景色 */
    .stApp {
        background-color: #f5f7fb;
    }
    /* 主容器圆角卡片效果 */
    .main > div {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    /* 侧边栏样式 */
    .css-1d391kg, .css-1lcbmhc {
        background-color: #eef2f7;
        border-right: 1px solid #d0d7de;
    }
    /* 标题字体颜色 */
    h1, h2, h3 {
        color: #1e466e;
    }
    /* 按钮悬停效果 */
    .stButton > button {
        background-color: #1e466e;
        color: white;
        border-radius: 20px;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #2c6288;
        color: white;
    }
    /* 滑块样式 */
    .stSlider > div > div {
        background-color: #cbd5e1;
    }
    /* 选择框美化 */
    .stSelectbox > div > div {
        background-color: #f0f2f6;
    }
    /* 信息框圆角 */
    .stAlert {
        border-radius: 10px;
    }
    footer {
        font-size: 12px;
        color: #6c757d;
        text-align: center;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ================== 页面配置 ==================
st.set_page_config(page_title="厄尔尼诺可视化分析", layout="wide", page_icon="🌊")
st.markdown("<h1 style='text-align: center; color: #1e466e;'>🌊 2026年厄尔尼诺事件：赤道太平洋海温与洋流<h1>", unsafe_allow_html=True)

# ================== 侧边栏 ==================
with st.sidebar:
    st.markdown("## 🔍 导航")
    page = st.radio(
        "选择分析页面",
        [
            "1. Niño3.4 指数时间序列",
            "2. Hovmöller 图 (海温距平)",
            "3. 洋流方向与强度热力图",
            "4. 流速剖面（经向与纬向）",
            "5. 海温与纬向流速耦合关系"
        ]
    )
    st.markdown("---")
    st.markdown("📅 **主要数据时间范围**  \n2026年4月1日 – 6月9日")
    st.markdown("📌 **研究区域**  \n170°W–120°W, 5°S–5°N")
    st.markdown("💡 **提示**  \n交互控件可实时调整图表参数")
    st.markdown("---")
    st.caption("项目：数据可视化课程设计")

# ================== 数据加载缓存 ==================
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
    return ds

# 预加载 ONI 数据
oni_df = load_oni_data(ONI_FILEPATH)
oni_5y = oni_df.loc[f"{ONI_YEARS_START}":f"{ONI_YEARS_END}"]

# ================== 页面1 ==================
if page == "1. Niño3.4 指数时间序列":
    st.header("📈 Niño3.4 指数时间序列 (ONI)")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(oni_5y.index, oni_5y['anom'], marker='o', color='#d62728', linewidth=1.5, markersize=3)
    ax.axhline(0.5, color='#ff7f0e', linestyle='--', label='厄尔尼诺阈值 (+0.5°C)')
    ax.axhline(-0.5, color='#1f77b4', linestyle='--', label='拉尼娜阈值 (-0.5°C)')
    ax.set_ylabel("海温距平 (°C)")
    ax.set_xlabel("时间")
    ax.set_title(f"Nino3.4 指数 ({ONI_YEARS_START}-{ONI_YEARS_END})")
    ax.legend()
    ax.grid(alpha=0.3)
    st.pyplot(fig)
    plt.close()
    st.info("ONI指数基于海表温度距平，持续高于+0.5°C表示厄尔尼诺事件。")

    st.subheader("📊 周平均 Niño3.4 海温距平 (2026年3月30日 - 6月6日)")
    if Path(WEEKLY_SSTA_FILEPATH).exists():
        df_weekly = pd.read_csv(WEEKLY_SSTA_FILEPATH, sep='\t')
        df_weekly['DATE'] = pd.to_datetime(df_weekly['DATE'])
        df_weekly = df_weekly.sort_values('DATE')
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        ax2.plot(df_weekly['DATE'], df_weekly['ANOM'], marker='s', color='#8c564b', linewidth=2, markersize=6)
        ax2.axhline(0.5, color='#ff7f0e', linestyle='--', label='厄尔尼诺阈值 (+0.5°C)')
        ax2.axhline(-0.5, color='#1f77b4', linestyle='--', label='拉尼娜阈值 (-0.5°C)')
        ax2.set_ylabel("海温距平 (°C)")
        ax2.set_xlabel("时间")
        ax2.set_title("周平均 Nino3.4 海温距平 (每周一代表整周)")
        ax2.legend()
        ax2.grid(alpha=0.3)
        ax2.set_xlim(df_weekly['DATE'].min(), df_weekly['DATE'].max())
        st.pyplot(fig2)
        plt.close()
        st.caption("数据源：OISST 日平均 anom，经区域平均后按周（周一至周日）聚合。")
    else:
        st.warning(f"未找到周平均数据文件：{WEEKLY_SSTA_FILEPATH}。请先运行 calc_oni.py 生成数据。")

# ================== 页面2 ==================
elif page == "2. Hovmöller 图 (海温距平)":
    st.header("🗺️ Hovmöller 图 (固定纬度 SSTA)")
    col1, col2 = st.columns(2)
    with col1:
        lat_value = st.slider("选择固定纬度 (°N)", -5.0, 5.0, 0.0, 0.25)
    with col2:
        start_date = st.date_input("起始日期", HOV_START_DATE)
        end_date = st.date_input("结束日期", HOV_END_DATE)

    with st.spinner("加载海温数据（约1GB，首次较慢）..."):
        ds_sst = load_sst_data(SST_FILEPATH)

    sst_subset = ds_sst['anom'].sel(
        time=slice(str(start_date), str(end_date)),
        lat=slice(LAT_MIN, LAT_MAX),
        lon=slice(LON_MIN, LON_MAX)
    )
    latitudes = sst_subset.lat.values
    nearest_lat = latitudes[np.argmin(np.abs(latitudes - lat_value))]
    hov_data = sst_subset.sel(lat=nearest_lat, method='nearest').sortby('time').sortby('lon')
    time_vals = hov_data.time.values
    lon_vals = hov_data.lon.values
    ssta_2d = hov_data.values

    fig, ax = plt.subplots(figsize=(7, 4))
    im = ax.pcolormesh(lon_vals, time_vals, ssta_2d, cmap='RdBu_r', vmin=-2, vmax=2, shading='auto')
    ax.set_ylabel("时间")
    ax.set_xlabel("经度")
    ax.set_title(f"赤道太平洋海温距平 (纬度固定 {nearest_lat:.2f}°N)")
    xticks = [LON_MIN, (LON_MIN+LON_MAX)/2, LON_MAX]
    ax.set_xticks(xticks)
    ax.set_xticklabels(['170°W', '150°W', '130°W'])
    plt.colorbar(im, ax=ax, label='海温距平 (°C)')
    st.pyplot(fig)
    plt.close()
    st.info(f"经度范围: 170°W-120°W | 纬度: {nearest_lat:.2f}°N。红色为暖异常，蓝色为冷异常。")

# ================== 页面3 ==================
elif page == "3. 洋流方向与强度热力图":
    st.header("🌊 洋流方向与强度热力图")
    st.markdown("颜色表示流向（参见右侧色轮），亮度表示流速大小。可切换亮度与流速的关系。")

    with st.spinner("加载洋流数据..."):
        ds_cur = load_currents_data(CURRENTS_FILEPATH)

    lon_min_data = float(ds_cur.longitude.min())
    lon_max_data = float(ds_cur.longitude.max())
    st.info(f"洋流数据经度范围: {lon_min_data:.1f}°E – {lon_max_data:.1f}°E。当前绘图聚焦于 170°W–120°W（即 {LON_MIN:.0f}°E–{LON_MAX:.0f}°E）。")

    time_list = ds_cur.time.values
    selected_date = st.selectbox(
        "选择日期",
        options=time_list,
        format_func=lambda x: pd.to_datetime(x).strftime('%Y-%m-%d'),
        index=0
    )

    brightness_mode = st.radio(
        "亮度与流速关系",
        options=["越亮越快", "越亮越慢"],
        index=0,
        horizontal=True
    )

    u_full = ds_cur.u_current.sel(time=selected_date, method='nearest')
    v_full = ds_cur.v_current.sel(time=selected_date, method='nearest')
    lon_full = u_full.longitude.values
    lat_full = u_full.latitude.values

    mask = (lon_full >= LON_MIN) & (lon_full <= LON_MAX)
    u = u_full.values[:, mask]
    v = v_full.values[:, mask]
    lon = lon_full[mask]
    lat = lat_full

    angle = np.arctan2(v, u)
    hue = (np.rad2deg(angle) + 360) % 360
    speed = np.sqrt(u**2 + v**2)
    vmax_speed = speed.max() if speed.max() > 0 else 0.5

    if brightness_mode == "越亮越快":
        value = np.clip(speed / vmax_speed, 0, 1)
        cbar_label = "流速 (m/s)  →  越亮越快"
    else:
        value = 1 - np.clip(speed / vmax_speed, 0, 1)
        cbar_label = "流速 (m/s)  →  越亮越慢"

    saturation = np.ones_like(speed)
    hsv = np.stack([hue/360, saturation, value], axis=-1)
    rgb = mcolors.hsv_to_rgb(hsv)

    col_left, col_right = st.columns([3, 1])
    with col_left:
        fig1, ax = plt.subplots(figsize=(8, 4))
        ax.imshow(rgb, origin='lower', extent=[lon.min(), lon.max(), lat.min(), lat.max()], aspect='auto')
        ax.set_xlabel("经度")
        ax.set_ylabel("纬度")
        ax.set_title(f"洋流方向与强度 ({pd.to_datetime(selected_date).strftime('%Y-%m-%d')})\n{LON_MIN:.0f}°E – {LON_MAX:.0f}°E (170°W–120°W)")
        ax.set_xlim(LON_MIN, LON_MAX)
        ax.set_ylim(LAT_MIN, LAT_MAX)
        sm = plt.cm.ScalarMappable(cmap='gray', norm=plt.Normalize(0, vmax_speed))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, label=cbar_label)
        if brightness_mode == "越亮越快":
            cbar.ax.set_yticklabels([f'{0:.2f}', f'{vmax_speed:.2f}'])
        else:
            cbar.ax.set_yticklabels([f'{vmax_speed:.2f}', f'{0:.2f}'])
        st.pyplot(fig1)
        plt.close()

    with col_right:
        fig2, ax_c = plt.subplots(figsize=(1, 1), subplot_kw={'projection': 'polar'})
        ax_c.set_theta_zero_location('E')
        ax_c.set_xticks([0, np.pi/2, np.pi, 3*np.pi/2])
        ax_c.set_xticklabels(['东', '北', '西', '南'], fontsize=8)
        ax_c.set_yticks([])
        ax_c.set_ylim(0, 1)
        n = 360
        theta = np.linspace(0, 2*np.pi, n)
        radii = np.ones(n)
        width = 2*np.pi / n
        colors = mcolors.hsv_to_rgb(np.stack([theta/(2*np.pi), np.ones(n), np.ones(n)], axis=1))
        ax_c.bar(theta, radii, width=width, bottom=0, color=colors, edgecolor='none')
        ax_c.set_title("流向色轮", fontsize=10)
        st.pyplot(fig2)
        plt.close()

# ================== 页面4 ==================
elif page == "4. 流速剖面（经向与纬向）":
    st.header("📐 纬向流速剖面分析")
    st.markdown("包括经向剖面（固定纬度）和纬向剖面（固定经度范围），用于研究流轴位置和东向流强度。")

    with st.spinner("加载洋流数据..."):
        ds_cur = load_currents_data(CURRENTS_FILEPATH)

    time_list = ds_cur.time.values
    selected_dates = st.multiselect(
        "选择对比日期（最多5个）",
        options=time_list,
        format_func=lambda x: pd.to_datetime(x).strftime('%Y-%m-%d'),
        default=[time_list[0], time_list[-1]] if len(time_list) > 1 else [time_list[0]]
    )
    if len(selected_dates) > 5:
        st.warning("最多选择5个日期，已自动限制")
        selected_dates = selected_dates[:5]

    st.subheader("经向剖面：纬向流速随经度的变化")
    selected_lat = st.slider(
        "选择纬度 (°N)", min_value=LAT_MIN, max_value=LAT_MAX, value=0.0, step=0.1,
        help="负值表示南纬，正值表示北纬。"
    )
    u_profile_lat = ds_cur.u_current.sel(latitude=selected_lat, method='nearest')

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    for date in selected_dates:
        u_profile = u_profile_lat.sel(time=date, method='nearest')
        ax1.plot(u_profile.longitude, u_profile.values,
                 label=pd.to_datetime(date).strftime('%Y-%m-%d'), alpha=0.7)
    ax1.axhline(y=0, color='k', linestyle='--', linewidth=1, label='0 m/s')
    ax1.set_xlabel("经度 (°E)")
    ax1.set_ylabel("纬向流速 (m/s)")
    ax1.set_title(f"纬向流速经向剖面 (纬度 = {selected_lat:.1f}°N)")
    ax1.legend()
    ax1.grid(alpha=0.3)
    ax1.set_xlim(LON_MIN, LON_MAX)
    st.pyplot(fig1)
    plt.close()

    st.subheader("纬向剖面：纬向流速随纬度的变化（寻找流轴）")
    lon_mode = st.radio("经度范围模式", ["平均 (170°W-120°W)", "单点经度"], horizontal=True)
    if lon_mode == "平均 (170°W-120°W)":
        u_for_lat = ds_cur.u_current.sel(longitude=PROFILE_LON_SLICE).mean(dim='longitude')
        title_suffix = "经度平均 (170°W-120°W)"
    else:
        lon_single = st.slider("选择单个经度 (°E)", LON_MIN, LON_MAX, (LON_MIN+LON_MAX)/2, 1.0)
        u_for_lat = ds_cur.u_current.sel(longitude=lon_single, method='nearest')
        title_suffix = f"经度 {lon_single:.1f}°E"

    fig2, ax2 = plt.subplots(figsize=(8, 4))
    for date in selected_dates:
        u_lat_profile = u_for_lat.sel(time=date, method='nearest')
        ax2.plot(u_lat_profile.latitude, u_lat_profile.values,
                 label=pd.to_datetime(date).strftime('%Y-%m-%d'), alpha=0.7)
    ax2.axhline(y=0, color='k', linestyle='--', linewidth=1, label='0 m/s')
    ax2.set_xlabel("纬度 (°N)")
    ax2.set_ylabel("纬向流速 (m/s)")
    ax2.set_title(f"纬向流速纬向剖面 ({title_suffix})")
    ax2.legend()
    ax2.grid(alpha=0.3)
    ax2.set_xlim(LAT_MIN, LAT_MAX)
    st.pyplot(fig2)
    plt.close()
    st.info("正值为东向流。在图2中，流速峰值对应的纬度即为强流轴位置，可用于检测流轴是否发生南北偏移。")

# ================== 页面5 ==================
elif page == "5. 海温与纬向流速耦合关系":
    st.header("🔗 海温与纬向流速耦合关系 (Niño3.4区域)")
    st.markdown("验证赤道中东太平洋（170°W-120°W）海温升高是否伴随东向流增强。")

    with st.spinner("加载数据..."):
        ds_sst = load_sst_data(SST_FILEPATH)
        ds_cur = load_currents_data(CURRENTS_FILEPATH)

    ds_sst['time'] = ds_sst['time'].dt.floor('D')
    ds_cur['time'] = ds_cur['time'].dt.floor('D')

    region_mode = st.radio(
        "选择纬度范围模式",
        ["平均纬度 (5°S-5°N)", "单点纬度 (滑块选择)"],
        horizontal=True
    )

    lon_range = slice(LON_MIN, LON_MAX)

    if region_mode == "平均纬度 (5°S-5°N)":
        lat_range = slice(LAT_MIN, LAT_MAX)
        ssta_region = ds_sst['anom'].sel(lon=lon_range, lat=lat_range).mean(dim=['lon', 'lat'])
        u_region = ds_cur['u_current'].sel(longitude=lon_range, latitude=lat_range).mean(dim=['longitude', 'latitude'])
        df_sst = ssta_region.to_dataframe(name='ssta').reset_index()
        df_u = u_region.to_dataframe(name='u').reset_index()
        df_merged = pd.merge(df_sst, df_u, on='time', how='inner').dropna(subset=['ssta', 'u'])
        title_suffix = "区域平均 (5°S-5°N)"
    else:
        selected_lat = st.slider(
            "选择纬度 (°N)", min_value=LAT_MIN, max_value=LAT_MAX, value=0.0, step=0.1,
            help="负值表示南纬，正值表示北纬。"
        )
        ssta_temp = ds_sst['anom'].sel(lat=selected_lat, method='nearest')
        ssta_lat = ssta_temp.sel(lon=lon_range).mean(dim='lon')
        u_temp = ds_cur['u_current'].sel(latitude=selected_lat, method='nearest')
        u_lat = u_temp.sel(longitude=lon_range).mean(dim='longitude')
        df_sst = ssta_lat.to_dataframe(name='ssta').reset_index()
        df_u = u_lat.to_dataframe(name='u').reset_index()
        df_merged = pd.merge(df_sst, df_u, on='time', how='inner').dropna(subset=['ssta', 'u'])
        title_suffix = f"单点纬度 {selected_lat:.1f}°N"

    if df_merged.empty:
        st.error("数据合并为空，请检查时间对齐。")
    else:
        df_merged['day_offset'] = (df_merged['time'] - df_merged['time'].min()).dt.days
        if df_merged['ssta'].std() == 0 or df_merged['u'].std() == 0:
            st.warning("数据变化不足，无法计算相关系数。")
            fig, ax = plt.subplots(figsize=(8, 4))
            sc = ax.scatter(df_merged['ssta'], df_merged['u'],
                            c=df_merged['day_offset'], cmap='viridis', alpha=0.7)
            ax.set_xlabel("海温距平 SSTA (°C)")
            ax.set_ylabel("纬向流速 (m/s)")
            ax.set_title(f"Nino3.4区域 SSTA vs 纬向流速 ({title_suffix})")
            plt.colorbar(sc, ax=ax, label='天数偏移')
            st.pyplot(fig)
        else:
            slope, intercept, r_value, p_value, _ = stats.linregress(df_merged['ssta'], df_merged['u'])
            x_fit = np.array([df_merged['ssta'].min(), df_merged['ssta'].max()])
            y_fit = slope * x_fit + intercept

            fig, ax = plt.subplots(figsize=(8, 4))
            sc = ax.scatter(df_merged['ssta'], df_merged['u'],
                            c=df_merged['day_offset'], cmap='viridis', alpha=0.7)
            ax.plot(x_fit, y_fit, color='red', linestyle='--',
                    label=f'回归: u = {slope:.2f}·SSTA + {intercept:.2f}  (r={r_value:.2f})')
            ax.set_xlabel("海温距平 SSTA (°C)")
            ax.set_ylabel("纬向流速 (m/s)")
            ax.set_title(f"Nino3.4区域 SSTA vs 纬向流速 ({title_suffix})")
            ax.legend()
            ax.grid(alpha=0.3)
            plt.colorbar(sc, ax=ax, label='天数偏移 (起始日=0)')
            st.pyplot(fig)
            plt.close()
            st.info(f"回归方程：u = {slope:.3f} * SSTA + {intercept:.3f}；相关系数 r = {r_value:.3f}，p = {p_value:.4f}。")
        st.caption("颜色代表时间先后，从深紫到亮黄表示从4月初到6月。注意：线性回归可能掩盖时间阶段的非线性特征，建议结合剖面图分析流轴偏移的影响。")

# ================== 页脚 ==================
st.markdown("---")
st.markdown(
    "<footer style='text-align: center; color: #6c757d;'>"
    "数据来源：NOAA OISST v2.1, NOAA ERDDAP (miamicurrents), NOAA CPC ONI<br>"
    "可视化工具：Streamlit, Matplotlib, Xarray | 项目完成于2026年6月"
    "</footer>",
    unsafe_allow_html=True
)