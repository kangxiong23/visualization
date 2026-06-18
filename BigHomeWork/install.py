import xarray as xr
import numpy as np
import pandas as pd
import time

# ===== 参数配置 =====
url = 'https://coastwatch.pfeg.noaa.gov/erddap/griddap/miamicurrents'
time_start = '2026-04-01'
time_end = '2026-06-30'
lat_range = slice(-5, 5)          # 赤道带
# 目标经度范围：120°E 到 70°W，在 -180~180 系统中是 120 到 -70（不连续），
# 因此我们先用经度范围 120 到 290（0-360 系统），下载后再处理。
# 但注意 miamicurrents 数据的经度是 -180~180 系统，所以先不限制经度，下载后在内存中转换并裁剪。
lon_target_360 = slice(120, 290)  # 120°E 到 70°W

# 分块下载参数
chunk_days = 5
wait_seconds = 3

# 生成日期块
date_range = pd.date_range(time_start, time_end, freq='D')
chunks = [date_range[i:i+chunk_days] for i in range(0, len(date_range), chunk_days)]

all_ds = []
for i, chunk in enumerate(chunks):
    start_date = chunk[0]
    end_date = chunk[-1]
    print(f"正在下载第 {i+1}/{len(chunks)} 块：{start_date.date()} 至 {end_date.date()}")
    try:
        # 打开数据集，只选择时间和纬度（经度暂不限制）
        ds = xr.open_dataset(url).sel(
            time=slice(start_date, end_date),
            latitude=lat_range
        )
        # 加载到内存
        ds = ds.load()
        # 经度转换：-180~180 -> 0~360
        lon_360 = np.where(ds.longitude < 0, ds.longitude + 360, ds.longitude)
        ds = ds.assign_coords(longitude=('longitude', lon_360)).sortby('longitude')
        # 裁剪经度范围 120°E 到 70°W (120~290)
        ds = ds.sel(longitude=lon_target_360)
        all_ds.append(ds)
        print(f"  成功，数据形状：{ds.u_current.shape}")
    except Exception as e:
        print(f"  出错：{e}")
        continue
    time.sleep(wait_seconds)

if all_ds:
    combined = xr.concat(all_ds, dim='time')
    print(f"合并完成，总形状：{combined.u_current.shape}")
    output_file = 'currents_2026_04_06_full_lon_extended.nc'
    combined.to_netcdf(output_file, engine='scipy')
    print(f"已保存至 {output_file}")
else:
    print("未下载到任何数据")