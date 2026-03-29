"""
generate_visualizations.py
==========================
EDA visualization suite for the Zillow ZHVI housing price project.
Produces 6 core charts aligned to rubric criteria #3 (Data Understanding)
and #6 (Visualization).

Uses Plotly to generate interactive HTML dashboards and static PNGs.

Outputs (saved to visualizations/):
  1. national_price_trend.[html/png]
  2. log_return_by_year.[html/png]
  3. correlation_matrix.[html/png]
  4. lag_autocorrelation.[html/png]
  5. top_states_price.[html/png]
  6. target_distributions.[html/png]

Run:
    python src/visualization/generate_visualizations.py
"""

import sys
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from pathlib import Path

# Fix Windows terminal encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR     = PROJECT_ROOT / "data" / "processed"
VIZ_DIR      = PROJECT_ROOT / "visualizations"

# ── Style ─────────────────────────────────────────────────────────────────────
BLUE    = "#2C7BB6"
ORANGE  = "#D7191C"
GREEN   = "#1A9641"


def _save(fig: go.Figure, name: str) -> None:
    """Save static PNG (requires kaleido to be installed)."""
    png_path = VIZ_DIR / f"{name}.png"
    try:
        # Save PNG scale 2 for high definition
        fig.write_image(str(png_path), scale=2, width=1100, height=600)
        print(f"  Saved: {name}.png")
    except Exception as e:
        print(f"  Failed: {name}.png (kaleido not installed or error: {e})")


# ─────────────────────────────────────────────────────────────────────────────
# Plot 1: National Median Price Trend (line chart)
# ─────────────────────────────────────────────────────────────────────────────
def plot_national_price_trend(df: pd.DataFrame) -> None:
    trend = (df.groupby("date")["price"]
               .median()
               .reset_index()
               .sort_values("date"))

    fig = go.Figure()
    
    # Line and shaded area
    fig.add_trace(go.Scatter(
        x=trend["date"], 
        y=trend["price"],
        fill='tozeroy',
        mode='lines',
        name='Median Price',
        line=dict(color=BLUE, width=3),
        fillcolor='rgba(44, 123, 182, 0.15)',
        hovertemplate="Date: %{x|%Y-%m}<br>Median Price: $%{y:,.0f}<extra></extra>"
    ))

    # Add Vertical lines for events
    events = {
        "2008-09-01": ("2008 Crisis", ORANGE),
        "2020-03-01": ("COVID-19", "grey"),
        "2021-01-01": ("2021 Boom", GREEN),
    }

    annotations = []
    for date_str, (label, color) in events.items():
        fig.add_vline(x=date_str, line_dash="dash", line_color=color, opacity=0.8, line_width=2)
        annotations.append(dict(
            x=date_str, y=1.02, xref="x", yref="paper",
            text=f"<b>{label}</b>", showarrow=False, 
            font=dict(color=color, size=12)
        ))

    fig.update_layout(
        title="<b>U.S. Housing Market: National Median Price Trend (2001–2026)</b>",
        xaxis_title="<b>Year</b>",
        yaxis_title="<b>Median Price (USD)</b>",
        yaxis=dict(tickformat="$,.0s"),
        template="plotly_white",
        annotations=annotations,
        hovermode="x unified",
        margin=dict(t=80)
    )
    _save(fig, "national_price_trend")


# ─────────────────────────────────────────────────────────────────────────────
# Plot 2: Annual Log-Return Bar Chart
# ─────────────────────────────────────────────────────────────────────────────
def plot_log_return_by_year(df: pd.DataFrame) -> None:
    yearly = (df[df["log_return"] != 0]
                .groupby(df["date"].dt.year)["log_return"]
                .agg(mean="mean", std="std")
                .reset_index()
                .rename(columns={"date": "year"}))

    colors = [GREEN if v >= 0 else ORANGE for v in yearly["mean"]]

    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=yearly["year"], 
        y=yearly["mean"] * 100,
        marker_color=colors,
        name="Mean Log Return",
        error_y=dict(
            type='data',
            array=yearly["std"] * 100,
            visible=True,
            color='black',
            thickness=1.5
        ),
        hovertemplate="Year: %{x}<br>Mean Return: %{y:.3f}%<br>Std Dev: %{customdata:.3f}%<extra></extra>",
        customdata=yearly["std"] * 100
    ))

    # Zero Line
    fig.add_hline(y=0, line_width=1, line_color="black")

    # Recession / Boom backgrounds
    fig.add_vrect(x0=2007.5, x1=2011.5, fillcolor=ORANGE, opacity=0.1, layer="below", line_width=0, annotation_text="Housing Crisis", annotation_position="top left")
    fig.add_vrect(x0=2020.0, x1=2022.5, fillcolor=GREEN, opacity=0.1, layer="below", line_width=0, annotation_text="Post-COVID Boom", annotation_position="top left")

    fig.update_layout(
        title="<b>Annual Mean Log-Return of Housing Prices (2001–2026)</b>",
        xaxis_title="<b>Year</b>",
        yaxis_title="<b>Mean Monthly Log-Return (%)</b>",
        yaxis=dict(ticksuffix="%"),
        template="plotly_white",
        showlegend=False,
        margin=dict(t=80)
    )
    _save(fig, "log_return_by_year")


# ─────────────────────────────────────────────────────────────────────────────
# Plot 3: Correlation Heatmap
# ─────────────────────────────────────────────────────────────────────────────
def plot_correlation_matrix(df: pd.DataFrame) -> None:
    cols = ["log_return", "price", "lag_1", "lag_2", "lag_3", "lag_6", "lag_12", "city_enc"]
    corr = df[cols].corr().round(3)
    
    # Mask upper triangle
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    corr_masked = corr.mask(mask)

    x_labels = [c.replace('_', ' ').title() for c in corr.columns]
    y_labels = [c.replace('_', ' ').title() for c in corr.index]

    fig = go.Figure(data=go.Heatmap(
        z=corr_masked.values,
        x=x_labels,
        y=y_labels,
        colorscale='RdBu',
        zmin=-1, zmax=1,
        text=corr_masked.values,
        texttemplate="%{text:.3f}",
        textfont={"size": 12},
        hovertemplate="%{y} vs %{x}<br>Correlation: %{z:.3f}<extra></extra>"
    ))

    fig.update_layout(
        title="<b>Correlation Matrix: Feature & Target Variables</b>",
        template="plotly_white",
        width=800, height=800,
        margin=dict(t=80, l=120, b=100)
    )
    # Reverse y-axis to match standard heatmap style
    fig.update_yaxes(autorange="reversed")
    _save(fig, "correlation_matrix")


# ─────────────────────────────────────────────────────────────────────────────
# Plot 4: Lag Feature Autocorrelation (bar chart)
# ─────────────────────────────────────────────────────────────────────────────
def plot_lag_autocorrelation(df: pd.DataFrame) -> None:
    lag_cols = ["lag_1", "lag_2", "lag_3", "lag_6", "lag_12"]
    corrs    = [df["log_return"].corr(df[c]) for c in lag_cols]
    labels   = ["Lag-1 (1 mo)", "Lag-2 (2 mo)", "Lag-3 (3 mo)", "Lag-6 (6 mo)", "Lag-12 (12 mo)"]
    colors   = [BLUE if c >= 0 else ORANGE for c in corrs]

    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=labels, 
        y=corrs,
        marker_color=colors,
        text=[f"{v:.4f}" for v in corrs],
        textposition='outside',
        textfont=dict(size=14, color='black'),
        hovertemplate="%{x}<br>Autocorrelation: %{y:.4f}<extra></extra>"
    ))

    fig.update_layout(
        title="<b>Autocorrelation: Lag Features vs Log-Return</b><br><sup>Predictive power decays with longer lag period</sup>",
        yaxis_title="<b>Pearson Correlation Coefficient</b>",
        yaxis=dict(range=[0, 1.1]),
        template="plotly_white",
        width=900, height=500,
        margin=dict(t=100)
    )
    _save(fig, "lag_autocorrelation")


# ─────────────────────────────────────────────────────────────────────────────
# Plot 5: Top 10 vs Bottom 10 States by Average Price
# ─────────────────────────────────────────────────────────────────────────────
def plot_top_states_price(df: pd.DataFrame) -> None:
    state_avg = (df.groupby("StateName")["price"]
                   .mean()
                   .sort_values(ascending=False)
                   .reset_index())
    
    top10    = state_avg.head(10).sort_values("price", ascending=True)
    bottom10 = state_avg.tail(10).sort_values("price", ascending=True)

    fig = make_subplots(rows=1, cols=2, subplot_titles=("<b>Top 10 Most Expensive States</b>", "<b>Bottom 10 Most Affordable States</b>"))

    # Top 10 (Red)
    fig.add_trace(go.Bar(
        x=top10["price"], y=top10["StateName"], orientation='h',
        marker_color=ORANGE,
        text=top10["price"].apply(lambda x: f"${x/1000:,.0f}K"),
        textposition='outside', textfont=dict(size=11),
        hovertemplate="State: %{y}<br>Avg Price: $%{x:,.0f}<extra></extra>"
    ), row=1, col=1)

    # Bottom 10 (Blue)
    fig.add_trace(go.Bar(
        x=bottom10["price"], y=bottom10["StateName"], orientation='h',
        marker_color=BLUE,
        text=bottom10["price"].apply(lambda x: f"${x/1000:,.0f}K"),
        textposition='outside', textfont=dict(size=11),
        hovertemplate="State: %{y}<br>Avg Price: $%{x:,.0f}<extra></extra>"
    ), row=1, col=2)

    fig.update_layout(
        title="<b>Average Housing Price by State (2001–2026)</b>",
        template="plotly_white",
        showlegend=False,
        margin=dict(t=100, l=80)
    )
    
    fig.update_xaxes(title_text="Avg Price (USD)", row=1, col=1, tickformat="$,.0s")
    fig.update_xaxes(title_text="Avg Price (USD)", row=1, col=2, tickformat="$,.0s")
    
    # Extend X-axis to ensure labels aren't cut off
    fig.update_xaxes(range=[0, top10["price"].max() * 1.2], row=1, col=1)
    fig.update_xaxes(range=[0, bottom10["price"].max() * 1.2], row=1, col=2)

    _save(fig, "top_states_price")


# ─────────────────────────────────────────────────────────────────────────────
# Plot 6: Target Variable Distributions
# ─────────────────────────────────────────────────────────────────────────────
def plot_target_distributions(df: pd.DataFrame) -> None:
    sample = df.sample(100000, random_state=42) if len(df) > 100000 else df

    fig = make_subplots(rows=1, cols=2, subplot_titles=(
        "<b>Distribution of Housing Price</b>", 
        "<b>Distribution of Monthly Log-Return</b>"
    ))

    # Price distribution
    fig.add_trace(go.Histogram(
        x=sample["price"], nbinsx=80, marker_color=BLUE, name="Price",
        hovertemplate="Price Range: $%{x:,.0f}<br>Count: %{y}<extra></extra>"
    ), row=1, col=1)

    # Log Return distribution
    lr = sample["log_return"][sample["log_return"] != 0] * 100
    fig.add_trace(go.Histogram(
        x=lr, nbinsx=100, marker_color=GREEN, name="Log Return",
        hovertemplate="Return: %{x:.2f}%<br>Count: %{y}<extra></extra>"
    ), row=1, col=2)

    # Add Median / Mean lines
    med_price = sample["price"].median()
    fig.add_vline(x=med_price, line_dash="dash", line_color=ORANGE, line_width=2, 
                  annotation_text=f"Median:<br>${med_price:,.0f}", annotation_position="top right", row=1, col=1)

    mean_lr = lr.mean()
    fig.add_vline(x=mean_lr, line_dash="dash", line_color=ORANGE, line_width=2, 
                  annotation_text=f"Mean:<br>{mean_lr:.3f}%", annotation_position="top right", row=1, col=2)

    fig.update_layout(
        title="<b>Target Variable Distributions</b>",
        template="plotly_white",
        showlegend=False,
        margin=dict(t=100)
    )
    
    fig.update_xaxes(title_text="Price (USD)", tickformat="$,.0s", row=1, col=1)
    fig.update_xaxes(title_text="Log Return (%)", tickformat=".1f", ticksuffix="%", row=1, col=2)
    
    _save(fig, "target_distributions")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def create_visualizations() -> None:
    VIZ_DIR.mkdir(exist_ok=True)

    print("Loading data/processed/train.csv + test.csv ...")
    train = pd.read_csv(DATA_DIR / "train.csv", parse_dates=["date"])
    test  = pd.read_csv(DATA_DIR / "test.csv",  parse_dates=["date"])
    df    = pd.concat([train, test], ignore_index=True).sort_values("date")
    print(f"  Combined shape: {df.shape}\n")

    print("1. National price trend ...")
    plot_national_price_trend(df)

    print("2. Log-return by year ...")
    plot_log_return_by_year(df)

    print("3. Correlation matrix ...")
    plot_correlation_matrix(df)

    print("4. Lag autocorrelation ...")
    plot_lag_autocorrelation(df)

    print("5. Top/bottom states by price ...")
    plot_top_states_price(df)

    print("6. Target distributions ...")
    plot_target_distributions(df)

    print(f"\nAll static plots saved to: {VIZ_DIR}")


if __name__ == "__main__":
    create_visualizations()
