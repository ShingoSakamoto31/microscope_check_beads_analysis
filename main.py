import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from pathlib import Path
from analysisrun.interactive import scan_model_input, FilePath
from pydantic import BaseModel, Field
from matplotlib import rcParams
from beads_output import result


class Input(BaseModel):
    input_csv: FilePath = Field(
        description="画像解析結果CSVファイル（ファイルのあるフォルダーに解析結果が出力されます）",
    )


def beads_analysis(df: pd.DataFrame, disc: str):
    if len(df) == 0:  # データがない場合の処理
        return result(
            data_name="data",
            count=None,
            count_cv_field=None,
            intensity=None,
            intensity_cv_all=None,
            intensity_cv_field=None,
        )

    # QC画像データ出力
    x = df.MultiPointIndex.unique()
    qc_fig = plt.figure(figsize=(10, 5))
    rcParams["font.family"] = "Arial"
    rcParams["axes.linewidth"] = 2.0

    # 視野ごとのビーズの数
    qc_fig_signal_count = qc_fig.add_subplot(1, 2, 1)
    y_count = np.empty(0)
    for k in x:
        df_f = df[df.MultiPointIndex == k]
        count_f = df_f.Activity_Spot_Number.unique()[0]
        y_count = np.append(y_count, count_f)
    count = round(float(np.average(y_count)), 0)
    count_cv_field = (
        np.std(y_count) / np.average(y_count) if np.average(y_count) > 0 else 0
    )
    count_cv_field = round(float(count_cv_field) * 100, 1)

    qc_fig_signal_count.bar(x, y_count, color="blue")
    qc_fig_signal_count.set_xlabel("Slice", fontsize=12)
    qc_fig_signal_count.set_ylabel("number of beads", fontsize=12)
    qc_fig_signal_count.set_ylim(0, 1300)
    qc_fig_signal_count.tick_params(labelsize=12)
    qc_fig_signal_count.set_title(
        f"Count = {count}, CV = {count_cv_field}%", fontsize=12
    )

    # 視野ごとのビーズの平均輝度
    qc_fig_signal_intensity = qc_fig.add_subplot(1, 2, 2)
    y_intensity = np.empty(0)
    for k in x:
        df_f = df[df.MultiPointIndex == k]
        intensity_f = np.average(df_f.FITC_Sum)
        y_intensity = np.append(y_intensity, intensity_f)
    intensity = round(float(np.average(df.FITC_Sum)), 0)
    intensity_cv_field = (
        np.std(y_intensity) / np.average(y_intensity)
        if np.average(y_intensity) > 0
        else 0
    )
    intensity_cv_field = round(float(intensity_cv_field) * 100, 1)
    intensity_cv_all = (
        np.std(df.FITC_Sum) / np.average(df.FITC_Sum)
        if np.average(df.FITC_Sum) > 0
        else 0
    )
    intensity_cv_all = round(float(intensity_cv_all) * 100, 1)

    qc_fig_signal_intensity.bar(x, y_intensity, color="blue")
    qc_fig_signal_intensity.set_xlabel("Slice", fontsize=12)
    qc_fig_signal_intensity.set_ylabel("FI of beads", fontsize=12)
    qc_fig_signal_intensity.set_ylim(0, 1600000)
    qc_fig_signal_intensity.tick_params(labelsize=12)
    qc_fig_signal_intensity.set_title(
        f"FI = {intensity}, CV = {intensity_cv_field}", fontsize=12
    )

    qc_fig.tight_layout()
    qc_fig.savefig(f"{disc}_QC.png", bbox_inches="tight")

    return result(
        data_name=disc,
        count=count,
        count_cv_field=count_cv_field,
        intensity=intensity,
        intensity_cv_all=intensity_cv_all,
        intensity_cv_field=intensity_cv_field,
    )


def main():
    _in = scan_model_input(Input)
    input_csv_path = Path(_in.input_csv)
    disc = input_csv_path.stem
    df = pd.read_csv(input_csv_path)
    os.chdir(
        input_csv_path.parent
    )  # 解析対象となる画像解析結果データが存在するディレクトリを作業ディレクトリとする。

    # 解析を実行する関数
    result = beads_analysis(df, disc)
    result.to_csv(f"{disc}_result.csv")


if __name__ == "__main__":
    main()
