# multi_well.py (Multi-Well Comparison Page)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import shared utility functions and chart functions
from utils import apply_shared_filters
from enhanced_dashboard_charts import radar_chart_multi_kpi, rop_vs_depth_scatter

def render_multi_well(df):
    """
    Renders the Multi-Well Comparison Dashboard page.

    Args:
        df (pd.DataFrame): The raw input DataFrame.
    """
    st.title("🚀 Prodigy IQ Multi-Well Dashboard")
    filtered_df = apply_shared_filters(df) # Apply shared filters

    if filtered_df.empty:
        st.info("No data available for Multi-Well Comparison with current filters.")
        return

    st.subheader("Summary Metrics")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    # Display metrics, handling potential empty data or NaN values
    col1.metric("📏 IntLength", f"{filtered_df['IntLength'].mean():.1f}" if 'IntLength' in filtered_df.columns and not filtered_df['IntLength'].empty else "N/A")
    col2.metric("🏃 ROP", f"{filtered_df['ROP'].mean():.1f}" if 'ROP' in filtered_df.columns and not filtered_df['ROP'].empty else "N/A")
    col3.metric("🧪 Dilution Ratio", f"{filtered_df['Dilution_Ratio'].mean():.2f}" if 'Dilution_Ratio' in filtered_df.columns and not filtered_df['Dilution_Ratio'].empty else "N/A")
    col4.metric("🧴 Discard Ratio", f"{filtered_df['Discard Ratio'].mean():.2f}" if 'Discard Ratio' in filtered_df.columns and not filtered_df['Discard Ratio'].empty else "N/A")
    col5.metric("🚛 Haul OFF", f"{filtered_df['Haul_OFF'].mean():.1f}" if 'Haul_OFF' in filtered_df.columns and not filtered_df['Haul_OFF'].empty else "N/A")
    col6.metric("🌡️ AMW", f"{filtered_df['AMW'].mean():.2f}" if 'AMW' in filtered_df.columns and not filtered_df['AMW'].empty else "N/A")

    st.subheader("📊 Compare Metrics")
    numeric_cols = filtered_df.select_dtypes(include='number').columns.tolist()
    # Exclude columns that are IDs or not relevant for direct comparison as primary metric
    exclude = ['No', 'Well_Job_ID', 'Well_Coord_Lon', 'Well_Coord_Lat', 'Hole_Size', 'IsReviewed', 'State Code', 'County Code', 'Total_SCE', 'Base_Oil', 'Water', 'Chemicals', 'Drilling_Hours', 'Total_Dil', 'LGS', 'DSRE']
    metric_options = [col for col in numeric_cols if col not in exclude]
    
    if not metric_options:
        st.info("No comparable numeric metrics available with current filters.")
    else:
        selected_metric = st.selectbox("Select Metric", metric_options, key="multi_well_metric_select")

        if selected_metric:
            fig = px.bar(filtered_df, x="Well_Name", y=selected_metric, color="Operator",
                         title=f"{selected_metric} across Wells")
            fig.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)

    radar_chart_multi_kpi(filtered_df) # Call the radar chart function

    rop_vs_depth_scatter(filtered_df) # New chart added

    st.subheader("🗺️ Well Map")
    # Ensure latitude and longitude columns exist and have non-null values
    if "Well_Coord_Lon" in filtered_df.columns and "Well_Coord_Lat" in filtered_df.columns and not filtered_df.dropna(subset=["Well_Coord_Lon", "Well_Coord_Lat"]).empty:
        fig_map = px.scatter_mapbox(
            filtered_df.dropna(subset=["Well_Coord_Lon", "Well_Coord_Lat"]),
            lat="Well_Coord_Lat", lon="Well_Coord_Lon", hover_name="Well_Name",
            color="Operator", # Color points by operator
            zoom=4, height=500,
            title="Well Locations"
        )
        fig_map.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No valid geographical coordinates available for the well map with current filters.")

