import xarray as xr
import pandas as pd
import numpy as np
from pathlib import Path

# ================== 配置 ==================
SST_FILEPATH = "data/sst_2026_04_06_combined.nc"
OUTPUT_DIR = Path("data")
OUTPUT_FILE = OUTPUT_DIR / "weekly_ssta.txt"

# Niño3.4 区域
LON_MIN, LON_MAX = 190.0, 240.0   # 170°W-120°W
LAT_MIN, LAT_MAX = -5.0, 5.0

# 时间范围：从 2026-03-30（周一）到 2026-06-06（周日）
START_DATE = "2026-03-30"
END_DATE = "2026-06-06"

# ================== 加载数据 ==================
print("加载海温数据...")
ds = xr.open_dataset(SST_FILEPATH)
ds = ds.squeeze()   # 去掉 zlev 单维度
print("数据加载完成，形状:", ds.anom.shape)

# 选择区域
ssta_region = ds['anom'].sel(
    lon=slice(LON_MIN, LON_MAX),
    lat=slice(LAT_MIN, LAT_MAX)
)
sst_region = ds['sst'].sel(
    lon=slice(LON_MIN, LON_MAX),
    lat=slice(LAT_MIN, LAT_MAX)
)

# ================== 生成日期序列并分组 ==================
date_range = pd.date_range(START_DATE, END_DATE, freq='D')
weeks = []
current_week = []
for i, date in enumerate(date_range):
    current_week.append(date)
    if date.weekday() == 6 or date == date_range[-1]:
        weeks.append(current_week)
        current_week = []

# ================== 计算每周平均 SSTA 和 SST ==================
results = []
for i, week_dates in enumerate(weeks, start=1):
    start = week_dates[0]
    end = week_dates[-1]
    # 代表日期：周一（起始日）
    rep_date = start
    # 提取该周内的所有日数据
    ssta_week = ssta_region.sel(time=slice(start, end))
    sst_week = sst_region.sel(time=slice(start, end))
    # 空间平均 -> 时间序列
    ssta_ts = ssta_week.mean(dim=['lon', 'lat'])
    sst_ts = sst_week.mean(dim=['lon', 'lat'])
    # 时间平均
    weekly_ssta = float(ssta_ts.mean().values)
    weekly_sst = float(sst_ts.mean().values)
    results.append({
        'week': f"W{i:02d}",
        'date': rep_date.strftime('%Y-%m-%d'),
        'anom': weekly_ssta,
        'total': weekly_sst
    })
    print(f"{results[-1]['week']}: {rep_date.date()}  ANOM = {weekly_ssta:.2f}°C, SST = {weekly_sst:.2f}°C")

# ================== 保存为 TXT（类似官方格式） ==================
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    # 写表头（四列：WEEK, DATE, ANOM, TOTAL）
    f.write("WEEK\tDATE\tANOM\tTOTAL\n")
    for res in results:
        f.write(f"{res['week']}\t{res['date']}\t{res['anom']:.2f}\t{res['total']:.2f}\n")

print(f"\n周平均 SSTA 已保存至: {OUTPUT_FILE}")