# NullSweep

NullSweep is a Python library designed for detecting and handling patterns of missing data in pandas DataFrames. This tool provides a simple API to identify global missing data patterns across the entire dataset, patterns related to specific features within the dataset, and to impute missing values using various strategies.

## Features

- Detect global patterns of missing data in a DataFrame.
- Detect missing data patterns in specific features/columns of a DataFrame.
- Impute missing data in specific features or across the entire DataFrame using a variety of strategies.
- Utilizes a modular approach with different pattern detection and imputation strategies.

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

To impute missing values in a specific feature or across the entire DataFrame:

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
df = ns.impute_nulls(df, feature='Age', strategy='mean')

# Impute missing values in 'Gender' using the most frequent value
df = ns.impute_nulls(df, feature='Gender', strategy='most_frequent')

# Impute missing values in 'Age' using linear interpolation
df = ns.impute_nulls(df, feature='Age', strategy='interpolate')

# Impute missing values for multiple features
df = ns.impute_nulls(df, feature=['Age', 'Gender'], strategy='interpolate')

# Impute all features with missing values using automatic strategy detection
df = ns.impute_nulls(df)
```

## Contributing

Contributions are welcome! Please feel free to submit pull requests, open issues, or suggest improvements.
