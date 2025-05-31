# advanced_analysis.py (Advanced Analysis Page)

import streamlit as st
import pandas as pd
import plotly.express as px

# Import shared utility functions and chart functions
from utils import apply_shared_filters
from enhanced_dashboard_charts import kpi_heatmap, kpi_boxplot, kpi_comparison_scatter

def render_advanced_analysis(df):
    """
    Renders the Advanced Analysis Dashboard page.

    Args:
        df (pd.DataFrame): The raw input DataFrame.
    """
    st.title("📌 Advanced Analysis Dashboard")
    filtered_df = apply_shared_filters(df) # Apply shared filters

    if filtered_df.empty:
        st.info("No data available for Advanced Analysis with current filters.")
        return

    st.sidebar.header("🛠️ Manual Input (If Data Missing)")
    # Ensure default values are reasonable and types are correct
    total_flow_rate = st.sidebar.number_input("Total Flow Rate (GPM)", value=800.0, format="%.1f", key="adv_flow_rate")
    number_of_screens = st.sidebar.number_input("Number of Screens Installed", value=3, min_value=1, key="adv_num_screens")
    screen_area = st.sidebar.number_input("Area per Screen (sq ft)", value=2.0, format="%.1f", key="adv_screen_area")
    unit = st.sidebar.radio("Normalize by", ["None", "Feet", "Hours", "Days"], key="adv_normalize_unit")

    def safe_div(n, d):
        """Safely divides n by d, returning 0 if d is zero or NaN."""
        if pd.isna(n) or pd.isna(d) or d == 0:
            return 0
        return n / d

    metrics = []
    for _, row in filtered_df.iterrows():
        # Use .get() with default values to handle potentially missing columns gracefully
        haul = row.get("Haul_OFF", 0)
        intlen = row.get("IntLength", 0)
        hole = row.get("Hole_Size", 1) # Avoid division by zero
        sce = row.get("Total_SCE", 0)
        bo, water, chem = row.get("Base_Oil", 0), row.get("Water", 0), row.get("Chemicals", 0)
        rop = row.get("ROP", 0)

        metrics.append({
            "Well_Name": row.get("Well_Name", "N/A"),
            "Operator": row.get("Operator", "N/A"),
            # Ensure calculations handle potential zero/NaN values correctly
            "Shaker Throughput Efficiency": safe_div(sce, sce) * 100 if sce > 0 else 0, # If SCE is 0, efficiency is 0
            "Cuttings Volume Ratio": safe_div(haul, intlen),
            "Screen Loading Index": safe_div(total_flow_rate, number_of_screens * screen_area),
            "Fluid Retention on Cuttings (%)": safe_div(sce, sce) * 100 if sce > 0 else 0,
            "Drilling Intensity Index": safe_div(rop, hole),
            "Fluid Loading Index": safe_div(bo + water + chem, intlen),
            "Chemical Demand Rate": safe_div(chem, intlen),
            "Mud Retention Efficiency (%)": 100 - (safe_div(sce, sce) * 100 if sce > 0 else 0),
            "Downstream Solids Loss": 100 - (safe_div(sce, sce) * 100 if sce > 0 else 0)
        })

    metric_df = pd.DataFrame(metrics)

    # Apply normalization based on selected unit
    divisor = None
    if unit == "Feet" and "IntLength" in filtered_df.columns:
        divisor = filtered_df["IntLength"].sum()
    elif unit == "Hours" and "Drilling_Hours" in filtered_df.columns:
        divisor = filtered_df["Drilling_Hours"].sum()
    elif unit == "Days" and "Drilling_Hours" in filtered_df.columns:
        divisor = safe_div(filtered_df["Drilling_Hours"].sum(), 24)
    # If divisor is 0 or None, no normalization will be applied
    
    if divisor and divisor != 0:
        for col in metric_df.columns[2:]: # Apply normalization to KPI columns
            metric_df[col] = metric_df[col].apply(lambda x: safe_div(x, divisor))

    st.subheader("📋 KPI Summary")
    # Display average of each KPI
    kpi_cols = st.columns(3)
    for i, col in enumerate(metric_df.columns[2:]):
        with kpi_cols[i % 3]:
            st.metric(col, f"{metric_df[col].mean():.2f}")

    st.subheader("📊 Compare Metrics")
    # Select a KPI for comparison bar chart
    kpi_options = metric_df.columns[2:].tolist()
    if not kpi_options:
        st.info("No calculated KPIs available for comparison.")
    else:
        selected_metric = st.selectbox("Select Metric", kpi_options, key="advanced_analysis_metric_select")
        if selected_metric:
            fig = px.bar(metric_df, x="Well_Name", y=selected_metric, color="Operator", 
                         title=f"{selected_metric} across Wells")
            fig.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

    kpi_heatmap(metric_df) # Call KPI heatmap
    kpi_boxplot(metric_df) # Call KPI boxplot
    kpi_comparison_scatter(metric_df) # New chart added

    st.subheader("📤 Export Filtered Data")
    if not metric_df.empty:
        st.download_button(
            label="Download CSV",
            data=metric_df.to_csv(index=False).encode('utf-8'), # Encode for download
            file_name="filtered_advanced_metrics.csv",
            mime="text/csv"
        )
    else:
        st.info("No data to export.")

