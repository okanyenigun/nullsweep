# NullSweep

NullSweep is a Python library designed for detecting patterns of missing data in pandas DataFrames. This tool provides a simple API to identify global missing data patterns across the entire dataset as well as patterns related to specific features within the dataset.

## Features

- Detect global patterns of missing data in a DataFrame.
- Detect missing data patterns in specific features/columns of a DataFrame.
- Utilizes a modular approach with different pattern detection strategies.

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

### Detect Feature-Specific Patterns

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

## Contributing

Contributions are welcome! Please feel free to submit pull requests, open issues, or suggest improvements.
