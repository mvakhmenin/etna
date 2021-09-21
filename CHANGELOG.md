# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added 
- MedianOutliersTransform, DensityOutliersTransform ([#30](https://github.com/tinkoff-ai/etna-ts/pull/30))
- Issues and Pull Request templates
- TSDataset checks ([#24](https://github.com/tinkoff-ai/etna-ts/pull/24), [#20](https://github.com/tinkoff-ai/etna-ts/pull/20))\
- Pytorch-Forecasting models ([#29](https://github.com/tinkoff-ai/etna-ts/pull/29))
- SARIMAX model ([#10](https://github.com/tinkoff-ai/etna-ts/pull/10))
- Logging, including ConsoleLogger ([#46](https://github.com/tinkoff-ai/etna-ts/pull/46))

### Changed
- Backtest is fully parallel 

### Fixed
- Documentation fixes ([#55](https://github.com/tinkoff-ai/etna-ts/pull/55), [#53](https://github.com/tinkoff-ai/etna-ts/pull/53), [#52](https://github.com/tinkoff-ai/etna-ts/pull/52))
- Solved warning in LogTransform and AddConstantTransform ([#26](https://github.com/tinkoff-ai/etna-ts/pull/26))
- Regressors does not have enough history bug ([#35](https://github.com/tinkoff-ai/etna-ts/pull/35))
- make_future(1) and make_future(2) bug

## [1.0.0] - 2021-09-05
### Added
- Models
  - CatBoost
  - Prophet
  - Seasonal Moving Average
  - Naive
  - Linear
- Transforms
  - Rolling statistics
  - Trend removal
  - Segment encoder
  - Datetime flags
  - Sklearn skalers (MinMax, Robust, MinMaxAbs, Standard, MaxAbs)
  - BoxCox, YeoJohnson, LogTransform
  - Lag operator
  - NaN imputer
- TimeSeriesCrossValidation
- Time Series Dataset (TSDataset)
- Playground datasets generation (AR, constant, periodic, from pattern)
- Matrics (MAE, MAPE, SMAPE, MedAE, MSE, MSLE, R^2)
- EDA mehods
  - Outliers detection
  - PACF plot
  - Cross correlation plot
  - Destribution plot
  - Anomalies (Outliers) plot
  - Backtest (CrossValidation) plot
  - Forecast plot