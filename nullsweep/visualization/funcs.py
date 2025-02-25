import pandas as pd
import seaborn as sns
import missingno as msno
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from upsetplot import plot as upsetplot
from upsetplot import from_indicators
from matplotlib.figure import Figure
from ..utils.decorators import to_pandas


FIGSIZE = (10, 6)

@to_pandas
def plot_heatmap(df: pd.DataFrame) -> Figure:
    fig, ax = plt.subplots(figsize=FIGSIZE)
    sns.heatmap(df.isnull(), cbar=False, cmap="viridis", ax=ax)
    ax.set_title("Missing Values Heatmap")
    return fig

@to_pandas
def plot_correlation(df: pd.DataFrame) -> Figure:
    fig = plt.figure(figsize=(10, 6))
    msno.heatmap(df)
    return fig

@to_pandas
def plot_percentage(df: pd.DataFrame) -> Figure:
    missing_percentage = (df.isnull().sum() / len(df)) * 100
    fig, ax = plt.subplots(figsize=FIGSIZE)
    missing_percentage.sort_values(ascending=False).plot(kind='bar', color='skyblue', ax=ax)
    ax.set_title("Percentage of Missing Values by Column")
    ax.set_xlabel("Columns")
    ax.set_ylabel("% Missing")
    return fig

@to_pandas
def plot_matrix(df: pd.DataFrame) -> Figure:
    fig = plt.figure(figsize=FIGSIZE)
    msno.matrix(df)
    return fig

@to_pandas
def plot_dendrogram(df: pd.DataFrame) -> Figure:
    fig = plt.figure(figsize=FIGSIZE)
    msno.dendrogram(df)
    return fig

@to_pandas
def plot_upset_plot(df: pd.DataFrame) -> Figure:
    df_missing = df.isnull().copy()
    upset_data = from_indicators(df_missing.columns, df_missing)
    fig = plt.figure(figsize=FIGSIZE)
    upsetplot(upset_data, fig=fig)
    return fig

@to_pandas
def plot_wordcloud(df: pd.DataFrame) -> Figure:
    missing_dict = dict(zip(df.columns, df.isnull().sum()))
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(missing_dict)
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("Missing Values Word Cloud")
    return fig

@to_pandas
def plot_pair(df: pd.DataFrame) -> Figure:
    df['missing'] = df.isnull().any(axis=1)
    g = sns.pairplot(df, hue='missing')
    return g.figure

@to_pandas
def plot_histogram(df: pd.DataFrame) -> Figure:
    fig, ax = plt.subplots(figsize=FIGSIZE)
    df.isnull().sum(axis=1).plot(kind='hist', bins=20, color='orange', edgecolor='black', ax=ax)
    ax.set_title("Histogram of Missing Values per Row")
    ax.set_xlabel("Number of Missing Values")
    ax.set_ylabel("Frequency")
    return fig


PLOT_FUNCTIONS = {
    'heatmap': lambda df: plot_heatmap(df),
    'correlation': lambda df: plot_correlation(df),
    'percentage': lambda df: plot_percentage(df),
    'matrix': lambda df: plot_matrix(df),
    'dendogram': lambda df: plot_dendrogram(df),
    'upset_plot': lambda df: plot_upset_plot(df),
    'pair': lambda df: plot_pair(df),
    'wordcloud': lambda df: plot_wordcloud(df),
    'histogram': lambda df: plot_histogram(df),
}