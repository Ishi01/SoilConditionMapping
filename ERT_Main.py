import os
from matplotlib import pyplot as plt
import numpy as np

import pygimli as pg
import pygimli.meshtools as mt
from pygimli.physics import ert

# Define paths to the processed data directories
processed_data_dir1 = os.path.join(os.path.dirname(__file__), 'outputs/corrected_resistivity_detailed')
processed_data_dir2 = os.path.join(os.path.dirname(__file__), 'outputs/corrected_resistivity_simplified')


def inversion(
        processed_data_dir,  # 处理后数据所在目录
        start=[0, 0],
        end=[47, -8],
        quality=33.5,
        area=0.5,
        work_dir=None,
        inversion_params=None  # 用于配置反演参数的字典
):
    """
    ERT 反演和可视化过程
    """
    if work_dir is None:
        work_dir = os.getcwd()

    os.makedirs(work_dir, exist_ok=True)

    # Set the current working directory
    os.chdir(processed_data_dir)

    # 查找所有处理后的 .txt 文件
    entries_sel = [file for file in os.listdir() if file.endswith(".txt")]

    # 创建几何和网格
    geom = mt.createWorld(start=start, end=end, worldMarker=False)
    pg.show(geom, boundaryMarker=True)
    mesh = mt.createMesh(geom, quality=quality, area=area, smooth=True)
    mesh.save("mesh.bms")

    Storage = np.zeros([np.shape(mesh.cellMarkers())[0], np.shape(entries_sel)[0]])

    # 确保 inversion_params 不是 None
    if inversion_params is None:
        inversion_params = {}  # 使用空字典代替

    # 开始反演
    for i, date in enumerate(entries_sel):
        # 设置工作目录
        current_work_dir = os.path.join(work_dir, date)
        os.makedirs(current_work_dir, exist_ok=True)
        os.chdir(current_work_dir)

        # 使用完整路径加载处理后的 .txt 文件
        file_path = os.path.join(processed_data_dir, date)
        mgr = ert.ERTManager(file_path, verbose=True, debug=True)

        # 移除负阻抗值
        mgr.data.remove(mgr.data["rhoa"] < 0)

        # 添加误差估计
        mgr.data["err"] = ert.estimateError(
            mgr.data, absoluteError=0.001, relativeError=0.03
        )
        mgr.data["k"] = ert.createGeometricFactors(mgr.data, numerical=True)
        ert.show(mgr.data)

        # 使用提供的参数进行反演
        inv = mgr.invert(
            mgr.data,
            **inversion_params  # 使用UI提供的参数
        )

        # 保存并显示结果
        fig1, ax1 = plt.subplots(1, figsize=(16.0, 5))
        mgr.showResult(ax=ax1, cMin=50, cMax=1000)
        labels = date
        ax1.set_xlim(-0, mgr.paraDomain.xmax())
        ax1.set_ylim(-10, mgr.paraDomain.ymax())
        ax1.set_title(labels)
        plt.tight_layout()

    plt.show()
    return fig1


# 主函数
if __name__ == "__main__":
    # 使用简化数据目录调用反演函数，传入空字典作为 inversion_params
    inversion(processed_data_dir2, inversion_params={})
