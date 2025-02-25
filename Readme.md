# NullSweep

NullSweep is a Python library designed for detecting and handling patterns of missing data in pandas DataFrames. This tool provides a simple API to identify global missing data patterns across the entire dataset, patterns related to specific features within the dataset, and to impute missing values using various strategies.

It supports **pandas** and **polars** DataFrames.

## Features

- Detect global patterns of missing data in a DataFrame.
- Detect missing data patterns in specific features/columns of a DataFrame.
- Impute missing data in specific features or across the entire DataFrame using a variety of strategies.
- Utilizes a modular approach with different pattern detection and imputation strategies.
- Visualize missing data patterns for better understanding and analysis.

## Installation

Install NullSweep using pip:

```bash
pip install nullsweep
```

## Usage

### Detect Global Patterns

To detect global missing data patterns in a pandas DataFrame:

```python
import pandas as pd
from nullsweep import detect_global_pattern

# Sample DataFrame
data = {'A': [1, 2, None], 'B': [None, 2, 3]}
df = pd.DataFrame(data)

# Detect global missing data pattern
pattern, details = detect_global_pattern(df)
print("Detected Pattern:", pattern)
print("Details:", details)
```

### Detect Feature-Specific Patterns

To detect missing data patterns in a specific feature of a pandas DataFrame:

```python
import pandas as pd
from nullsweep import detect_feature_pattern

# Sample DataFrame
data = {'A': [1, None, 3], 'B': [4, 5, 6]}
df = pd.DataFrame(data)

# Detect feature-specific missing data pattern
feature_name = 'A'
pattern, details = detect_feature_pattern(df, feature_name)
print("Detected Pattern:", pattern)
print("Details:", details)
```

### Impute Missing Values

To handle missing values in a pandas DataFrame, the `impute_nulls` function offers a unified interface for various imputation strategies. Below is a comprehensive list of supported strategies, grouped by their functionality, and details about the parameters this function accepts.

#### **Imputation Strategies**

- **Deletion-Based Strategies**:

  - **`delete_column`**: Removes columns that meet certain criteria for missing values (e.g., columns with any or a threshold of missing values).
  - **`listwise`**: Deletes rows with missing values based on specified thresholds.

- **Flagging Strategy**:

  - **`flag`**: Creates binary indicator columns to flag the presence of missing values.

- **Nearest Neighbors Strategies**:

  - **`knn`**: Uses K-Nearest Neighbors imputation to estimate missing values based on similarity to other data points.

- **Multivariate Strategies**:

  - **`mice`**: Performs multiple imputation using chained equations (MICE) to estimate missing values.
  - **`regression`**: Uses regression-based imputation where missing values are predicted using regression models fitted on non-missing data.

- **Continuous Features**:

  - **`mean`**: Replaces missing values with the mean of the column.
  - **`median`**: Replaces missing values with the median of the column.
  - **`most_frequent`**: Replaces missing values with the most frequent value in the column.
  - **`constant`**: Replaces missing values with a user-provided constant value.
  - **`interpolate`**: Uses interpolation (linear or polynomial) to estimate missing values.
  - **`forwardfill`**: Fills missing values with the last non-missing value in a forward direction.
  - **`backfill`**: Fills missing values with the next non-missing value in a backward direction.

- **Categorical Features**:

  - **`most_frequent`**: Replaces missing values with the most frequent value.
  - **`least_frequent`**: Replaces missing values with the least frequent value.
  - **`constant`**: Replaces missing values with a user-provided constant value.
  - **`forwardfill`**: Fills missing values with the last non-missing value in a forward direction.
  - **`backfill`**: Fills missing values with the next non-missing value in a backward direction.

- **Date Features**:

  - **`interpolate`**: Uses time-based interpolation to estimate missing values.
  - **`forwardfill`**: Fills missing values with the last non-missing value in a forward direction.
  - **`backfill`**: Fills missing values with the next non-missing value in a backward direction.

- **Automatic Strategy Detection**:
  - **`auto`**: Automatically determines the best strategy for each column based on its data type and characteristics.

---

#### **Parameters**

- **`df`** _(pd.DataFrame)_:  
  The input pandas DataFrame containing the data to process. Must not be empty.

- **`column`** _(Optional[Union[Iterable, str]])_:  
  The target column(s) for imputation. Can be a single column name (str), a list of column names (Iterable), or `None`. If `None`, all columns with missing values will be considered for imputation.

- **`strategy`** _(str)_:  
  The imputation strategy to use. Refer to the above list for supported strategies. Defaults to `"auto"`.

- **`fill_value`** _(Optional[Any])_:  
  A constant value to use for imputation when the strategy is `"constant"`.

- **`strategy_params`** _(Optional[Dict[str, Any]])_:  
  Additional parameters to configure the imputation strategy. Examples include:

  - For `interpolate`: `{"method": "linear", "order": 2}` to specify a polynomial interpolation.
  - For `constant`: `{"fill_value": 0}` for numeric columns or `"missing"` for categorical columns.

- **`in_place`** _(bool)_:  
  Whether to modify the input DataFrame in place. If `True`, the DataFrame is updated directly. If `False`, a copy of the DataFrame is returned. Defaults to `True`.

- **`**kwargs`\*\* _(Any)_:  
  Additional arguments for handler-specific configurations or compatibility.

```python
import pandas as pd
import nullsweep as ns

# Sample DataFrame
data = {
    'Age': [25, 30, None, 35, 40],
    'Gender': ['Male', 'Female', None, 'Female', 'Male']
}
df = pd.DataFrame(data)

# Impute missing values in 'Age' using mean
df = ns.impute_nulls(df, column='Age', strategy='mean')

# Impute missing values in 'Gender' using the most frequent value
df = ns.impute_nulls(df, column='Gender', strategy='most_frequent')

# Impute missing values in 'Age' using linear interpolation
df = ns.impute_nulls(df, column='Age', strategy='interpolate')

# Impute missing values for multiple columns
df = ns.impute_nulls(df, column=['Age', 'Gender'], strategy='interpolate')

# Impute all features with missing values using automatic strategy detection
df = ns.impute_nulls(df)

# Drop rows with missing values
df = ns.impute_nulls(df, strategy="listwise")

# Create missing flags for multiple columns in new columns
df = ns.impute_nulls(df, column=['Age', 'Gender'], strategy="flag")

```

### Visualize Missing Values

Options: 'heatmap', 'correlation', 'percentage', 'matrix', 'dendogram', 'upset_plot', 'pair', 'wordcloud', 'histogram'

```python

figure = ns.plot_missing_values(df, "heatmap")
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests, open issues, or suggest improvements.
