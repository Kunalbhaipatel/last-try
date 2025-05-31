# app.py (Main Streamlit Application)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import shared utility functions
from utils import apply_shared_filters

# Import all chart functions from enhanced_dashboard_charts
from enhanced_dashboard_charts import (
    radar_chart_multi_kpi,
    cumulative_wells_chart,
    fluid_pie_chart_by_operator,
    kpi_heatmap,
    kpi_boxplot,
    stacked_cost_chart,
    rop_vs_depth_scatter,
    avg_rop_over_time_chart,
    kpi_comparison_scatter,
    rop_by_operator_bar_chart
)

# Import render functions for each page
from multi_well import render_multi_well
from sales_analysis import render_sales_analysis
from advanced_analysis import render_advanced_analysis
from cost_estimator import render_cost_estimator
from executive_summary import render_executive_summary


# Set Streamlit page configuration ONCE at the top
st.set_page_config(page_title="Prodigy IQ Dashboard", layout="wide", page_icon="📊")

# ------------------------- STYLING -------------------------
def load_styles():
    """Applies custom CSS styling to Streamlit components."""
    st.markdown("""
    <style>
    /* Metric container styling */
    div[data-testid="metric-container"] {
        background-color: #fff;
        padding: 1.2em;
        border-radius: 15px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.1);
        margin: 0.5em;
        text-align: center;
    }
    /* Expander styling */
    .st-emotion-cache-1mn013o { /* This class might change with Streamlit updates, but targets expander header */
        background-color: #f0f2f6; /* Light grey background for expander header */
        border-radius: 10px;
        padding: 0.5rem 1rem;
        margin-bottom: 1rem;
    }
    /* General button styling */
    .stButton>button {
        background-color: #4CAF50; /* Green */
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        border: none;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
        box_shadow: 0 6px 12px rgba(0,0,0,0.3);
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)
    
# ------------------------- MAIN ENTRY POINT -------------------------
if __name__ == "__main__":
    load_styles() # Load custom CSS styles

    # Load data from CSV
    try:
        df = pd.read_csv("Refine Sample.csv")
        df["TD_Date"] = pd.to_datetime(df["TD_Date"], errors='coerce')
    except FileNotFoundError:
        st.error("Error: 'Refine Sample.csv' not found. Please ensure the CSV file is in the same directory.")
        st.stop() # Stop the app if data is not found
    except Exception as e:
        st.error(f"Error loading or processing data: {e}")
        st.stop()

    # Sidebar navigation
    page = st.sidebar.radio("📂 Navigate", [
        "Multi-Well Comparison",
        "Sales Analysis",
        "Advanced Analysis",
        "Cost Estimator",
        "Executive Summary"
    ])

    # Render the selected page based on sidebar selection
    if page == "Multi-Well Comparison":
        render_multi_well(df)
    elif page == "Sales Analysis":
        render_sales_analysis(df)
    elif page == "Advanced Analysis":
        render_advanced_analysis(df)
    elif page == "Cost Estimator":
        render_cost_estimator(df)
    elif page == "Executive Summary":
        render_executive_summary(df)

