# CHANGELOG

All notable changes to this project will be documented in this file.

## [0.2.0] - 2024-12-03

### Added

- Column-wise and list-wise removal of missing values, flagging for missing data indication, and multiple imputation methods, including KNN, MICE, and regression-based handlers, have been integrated into the imputation process.

### Changed

- In the API, the internals of the impute_nulls function have been updated. A Router function is now implemented to determine and delegate to the appropriate imputation class.

- The AHandler class serves as the abstract base class for all imputer classes.

### Deprecated

- The feature argument in the impute_nulls function has been deprecated and replaced with the column argument.

## [0.1.0] - 2024-08-28

### Added

- Simple imputation module has been added to the package.
