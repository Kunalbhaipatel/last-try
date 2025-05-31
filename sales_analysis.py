# sales_analysis.py (Sales Analysis Page)

import streamlit as st
import pandas as pd
import plotly.express as px

# Import shared utility functions and chart functions
from utils import apply_shared_filters
from enhanced_dashboard_charts import cumulative_wells_chart, fluid_pie_chart_by_operator, avg_rop_over_time_chart

def render_sales_analysis(df):
    """
    Renders the Sales Analysis Dashboard page.

    Args:
        df (pd.DataFrame): The raw input DataFrame.
    """
    st.title("📈 Prodigy IQ Sales Intelligence")
    filtered_df = apply_shared_filters(df) # Apply shared filters

    if filtered_df.empty:
        st.info("No data available for Sales Analysis with current filters.")
        return

    st.subheader("🧭 Wells Over Time")
    month_df = filtered_df.copy()
    
    if "TD_Date" in month_df.columns and not month_df["TD_Date"].empty:
        month_df["Month"] = month_df["TD_Date"].dt.to_period("M").astype(str)
        volume = month_df.groupby("Month").size().reset_index(name="Well Count")
        
        if not volume.empty:
            fig_monthly = px.bar(volume, x="Month", y="Well Count", title="Wells Completed per Month")
            st.plotly_chart(fig_monthly, use_container_width=True)
            cumulative_wells_chart(volume) # Call cumulative wells chart
        else:
            st.info("No monthly well completion data available.")
    else:
        st.info("TD_Date column is missing or empty, cannot show wells over time.")

    avg_rop_over_time_chart(filtered_df) # New chart added

    st.subheader("🧮 Avg Discard Ratio vs Contractor")
    if "Contractor" in filtered_df.columns and "Discard Ratio" in filtered_df.columns and not filtered_df.empty:
        avg_discard = filtered_df.groupby("Contractor")["Discard Ratio"].mean().reset_index()
        if not avg_discard.empty:
            fig_discard = px.bar(avg_discard, x="Contractor", y="Discard Ratio", color="Contractor",
                                 title="Average Discard Ratio by Contractor")
            st.plotly_chart(fig_discard, use_container_width=True)
        else:
            st.info("No discard ratio data available for contractors.")
    else:
        st.info("Contractor or Discard Ratio columns are missing or empty.")


    st.subheader("🧃 Fluid Consumption by Operator")
    fluid_cols = ["Base_Oil", "Water", "Chemicals"]
    if all(col in filtered_df.columns for col in fluid_cols) and "Operator" in filtered_df.columns and not filtered_df.empty:
        fluid_df_grouped = filtered_df.groupby("Operator")[fluid_cols].sum().reset_index()
        
        if not fluid_df_grouped.empty:
            fluid_df_melted = pd.melt(fluid_df_grouped, id_vars="Operator", var_name="Fluid", value_name="Volume")
            
            if not fluid_df_melted.empty and fluid_df_melted['Volume'].sum() > 0:
                fig_fluid = px.bar(fluid_df_melted, x="Operator", y="Volume", color="Fluid", barmode="group",
                                   title="Fluid Consumption by Operator")
                st.plotly_chart(fig_fluid, use_container_width=True)
                fluid_pie_chart_by_operator(fluid_df_melted) # Call fluid pie chart
            else:
                st.info("No fluid consumption data available for operators.")
        else:
            st.info("No fluid consumption data available for operators.")
    else:
        st.info("Required fluid consumption columns (Base_Oil, Water, Chemicals, Operator) are missing or empty.")

