import pandas as pd


def result(
    data_name: str,
    count: float | None,
    count_cv_field: float | None,
    intensity: float | None,
    intensity_cv_all: float | None,
    intensity_cv_field: float | None,
) -> pd.Series:
    return pd.Series(
        {
            "data_name": data_name,
            "count": count,
            "count_cv_field (%)": count_cv_field,
            "intensity": intensity,
            "intensity_cv_all (%)": intensity_cv_all,
            "intensity_cv_field (%)": intensity_cv_field,
        }
    )
