import numpy as np
import pandas as pd
import pytest
from pandas.util.testing import assert_frame_equal
from pytorch_forecasting.data import GroupNormalizer

from etna.datasets import TSDataset
from etna.models import AutoARIMAModel
from etna.models import BATSModel
from etna.models import CatBoostModelMultiSegment
from etna.models import CatBoostModelPerSegment
from etna.models import ElasticMultiSegmentModel
from etna.models import ElasticPerSegmentModel
from etna.models import HoltModel
from etna.models import HoltWintersModel
from etna.models import LinearMultiSegmentModel
from etna.models import LinearPerSegmentModel
from etna.models import MovingAverageModel
from etna.models import NaiveModel
from etna.models import ProphetModel
from etna.models import SARIMAXModel
from etna.models import SeasonalMovingAverageModel
from etna.models import SimpleExpSmoothingModel
from etna.models import TBATSModel
from etna.models.nn import DeepARModel
from etna.models.nn import TFTModel
from etna.transforms import LagTransform
from etna.transforms import PytorchForecastingTransform


def _test_forecast_in_sample_full(ts, model, transforms):
    df = ts.to_pandas()

    # fitting
    ts.fit_transform(transforms)
    model.fit(ts)

    # forecasting
    forecast_ts = TSDataset(df, freq="D")
    forecast_ts.transform(ts.transforms)
    forecast_ts.df.loc[:, pd.IndexSlice[:, "target"]] = np.NaN
    model.forecast(forecast_ts)

    # checking
    forecast_df = forecast_ts.to_pandas(flatten=True)
    assert not np.any(forecast_df["target"].isna())


def _test_forecast_in_sample_suffix(ts, model, transforms):
    df = ts.to_pandas()

    # fitting
    ts.fit_transform(transforms)
    model.fit(ts)

    # forecasting
    forecast_ts = TSDataset(df, freq="D")
    forecast_ts.transform(ts.transforms)
    forecast_ts.df.loc[:, pd.IndexSlice[:, "target"]] = np.NaN
    forecast_ts.df = forecast_ts.df.iloc[5:]
    model.forecast(forecast_ts)

    # checking
    forecast_df = forecast_ts.to_pandas(flatten=True)
    assert not np.any(forecast_df["target"].isna())


def _test_forecast_out_sample_prefix(ts, model, transforms):
    # fitting
    ts.fit_transform(transforms)
    model.fit(ts)

    # forecasting full
    forecast_full_ts = ts.make_future(5)
    model.forecast(forecast_full_ts)

    # forecasting only prefix
    forecast_prefix_ts = ts.make_future(5)
    forecast_prefix_ts.df = forecast_prefix_ts.df.iloc[:-2]
    model.forecast(forecast_prefix_ts)

    # checking
    forecast_full_df = forecast_full_ts.to_pandas()
    forecast_prefix_df = forecast_prefix_ts.to_pandas()
    assert_frame_equal(forecast_prefix_df, forecast_full_df.iloc[:-2])


def _test_forecast_out_sample_suffix(ts, model, transforms):
    # fitting
    ts.fit_transform(transforms)
    model.fit(ts)

    # forecasting full
    forecast_full_ts = ts.make_future(5)
    model.forecast(forecast_full_ts)

    # forecasting only suffix
    forecast_gap_ts = ts.make_future(5)
    forecast_gap_ts.df = forecast_gap_ts.df.iloc[2:]
    model.forecast(forecast_gap_ts)

    # checking
    forecast_full_df = forecast_full_ts.to_pandas()
    forecast_gap_df = forecast_gap_ts.to_pandas()
    assert_frame_equal(forecast_gap_df, forecast_full_df.iloc[2:])


@pytest.mark.parametrize(
    "model, transforms",
    [
        (CatBoostModelMultiSegment(), [LagTransform(in_column="target", lags=[2, 3])]),
        (ProphetModel(), []),
        (SARIMAXModel(), []),
        (AutoARIMAModel(), []),
        (HoltModel(), []),
        (HoltWintersModel(), []),
        (SimpleExpSmoothingModel(), []),
        (MovingAverageModel(window=3), []),
        (NaiveModel(lag=3), []),
        (SeasonalMovingAverageModel(), []),
        (BATSModel(use_trend=True), []),
        (TBATSModel(use_trend=True), []),
    ],
)
def test_forecast_in_sample_full(model, transforms, example_tsds):
    _test_forecast_in_sample_full(example_tsds, model, transforms)


@pytest.mark.xfail(strict=True)
@pytest.mark.parametrize(
    "model, transforms",
    [
        (CatBoostModelPerSegment(), [LagTransform(in_column="target", lags=[2, 3])]),
        (LinearPerSegmentModel(), [LagTransform(in_column="target", lags=[2, 3])]),
        (LinearMultiSegmentModel(), [LagTransform(in_column="target", lags=[2, 3])]),
        (ElasticPerSegmentModel(), [LagTransform(in_column="target", lags=[2, 3])]),
        (ElasticMultiSegmentModel(), [LagTransform(in_column="target", lags=[2, 3])]),
        (
            DeepARModel(max_epochs=1, learning_rate=[0.01]),
            [
                PytorchForecastingTransform(
                    max_encoder_length=1,
                    max_prediction_length=1,
                    time_varying_known_reals=["time_idx"],
                    time_varying_unknown_reals=["target"],
                    target_normalizer=GroupNormalizer(groups=["segment"]),
                )
            ],
        ),
        (
            TFTModel(max_epochs=1, learning_rate=[0.01]),
            [
                PytorchForecastingTransform(
                    max_encoder_length=21,
                    min_encoder_length=21,
                    max_prediction_length=5,
                    time_varying_known_reals=["time_idx"],
                    time_varying_unknown_reals=["target"],
                    static_categoricals=["segment"],
                    target_normalizer=None,
                )
            ],
        ),
    ],
)
def test_forecast_in_sample_full_failed(model, transforms, example_tsds):
    _test_forecast_in_sample_full(example_tsds, model, transforms)


@pytest.mark.parametrize(
    "model, transforms",
    [
        (CatBoostModelPerSegment(), [LagTransform(in_column="target", lags=[2, 3])]),
        (CatBoostModelMultiSegment(), [LagTransform(in_column="target", lags=[2, 3])]),
        (LinearPerSegmentModel(), [LagTransform(in_column="target", lags=[2, 3])]),
        (LinearMultiSegmentModel(), [LagTransform(in_column="target", lags=[2, 3])]),
        (ElasticPerSegmentModel(), [LagTransform(in_column="target", lags=[2, 3])]),
        (ElasticMultiSegmentModel(), [LagTransform(in_column="target", lags=[2, 3])]),
        (ProphetModel(), []),
        (SARIMAXModel(), []),
        (AutoARIMAModel(), []),
        (HoltModel(), []),
        (HoltWintersModel(), []),
        (SimpleExpSmoothingModel(), []),
        (MovingAverageModel(window=3), []),
        (NaiveModel(lag=3), []),
        (SeasonalMovingAverageModel(), []),
        (BATSModel(use_trend=True), []),
        (TBATSModel(use_trend=True), []),
    ],
)
def test_forecast_in_sample_suffix(model, transforms, example_tsds):
    _test_forecast_in_sample_suffix(example_tsds, model, transforms)


@pytest.mark.xfail(strict=True)
@pytest.mark.parametrize(
    "model, transforms",
    [
        (
            DeepARModel(max_epochs=1, learning_rate=[0.01]),
            [
                PytorchForecastingTransform(
                    max_encoder_length=1,
                    max_prediction_length=1,
                    time_varying_known_reals=["time_idx"],
                    time_varying_unknown_reals=["target"],
                    target_normalizer=GroupNormalizer(groups=["segment"]),
                )
            ],
        ),
        (
            TFTModel(max_epochs=1, learning_rate=[0.01]),
            [
                PytorchForecastingTransform(
                    max_encoder_length=21,
                    min_encoder_length=21,
                    max_prediction_length=5,
                    time_varying_known_reals=["time_idx"],
                    time_varying_unknown_reals=["target"],
                    static_categoricals=["segment"],
                    target_normalizer=None,
                )
            ],
        ),
    ],
)
def test_forecast_in_sample_suffix_failed(model, transforms, example_tsds):
    _test_forecast_in_sample_suffix(example_tsds, model, transforms)


@pytest.mark.parametrize(
    "model, transforms",
    [
        (CatBoostModelPerSegment(), [LagTransform(in_column="target", lags=[5, 6])]),
        (CatBoostModelMultiSegment(), [LagTransform(in_column="target", lags=[5, 6])]),
        (LinearPerSegmentModel(), [LagTransform(in_column="target", lags=[5, 6])]),
        (LinearMultiSegmentModel(), [LagTransform(in_column="target", lags=[5, 6])]),
        (ElasticPerSegmentModel(), [LagTransform(in_column="target", lags=[5, 6])]),
        (ElasticMultiSegmentModel(), [LagTransform(in_column="target", lags=[5, 6])]),
        (AutoARIMAModel(), []),
        (ProphetModel(), []),
        (SARIMAXModel(), []),
        (HoltModel(), []),
        (HoltWintersModel(), []),
        (SimpleExpSmoothingModel(), []),
        (MovingAverageModel(window=3), []),
        (SeasonalMovingAverageModel(), []),
        (NaiveModel(lag=3), []),
        (BATSModel(use_trend=True), []),
        (TBATSModel(use_trend=True), []),
    ],
)
def test_forecast_out_sample_prefix(model, transforms, example_tsds):
    _test_forecast_out_sample_prefix(example_tsds, model, transforms)


@pytest.mark.xfail(strict=True)
@pytest.mark.parametrize(
    "model, transforms",
    [
        (
            DeepARModel(max_epochs=5, learning_rate=[0.01]),
            [
                PytorchForecastingTransform(
                    max_encoder_length=5,
                    max_prediction_length=5,
                    time_varying_known_reals=["time_idx"],
                    time_varying_unknown_reals=["target"],
                    target_normalizer=GroupNormalizer(groups=["segment"]),
                )
            ],
        ),
        (
            TFTModel(max_epochs=1, learning_rate=[0.01]),
            [
                PytorchForecastingTransform(
                    max_encoder_length=21,
                    min_encoder_length=21,
                    max_prediction_length=5,
                    time_varying_known_reals=["time_idx"],
                    time_varying_unknown_reals=["target"],
                    static_categoricals=["segment"],
                    target_normalizer=None,
                )
            ],
        ),
    ],
)
def test_forecast_out_sample_prefix_failed(model, transforms, example_tsds):
    _test_forecast_out_sample_prefix(example_tsds, model, transforms)


@pytest.mark.parametrize(
    "model, transforms",
    [
        (CatBoostModelPerSegment(), [LagTransform(in_column="target", lags=[5, 6])]),
        (CatBoostModelMultiSegment(), [LagTransform(in_column="target", lags=[5, 6])]),
        (LinearPerSegmentModel(), [LagTransform(in_column="target", lags=[5, 6])]),
        (LinearMultiSegmentModel(), [LagTransform(in_column="target", lags=[5, 6])]),
        (ElasticPerSegmentModel(), [LagTransform(in_column="target", lags=[5, 6])]),
        (ElasticMultiSegmentModel(), [LagTransform(in_column="target", lags=[5, 6])]),
        (ProphetModel(), []),
        (SARIMAXModel(), []),
        (HoltModel(), []),
        (HoltWintersModel(), []),
        (SimpleExpSmoothingModel(), []),
        (
            TFTModel(max_epochs=1, learning_rate=[0.01]),
            [
                PytorchForecastingTransform(
                    max_encoder_length=21,
                    min_encoder_length=21,
                    max_prediction_length=5,
                    time_varying_known_reals=["time_idx"],
                    time_varying_unknown_reals=["target"],
                    static_categoricals=["segment"],
                    target_normalizer=None,
                )
            ],
        ),
    ],
)
def test_forecast_out_sample_suffix(model, transforms, example_tsds):
    _test_forecast_out_sample_suffix(example_tsds, model, transforms)


@pytest.mark.xfail(strict=True)
@pytest.mark.parametrize(
    "model, transforms",
    [
        (AutoARIMAModel(), []),
        (MovingAverageModel(window=3), []),
        (SeasonalMovingAverageModel(), []),
        (NaiveModel(lag=3), []),
        (BATSModel(use_trend=True), []),
        (TBATSModel(use_trend=True), []),
        (
            DeepARModel(max_epochs=5, learning_rate=[0.01]),
            [
                PytorchForecastingTransform(
                    max_encoder_length=5,
                    max_prediction_length=5,
                    time_varying_known_reals=["time_idx"],
                    time_varying_unknown_reals=["target"],
                    target_normalizer=GroupNormalizer(groups=["segment"]),
                )
            ],
        ),
    ],
)
def test_forecast_out_sample_suffix_failed(model, transforms, example_tsds):
    _test_forecast_out_sample_suffix(example_tsds, model, transforms)
