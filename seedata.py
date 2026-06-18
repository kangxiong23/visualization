import xarray as xr

# 直接用 xr.open_dataset 打开 .nc 文件（绝对路径）
file_path = r"data/raw/sst_2026_04_06_combined.nc"
ds = xr.open_dataset(file_path)

print(ds)