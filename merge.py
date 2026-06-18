import xarray as xr
from pathlib import Path

# 设置路径
data_dir = Path("data/SST")
output_file = Path("data/sst_2026_04_06_combined.nc")

# 查找所有 SST NetCDF 文件（递归搜索子目录）
sst_files = sorted(data_dir.glob("**/oisst*.nc"))
print(f"找到 {len(sst_files)} 个 SST 文件")

# 打开所有文件并合并（只保留需要的变量，如 'anom' 和 'sst'，以节省内存）
ds = xr.open_mfdataset(
    sst_files,
    combine='nested',
    concat_dim='time',
    parallel=True,          # 并行读取（多线程）
    data_vars='minimal',    # 只保留所有文件都有的变量
    coords='minimal',
    compat='override'
)

print("合并完成，形状:", ds.anom.shape)

# 可选：挤压掉长度为1的维度（zlev）
ds = ds.squeeze()

# 保存为单一 NetCDF 文件（使用 netCDF4 引擎，压缩可减少体积）
ds.to_netcdf(output_file, engine='netcdf4', mode='w')
print(f"已保存合并后的文件: {output_file}")