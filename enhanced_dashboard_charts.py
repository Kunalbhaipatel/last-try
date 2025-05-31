# enhanced_dashboard_charts.py (Contains all Plotly chart functions)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def radar_chart_multi_kpi(filtered_df):
    """
    Generates a multi-KPI radar chart for selected wells.

    Args:
        filtered_df (pd.DataFrame): The DataFrame filtered by shared criteria.
    """
    st.subheader("🕸️ Multi-KPI Radar Comparison")
    radar_metrics = ["ROP", "Dilution_Ratio", "Discard Ratio", "AMW", "Haul_OFF"]
    
    # Filter out wells with NaN in radar_metrics before grouping
    radar_df = filtered_df.dropna(subset=radar_metrics).groupby("Well_Name")[radar_metrics].mean().reset_index()
    
    if radar_df.empty:
        st.info("No data available for the radar chart with current filters.")
        return

    # Default to selecting up to 3 wells if available
    default_wells = radar_df["Well_Name"].unique()[:3].tolist()
    selected_wells = st.multiselect("Select Wells for Radar Chart", radar_df["Well_Name"].unique(), default=default_wells, key="radar_wells_select")
    
    if not selected_wells:
        st.info("Please select at least one well to display the radar chart.")
        return

    radar_data = radar_df[radar_df["Well_Name"].isin(selected_wells)]
    
    if radar_data.empty:
        st.info("Selected wells have no data for the radar chart metrics.")
        return

    fig = go.Figure()
    for _, row in radar_data.iterrows():
        # Ensure data is numeric and handle potential NaNs in individual rows for radar
        r_values = [row[metric] if pd.notna(row[metric]) else 0 for metric in radar_metrics]
        fig.add_trace(go.Scatterpolar(r=r_values, theta=radar_metrics, fill='toself', name=row["Well_Name"]))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, radar_data[radar_metrics].max().max() * 1.1] if not radar_data.empty else [0,100] # Dynamically set range
            )
        ),
        showlegend=True,
        title="Multi-KPI Performance by Well"
    )
    st.plotly_chart(fig, use_container_width=True)


def rop_vs_depth_scatter(filtered_df):
    """
    Generates a scatter plot of ROP vs. MD Depth.
    """
    st.subheader("📈 ROP vs. MD Depth")
    if "ROP" in filtered_df.columns and "MD Depth" in filtered_df.columns and not filtered_df.empty:
        fig = px.scatter(filtered_df, x="MD Depth", y="ROP", color="Operator",
                         hover_name="Well_Name", title="Rate of Penetration vs. Measured Depth",
                         labels={"MD Depth": "Measured Depth (ft)", "ROP": "ROP (ft/hr)"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ROP or MD Depth columns are missing or empty for scatter plot.")

def cumulative_wells_chart(volume_df):
    """
    Generates a cumulative wells completed chart over time.

    Args:
        volume_df (pd.DataFrame): DataFrame with 'Month' and 'Well Count'.
    """
    st.subheader("📈 Cumulative Wells Over Time")
    if volume_df.empty or 'Month' not in volume_df.columns or 'Well Count' not in volume_df.columns:
        st.info("No data available to show cumulative wells.")
        return

    volume_df['Cumulative Well Count'] = volume_df['Well Count'].cumsum()
    fig_cumulative = px.line(volume_df, x="Month", y="Cumulative Well Count", 
                             title="Cumulative Wells Completed Over Time",
                             markers=True) # Add markers for clarity
    fig_cumulative.update_layout(xaxis_title="Month", yaxis_title="Cumulative Well Count")
    st.plotly_chart(fig_cumulative, use_container_width=True)


def avg_rop_over_time_chart(filtered_df):
    """
    Generates a line chart showing average ROP over time.
    """
    st.subheader("📊 Average ROP Over Time")
    if "TD_Date" in filtered_df.columns and "ROP" in filtered_df.columns and not filtered_df.empty:
        # Ensure TD_Date is datetime and ROP is numeric
        df_plot = filtered_df.copy()
        df_plot["TD_Date"] = pd.to_datetime(df_plot["TD_Date"], errors='coerce')
        df_plot.dropna(subset=["TD_Date", "ROP"], inplace=True)
        
        if df_plot.empty:
            st.info("No valid TD Date or ROP data for average ROP over time chart.")
            return

        df_plot['Month'] = df_plot['TD_Date'].dt.to_period("M").astype(str)
        avg_rop_monthly = df_plot.groupby('Month')['ROP'].mean().reset_index()
        
        fig = px.line(avg_rop_monthly, x='Month', y='ROP', 
                      title='Average ROP per Month', markers=True)
        fig.update_layout(xaxis_title="Month", yaxis_title="Average ROP (ft/hr)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("TD_Date or ROP columns are missing or empty for average ROP over time chart.")


def fluid_pie_chart_by_operator(fluid_df):
    """
    Generates a pie chart showing fluid consumption distribution by operator.

    Args:
        fluid_df (pd.DataFrame): DataFrame with 'Operator', 'Fluid', and 'Volume'.
    """
    st.subheader("🧃 Fluid Consumption Distribution by Operator")
    if fluid_df.empty or 'Operator' not in fluid_df.columns or 'Volume' not in fluid_df.columns:
        st.info("No fluid consumption data available for pie chart with current filters.")
        return

    # Ensure 'Volume' is numeric and handle potential NaNs
    fluid_df['Volume'] = pd.to_numeric(fluid_df['Volume'], errors='coerce').fillna(0)
    
    # Aggregate total volume per operator
    total_fluid_per_operator = fluid_df.groupby('Operator')['Volume'].sum().reset_index()
    
    if not total_fluid_per_operator.empty and total_fluid_per_operator['Volume'].sum() > 0:
        fig_pie = px.pie(
            total_fluid_per_operator,
            values="Volume",
            names="Operator",
            title="Total Fluid Consumption by Operator",
            hole=0.3 # Add a hole for a donut chart effect
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No meaningful fluid consumption data available for pie chart.")


def kpi_heatmap(metric_df):
    """
    Generates a correlation heatmap of KPIs.

    Args:
        metric_df (pd.DataFrame): DataFrame containing calculated KPI metrics.
    """
    st.subheader("🔥 KPI Correlation Heatmap")
    # Exclude non-numeric columns from the heatmap and ensure there are enough columns for correlation
    numeric_metric_df = metric_df.select_dtypes(include='number')
    
    if numeric_metric_df.empty or numeric_metric_df.shape[1] < 2:
        st.info("Not enough numeric KPIs to display a correlation heatmap.")
        return

    # Calculate correlation matrix, handling potential NaNs
    corr_matrix = numeric_metric_df.corr()
    
    fig_heatmap = px.imshow(
        corr_matrix, 
        text_auto=True, 
        aspect="auto",
        color_continuous_scale=px.colors.sequential.Plasma, # Choose a nice color scale
        title="Correlation Heatmap of KPIs"
    )
    fig_heatmap.update_layout(xaxis_showgrid=False, yaxis_showgrid=False) # Remove grid for cleaner look
    st.plotly_chart(fig_heatmap, use_container_width=True)


def kpi_boxplot(metric_df):
    """
    Generates box plots to show KPI distribution by operator.

    Args:
        metric_df (pd.DataFrame): DataFrame containing calculated KPI metrics.
    """
    st.subheader("📦 KPI Distribution (Box Plots)")
    
    # Get only numeric columns that are not 'Well_Name' or 'Operator'
    kpi_cols_for_boxplot = [col for col in metric_df.select_dtypes(include='number').columns if col not in ['Well_Name']]
    
    if 'Operator' not in metric_df.columns or metric_df['Operator'].empty:
        st.info("Operator column is missing or empty, cannot create box plots by operator.")
        return

    if not kpi_cols_for_boxplot:
        st.info("No suitable numeric KPIs found for box plots.")
        return

    selected_kpi_boxplot = st.selectbox("Select KPI for Box Plot", kpi_cols_for_boxplot, key="kpi_boxplot_select")
    
    if selected_kpi_boxplot:
        fig_boxplot = px.box(metric_df, x="Operator", y=selected_kpi_boxplot,
                             title=f"Distribution of {selected_kpi_boxplot} by Operator",
                             points="all") # Show all points for better insight
        fig_boxplot.update_layout(xaxis_title="Operator", yaxis_title=selected_kpi_boxplot)
        st.plotly_chart(fig_boxplot, use_container_width=True)

def kpi_comparison_scatter(metric_df):
    """
    Generates a scatter plot to compare two selected KPIs.
    """
    st.subheader("📈 KPI Relationship Scatter Plot")
    kpi_options = metric_df.columns[2:].tolist() # Assuming first two are Well_Name, Operator
    
    if len(kpi_options) < 2:
        st.info("Not enough KPIs to create a scatter plot comparison.")
        return

    col_x, col_y = st.columns(2)
    with col_x:
        x_kpi = st.selectbox("Select X-axis KPI", kpi_options, key="scatter_x_kpi")
    with col_y:
        # Ensure y_kpi is different from x_kpi if possible, or pick next available
        default_y_index = 0
        if x_kpi in kpi_options and len(kpi_options) > 1:
            x_idx = kpi_options.index(x_kpi)
            default_y_index = (x_idx + 1) % len(kpi_options) # Pick the next KPI
        
        y_kpi = st.selectbox("Select Y-axis KPI", kpi_options, index=default_y_index, key="scatter_y_kpi")

    if x_kpi and y_kpi:
        fig = px.scatter(metric_df, x=x_kpi, y=y_kpi, color="Operator", hover_name="Well_Name",
                         title=f"{x_kpi} vs. {y_kpi}",
                         labels={x_kpi: x_kpi, y_kpi: y_kpi})
        st.plotly_chart(fig, use_container_width=True)

def stacked_cost_chart(summary_df):
    """
    Generates a stacked bar chart for cost breakdown.

    Args:
        summary_df (pd.DataFrame): DataFrame with cost summary.
    """
    st.subheader("📊 Stacked Cost Breakdown")
    if summary_df.empty:
        st.info("No cost summary data available for stacked chart.")
        return

    cost_components = ["Dilution", "Haul", "Screen", "Equipment", "Engineering", "Other"]
    
    # Ensure all cost components are present and numeric, fill NaN with 0
    for comp in cost_components:
        if comp not in summary_df.columns:
            summary_df[comp] = 0.0
        summary_df[comp] = pd.to_numeric(summary_df[comp], errors='coerce').fillna(0)

    fig_stacked = px.bar(summary_df, x="Label", y=cost_components, 
                         title="Cost Breakdown by Component (Stacked)",
                         barmode="stack",
                         color_discrete_sequence=px.colors.qualitative.Pastel) # Use a nice color palette
    fig_stacked.update_layout(xaxis_title="Shaker Type", yaxis_title="Cost")
    st.plotly_chart(fig_stacked, use_container_width=True)

def rop_by_operator_bar_chart(filtered_df):
    """
    Generates a bar chart showing average ROP by Operator.
    """
    st.subheader("Average ROP by Operator")
    if "Operator" in filtered_df.columns and "ROP" in filtered_df.columns and not filtered_df.empty:
        avg_rop_operator = filtered_df.groupby("Operator")["ROP"].mean().reset_index()
        fig = px.bar(avg_rop_operator, x="Operator", y="ROP", color="Operator",
                     title="Average Rate of Penetration by Operator")
        fig.update_layout(xaxis_title="Operator", yaxis_title="Average ROP (ft/hr)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Operator or ROP data missing for this chart.")

