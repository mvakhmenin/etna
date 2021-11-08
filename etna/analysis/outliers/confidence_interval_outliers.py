from copy import deepcopy
from typing import TYPE_CHECKING
from typing import Dict
from typing import List
from typing import Type
from typing import Union

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from etna.datasets import TSDataset
    from etna.models import ProphetModel
    from etna.models import SARIMAXModel


def create_ts_by_column(ts: "TSDataset", column: str) -> "TSDataset":
    """Create TSDataset based on original ts with selecting only column in each segment and setting it to target.

    Parameters
    ----------
    ts:
        dataset with timeseries data
    column:
        column to select in each.

    Returns
    -------
    result: TSDataset
        dataset with selected column.
    """
    from etna.datasets import TSDataset

    new_df = ts[:, :, [column]]
    new_columns_tuples = [(x[0], "target") for x in new_df.columns.tolist()]
    new_df.columns = pd.MultiIndex.from_tuples(new_columns_tuples, names=new_df.columns.names)
    return TSDataset(new_df, freq=ts.freq)


def get_anomalies_confidence_interval(
    ts: "TSDataset",
    model: Union[Type["ProphetModel"], Type["SARIMAXModel"]],
    interval_width: float = 0.95,
    in_column: str = "target",
    **model_params,
) -> Dict[str, List[pd.Timestamp]]:
    """
    Get point outliers in time series using confidence intervals (estimation model-based method).
    Outliers are all points out of the confidence interval predicted with the model.

    Parameters
    ----------
    ts:
        dataset with timeseries data(should contains all the necessary features).
    model:
        model for confidence interval estimation.
    interval_width:
        the significance level for the confidence interval. By default a 95% confidence interval is taken.
    in_column:
        column to analyzes
        If it is set to "target", then all data will be used for prediction.
        Otherwise, only column data will be used.

    Returns
    -------
    dict of outliers: Dict[str, List[pd.Timestamp]]
        dict of outliers in format {segment: [outliers_timestamps]}.

    Notes
    -----
    For not "target" column only column data will be used for learning.
    """
    if in_column == "target":
        ts_inner = ts
    else:
        ts_inner = create_ts_by_column(ts, in_column)
    outliers_per_segment = {}
    time_points = np.array(ts.index.values)
    model_instance = model(**model_params)
    model_instance.fit(ts_inner)
    confidence_interval = model_instance.forecast(
        deepcopy(ts_inner), confidence_interval=True, interval_width=interval_width
    )
    for segment in ts_inner.segments:
        segment_slice = confidence_interval[:, segment, :][segment]
        anomalies_mask = (segment_slice["target"] > segment_slice["target_upper"]) | (
            segment_slice["target"] < segment_slice["target_lower"]
        )
        outliers_per_segment[segment] = list(time_points[anomalies_mask])
    return outliers_per_segment