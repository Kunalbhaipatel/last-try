# executive_summary.py (Executive Summary Page)

import streamlit as st
import pandas as pd

# Import shared utility functions and chart functions
from utils import apply_shared_filters
from enhanced_dashboard_charts import rop_by_operator_bar_chart

def render_executive_summary(df):
    """
    Renders the Executive Summary page, providing key drilling performance metrics.

    Args:
        df (pd.DataFrame): The raw input DataFrame.
    """
    st.title("📄 Executive Summary")
    filtered_df = apply_shared_filters(df) # Apply shared filters

    if filtered_df.empty:
        st.info("No data available for Executive Summary with current filters.")
        return

    # Calculate summary statistics, handling potential empty data or NaN values
    total_wells = filtered_df["Well_Name"].nunique() if "Well_Name" in filtered_df.columns else 0
    avg_rop = filtered_df["ROP"].mean() if "ROP" in filtered_df.columns and not filtered_df["ROP"].empty else 0.0
    avg_amw = filtered_df["AMW"].mean() if "AMW" in filtered_df.columns and not filtered_df["AMW"].empty else 0.0
    avg_dil = filtered_df["Dilution_Ratio"].mean() if "Dilution_Ratio" in filtered_df.columns and not filtered_df["Dilution_Ratio"].empty else 0.0
    avg_discard = filtered_df["Discard Ratio"].mean() if "Discard Ratio" in filtered_df.columns and not filtered_df["Discard Ratio"].empty else 0.0

    top_well = {'Well_Name': 'N/A', 'ROP': 0.0}
    low_well = {'Well_Name': 'N/A', 'ROP': 0.0}

    if "ROP" in filtered_df.columns and not filtered_df["ROP"].empty:
        # Filter out NaN ROP values before finding min/max
        rop_data = filtered_df.dropna(subset=["ROP"])
        if not rop_data.empty:
            top_well = rop_data.loc[rop_data["ROP"].idxmax()]
            low_well = rop_data.loc[rop_data["ROP"].idxmin()]

    st.markdown(f"""
### 🛠️ Drilling Performance Overview
- Total Wells: **{total_wells}**
- Average ROP: **{avg_rop:.1f} ft/hr**
- Average Mud Weight: **{avg_amw:.2f} ppg**
- Avg Dilution Ratio: **{avg_dil:.2f}**
- Avg Discard Ratio: **{avg_discard:.2f}**

### 🔍 ROP Extremes
- **Fastest Well**: `{top_well['Well_Name']}` @ **{top_well['ROP']:.1f} ft/hr**
- **Slowest Well**: `{low_well['Well_Name']}` @ **{low_well['ROP']:.1f} ft/hr**
""")

    rop_by_operator_bar_chart(filtered_df) # New chart added

    summary_text = (
        f"Executive Summary for {total_wells} wells\n"
        f"Average ROP: {avg_rop:.1f} ft/hr\n"
        f"Average Mud Weight: {avg_amw:.2f} ppg\n"
        f"Average Dilution Ratio: {avg_dil:.2f}\n"
        f"Average Discard Ratio: {avg_discard:.2f}\n"
        f"Fastest Well: {top_well['Well_Name']} @ {top_well['ROP']:.1f} ft/hr\n"
        f"Slowest Well: {low_well['Well_Name']} @ {low_well['ROP']:.1f} ft/hr\n"
    )
    
    st.download_button(
        label="📥 Download Summary",
        data=summary_text.encode('utf-8'), # Encode for download
        file_name="executive_summary.txt",
        mime="text/plain"
    )

