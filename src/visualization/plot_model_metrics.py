"""
plot_model_metrics.py
=====================
Visualizes model evaluation metrics (MAE, RMSE, R²) using Plotly.
Generates an interactive HTML dashboard.
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import sys

# Fix Windows terminal encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Paths ─────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # ADY2026/
VIZ_DIR      = PROJECT_ROOT / "visualizations"

def plot_interactive_metrics():
    VIZ_DIR.mkdir(exist_ok=True)
    
    print("Loading metrics data...")
    df = pd.read_csv(VIZ_DIR / 'model_metrics_v2.csv')
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add MAE Bar
    fig.add_trace(
        go.Bar(
            x=df['Model'],
            y=df['MAE'],
            name='MAE ($)',
            marker_color='#2C7BB6',
            text=df['MAE'].apply(lambda x: f"${x:,.0f}"),
            textposition='auto',
            hovertemplate="Model: %{x}<br>MAE: $%{y:,.2f}<extra></extra>"
        ),
        secondary_y=False,
    )
    
    # Add RMSE Bar
    fig.add_trace(
        go.Bar(
            x=df['Model'],
            y=df['RMSE'],
            name='RMSE ($)',
            marker_color='#D7191C',
            text=df['RMSE'].apply(lambda x: f"${x:,.0f}"),
            textposition='auto',
            hovertemplate="Model: %{x}<br>RMSE: $%{y:,.2f}<extra></extra>"
        ),
        secondary_y=False,
    )
    
    # Add R2 Line/Scatter
    fig.add_trace(
        go.Scatter(
            x=df['Model'],
            y=df['R2'],
            name='R² Score',
            mode='lines+markers+text',
            marker=dict(size=12, color='#1A9641'),
            line=dict(width=3, color='#1A9641'),
            text=df['R2'].apply(lambda x: f"{x:.4f}"),
            textposition='top center',
            hovertemplate="Model: %{x}<br>R²: %{y:.6f}<extra></extra>"
        ),
        secondary_y=True,
    )
    
    # Update layout and axes
    fig.update_layout(
        title={
            'text': "<b>Performance Metrics by Model</b><br><sup>Evaluating baseline vs trained regression models</sup>",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        plot_bgcolor='white',
        hovermode="x unified",
        font=dict(size=13),
        margin=dict(t=120)
    )
    
    # Left Y-Axis (Errors)
    fig.update_yaxes(
        title_text="<b>Error Value (USD)</b> (Lower is Better)",
        showgrid=True, gridwidth=1, gridcolor='LightGray',
        secondary_y=False
    )
    
    # Right Y-Axis (R2)
    fig.update_yaxes(
        title_text="<b>R² Score</b> (Higher is Better)",
        range=[-0.1, 1.15], # Give space for text labels
        showgrid=False,
        secondary_y=True
    )
    
    fig.update_xaxes(
        title_text="<b>Regression Model</b>", 
        showline=True, linewidth=1, linecolor='black'
    )
    
    # Save static PNG using Kaleido
    try:
        output_png = VIZ_DIR / 'metrics_model_comparison.png'
        fig.write_image(str(output_png), scale=2, width=1200, height=700)
        print(f"Saved static image to: {output_png}")
    except Exception as e:
        print("Note: To save static PNG from Plotly, please run 'pip install kaleido'")
        print(f"Error: {e}")

if __name__ == '__main__':
    plot_interactive_metrics()
