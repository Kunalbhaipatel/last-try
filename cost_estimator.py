# cost_estimator.py (Cost Estimator Page)

import streamlit as st
import pandas as pd
import plotly.express as px

# Import shared utility functions and chart functions
from utils import apply_shared_filters
from enhanced_dashboard_charts import stacked_cost_chart

def render_cost_estimator(df):
    """
    Renders the Flowline Shaker Cost Comparison page with enhanced UI/UX.

    Args:
        df (pd.DataFrame): The raw input DataFrame.
    """
    st.title("💰 Flowline Shaker Cost Comparison")
    
    # Apply shared filters first
    filtered_df_shared = apply_shared_filters(df)

    if filtered_df_shared.empty:
        st.info("No data available for Cost Estimator with current filters.")
        return

    col_d, col_nd = st.columns(2)

    # --- Derrick Filters and Data ---
    with col_d:
        st.subheader("🟩 Derrick")
        # Filter for Derrick shakers from the already shared-filtered DataFrame
        derrick_df_base = filtered_df_shared[filtered_df_shared["flowline_Shakers"].str.contains("Derrick", na=False)]

        derrick_shaker_options = sorted(derrick_df_base["flowline_Shakers"].dropna().unique().tolist())
        derrick_shaker = st.selectbox("Select Flowline Shaker", ["All"] + derrick_shaker_options, key="d_shaker_select")
        if derrick_shaker != "All":
            derrick_df_base = derrick_df_base[derrick_df_base["flowline_Shakers"] == derrick_shaker]

        derrick_ops = sorted(derrick_df_base["Operator"].dropna().unique().tolist())
        derrick_operator = st.selectbox("Select Operator", ["All"] + derrick_ops, key="d_operator_select")
        if derrick_operator != "All":
            derrick_df_base = derrick_df_base[derrick_df_base["Operator"] == derrick_operator]

        derrick_contracts = sorted(derrick_df_base["Contractor"].dropna().unique().tolist())
        derrick_contractor = st.selectbox("Select Contractor", ["All"] + derrick_contracts, key="d_contract_select")
        if derrick_contractor != "All":
            derrick_df_base = derrick_df_base[derrick_df_base["Contractor"] == derrick_contractor]

        derrick_wells = sorted(derrick_df_base["Well_Name"].dropna().unique().tolist())
        derrick_well = st.selectbox("Select Well Name", ["All"] + derrick_wells, key="d_well_select")
        if derrick_well != "All":
            derrick_df_base = derrick_df_base[derrick_df_base["Well_Name"] == derrick_well]
        
        derrick_df = derrick_df_base # This is the final filtered DataFrame for Derrick


    # --- Non-Derrick Filters and Data ---
    with col_nd:
        st.subheader("🟣 Non-Derrick")
        # Filter for Non-Derrick shakers from the already shared-filtered DataFrame
        nond_df_base = filtered_df_shared[~filtered_df_shared["flowline_Shakers"].str.contains("Derrick", na=False)]

        nond_shaker_options = sorted(nond_df_base["flowline_Shakers"].dropna().unique().tolist())
        nond_shaker = st.selectbox("Select Flowline Shaker", ["All"] + nond_shaker_options, key="nd_shaker_select")
        if nond_shaker != "All":
            nond_df_base = nond_df_base[nond_df_base["flowline_Shakers"] == nond_shaker]

        nond_ops = sorted(nond_df_base["Operator"].dropna().unique().tolist())
        nond_operator = st.selectbox("Select Operator", ["All"] + nond_ops, key="nd_operator_select")
        if nond_operator != "All":
            nond_df_base = nond_df_base[nond_df_base["Operator"] == nond_operator]

        nond_contracts = sorted(nond_df_base["Contractor"].dropna().unique().tolist())
        nond_contractor = st.selectbox("Select Contractor", ["All"] + nond_contracts, key="nd_contract_select")
        if nond_contractor != "All":
            nond_df_base = nond_df_base[nond_df_base["Contractor"] == nond_contractor]

        nond_wells = sorted(nond_df_base["Well_Name"].dropna().unique().tolist())
        nond_well = st.selectbox("Select Well Name", ["All"] + nond_wells, key="nd_well_select")
        if nond_well != "All":
            nond_df_base = nond_df_base[nond_df_base["Well_Name"] == nond_well]
        
        nond_df = nond_df_base # This is the final filtered DataFrame for Non-Derrick

    # Default configurations for cost calculation
    derrick_config = {}
    nond_config = {}

    # --- Configuration Inputs (using expanders for better UI) ---
    with st.expander("🎯 Derrick Configuration"):
        derrick_config["dil_rate"] = st.number_input("Dilution Cost Rate ($/unit)", value=100.0, key="d_dil")
        derrick_config["haul_rate"] = st.number_input("Haul-Off Cost Rate ($/unit)", value=20.0, key="d_haul")
        derrick_config["screen_price"] = st.number_input("Screen Price", value=500.0, key="d_scr_price")
        derrick_config["num_screens"] = st.number_input("Screens used per rig", value=1, min_value=0, key="d_scr_cnt")
        derrick_config["equip_cost"] = st.number_input("Total Equipment Cost", value=100000.0, key="d_equip")
        derrick_config["num_shakers"] = st.number_input("Number of Shakers Installed", value=3, min_value=0, key="d_shkrs")
        derrick_config["shaker_life"] = st.number_input("Shaker Life (Years)", value=7.0, min_value=0.1, key="d_life")
        derrick_config["eng_cost"] = st.number_input("Engineering Day Rate", value=1000.0, key="d_eng")
        derrick_config["other_cost"] = st.number_input("Other Cost", value=500.0, key="d_other")

    with st.expander("🎯 Non-Derrick Configuration"):
        nond_config["dil_rate"] = st.number_input("Dilution Cost Rate ($/unit)", value=100.0, key="nd_dil")
        nond_config["haul_rate"] = st.number_input("Haul-Off Cost Rate ($/unit)", value=20.0, key="nd_haul")
        nond_config["screen_price"] = st.number_input("Screen Price", value=500.0, key="nd_scr_price")
        nond_config["num_screens"] = st.number_input("Screens used per rig", value=1, min_value=0, key="nd_scr_cnt")
        nond_config["equip_cost"] = st.number_input("Total Equipment Cost", value=100000.0, key="nd_equip")
        nond_config["num_shakers"] = st.number_input("Number of Shakers Installed", value=3, min_value=0, key="nd_shkrs")
        nond_config["shaker_life"] = st.number_input("Shaker Life (Years)", value=7.0, min_value=0.1, key="nd_life")
        nond_config["eng_cost"] = st.number_input("Engineering Day Rate", value=1000.0, key="nd_eng")
        nond_config["other_cost"] = st.number_input("Other Cost", value=500.0, key="nd_other")

    def calc_cost(sub_df, config, label):
        """
        Calculates various cost components and total cost per foot for a given DataFrame subset.
        Includes LGS% and DSRE% if available.
        """
        # Ensure columns exist and handle potential NaNs or empty sums
        td = sub_df["Total_Dil"].sum() if "Total_Dil" in sub_df.columns and not sub_df["Total_Dil"].empty else 0
        ho = sub_df["Haul_OFF"].sum() if "Haul_OFF" in sub_df.columns and not sub_df["Haul_OFF"].empty else 0
        intlen = sub_df["IntLength"].sum() if "IntLength" in sub_df.columns and not sub_df["IntLength"].empty else 0

        dilution = config["dil_rate"] * td
        haul = config["haul_rate"] * ho
        screen = config["screen_price"] * config["num_screens"]
        
        # Handle shaker_life being zero or very small to prevent division by zero
        equipment = (config["equip_cost"] * config["num_shakers"]) / config["shaker_life"] if config["shaker_life"] > 0 else 0
        
        total = dilution + haul + screen + equipment + config["eng_cost"] + config["other_cost"]
        per_ft = total / intlen if intlen else 0 # Avoid division by zero

        avg_lgs = (sub_df["LGS"].mean() * 100) if "LGS" in sub_df.columns and not sub_df["LGS"].empty else 0
        avg_dsre = (sub_df["DSRE"].mean() * 100) if "DSRE" in sub_df.columns and not sub_df["DSRE"].empty else 0

        return {
            "Label": label,
            "Cost/ft": per_ft,
            "Total Cost": total,
            "Dilution": dilution,
            "Haul": haul,
            "Screen": screen,
            "Equipment": equipment,
            "Engineering": config["eng_cost"],
            "Other": config["other_cost"],
            "Avg LGS%": avg_lgs,
            "DSRE%": avg_dsre,
            "Depth": sub_df["MD Depth"].max() if "MD Depth" in sub_df.columns and not sub_df["MD Depth"].empty else 0,
        }

    # Calculate costs for both types
    derrick_cost = calc_cost(derrick_df, derrick_config, "Derrick")
    nond_cost = calc_cost(nond_df, nond_config, "Non-Derrick")
    summary = pd.DataFrame([derrick_cost, nond_cost])

    # --- Display Cost Deltas with Enhanced UI ---
    delta_total = nond_cost['Total Cost'] - derrick_cost['Total Cost']
    delta_ft = nond_cost['Cost/ft'] - derrick_cost['Cost/ft']

    # Determine background and text colors based on delta value (savings vs. extra cost)
    bg_color_total = "#d4edda" if delta_total <= 0 else "#f8d7da" # Green for savings (non-derrick cheaper), red for extra cost
    text_color_total = "green" if delta_total <= 0 else "red"
    bg_color_ft = "#d4edda" if delta_ft <= 0 else "#f8d7da"
    text_color_ft = "green" if delta_ft <= 0 else "red"

    st.markdown(f"""
        <div style='display: flex; gap: 2rem; margin-top: 1rem;'>
            <div style='flex: 1; padding: 1rem; border: 2px solid #ccc; border-radius: 10px; box-shadow: 2px 2px 6px rgba(0,0,0,0.2); background-color: {bg_color_total};'>
                <h4 style='margin: 0 0 0.5rem 0; color: {text_color_total};'>💵 Total Cost Delta (Non-Derrick vs. Derrick)</h4>
                <div style='font-size: 24px; font-weight: bold; color: {text_color_total};'>${delta_total:,.0f}</div>
            </div>
            <div style='flex: 1; padding: 1rem; border: 2px solid #ccc; border-radius: 10px; box-shadow: 2px 2px 6px rgba(0,0,0,0.2); background-color: {bg_color_ft};'>
                <h4 style='margin: 0 0 0.5rem 0; color: {text_color_ft};'>📏 Cost Per Foot Delta (Non-Derrick vs. Derrick)</h4>
                <div style='font-size: 24px; font-weight: bold; color: {text_color_ft};'>${delta_ft:,.2f}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- Cost Breakdown Pie Charts ---
    st.markdown("#### 📊 Cost Breakdown Pie Charts")
    pie1, pie2 = st.columns(2)

    with pie1:
        if not derrick_df.empty:
            derrick_fig = px.pie(
                names=["Dilution", "Haul", "Screen", "Equipment", "Engineering", "Other"],
                values=[derrick_cost[k] for k in ["Dilution", "Haul", "Screen", "Equipment", "Engineering", "Other"]],
                title="Derrick Cost Breakdown",
                color_discrete_sequence=["#1b5e20", "#2e7d32", "#388e3c", "#43a047", "#4caf50", "#66bb6a"]
            )
            derrick_fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(derrick_fig, use_container_width=True)
        else:
            st.info("No Derrick data to display cost breakdown.")

    with pie2:
        if not nond_df.empty:
            nond_fig = px.pie(
                names=["Dilution", "Haul", "Screen", "Equipment", "Engineering", "Other"],
                values=[nond_cost[k] for k in ["Dilution", "Haul", "Screen", "Equipment", "Engineering", "Other"]],
                title="Non-Derrick Cost Breakdown",
                color_discrete_sequence=["#424242", "#616161", "#757575", "#9e9e9e", "#bdbdbd", "#e0e0e0"]
            )
            nond_fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(nond_fig, use_container_width=True)
        else:
            st.info("No Non-Derrick data to display cost breakdown.")

    # --- Cost per Foot and Depth Comparison Bar Charts ---
    st.markdown("#### 📉 Cost per Foot and Depth Comparison")
    bar1, bar2 = st.columns(2)

    with bar1:
        if not summary.empty:
            fig_cost = px.bar(summary, x="Label", y="Cost/ft", color="Label", title="Cost per Foot Comparison",
                              color_discrete_map={"Derrick": "#007635", "Non-Derrick": "grey"})
            st.plotly_chart(fig_cost, use_container_width=True)
        else:
            st.info("No summary data for cost per foot comparison.")

    with bar2:
        if not summary.empty:
            fig_depth = px.bar(summary, x="Label", y="Depth", color="Label", title="Total Depth Drilled",
                               color_discrete_map={"Derrick": "#007635", "Non-Derrick": "grey"})
            st.plotly_chart(fig_depth, use_container_width=True)
        else:
            st.info("No summary data for total depth drilled comparison.")

    stacked_cost_chart(summary) # Call stacked cost chart from enhanced_dashboard_charts

    # --- Additional Metrics for Cost Estimator ---
    st.subheader("Additional Performance Metrics")
    metric_col1, metric_col2 = st.columns(2)
    with metric_col1:
        st.metric("Derrick Avg LGS%", f"{derrick_cost['Avg LGS%']:.2f}%")
        st.metric("Derrick DSRE%", f"{derrick_cost['DSRE%']:.2f}%")
    with metric_col2:
        st.metric("Non-Derrick Avg LGS%", f"{nond_cost['Avg LGS%']:.2f}%")
        st.metric("Non-Derrick DSRE%", f"{nond_cost['DSRE%']:.2f}%")

