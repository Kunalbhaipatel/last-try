# utils.py (Shared Utility Functions)

import streamlit as st
import pandas as pd

def apply_shared_filters(df):
    """
    Applies a set of common filters to the DataFrame based on sidebar selections.

    Args:
        df (pd.DataFrame): The input DataFrame to filter.

    Returns:
        pd.DataFrame: The filtered DataFrame.
    """
    st.sidebar.header("📊 Shared Filters")
    
    # Search functionality across all columns
    search_term = st.sidebar.text_input("🔍 Search Anything", key="search_filter").lower()
    filtered = df.copy()

    if search_term:
        # Apply search across all string-convertible columns
        filtered = filtered[filtered.apply(lambda row: row.astype(str).str.lower().str.contains(search_term).any(), axis=1)]

    # Selectbox filters for categorical columns
    for col in ["Operator", "Contractor", "flowline_Shakers", "Hole_Size"]:
        if col in filtered.columns:
            options = sorted(filtered[col].dropna().astype(str).unique().tolist())
            selected = st.sidebar.selectbox(col, ["All"] + options, key=f"filter_{col}") # Unique key for each selectbox
            if selected != "All":
                filtered = filtered[filtered[col].astype(str) == selected]

    # Date range slider for 'TD_Date'
    if "TD_Date" in filtered.columns and not filtered["TD_Date"].empty:
        filtered["TD_Date"] = pd.to_datetime(filtered["TD_Date"], errors="coerce")
        # Get min/max year from data, or use a default range if data is empty
        min_year = int(filtered["TD_Date"].dt.year.min()) if not filtered["TD_Date"].empty and pd.notna(filtered["TD_Date"].dt.year.min()) else 2020
        max_year = int(filtered["TD_Date"].dt.year.max()) if not filtered["TD_Date"].empty and pd.notna(filtered["TD_Date"].dt.year.max()) else 2026
        
        # Ensure slider range is valid
        if min_year > max_year:
            # Fallback if data years are problematic or single year
            min_year, max_year = 2020, 2026 
            if not filtered["TD_Date"].empty:
                min_year = int(filtered["TD_Date"].dt.year.min())
                max_year = int(filtered["TD_Date"].dt.year.max())
                if min_year == max_year: # If only one year, make range 1 year
                    min_year -= 1
                    max_year += 1

        year_range = st.sidebar.slider("TD Date Range", min_year, max_year, (min_year, max_year), key="filter_td_date")
        filtered = filtered[(filtered["TD_Date"].dt.year >= year_range[0]) & (filtered["TD_Date"].dt.year <= year_range[1])]

    # Depth bin selection for 'MD Depth'
    if "MD Depth" in filtered.columns and not filtered["MD Depth"].empty:
        depth_bins = {
            "<5000 ft": (0, 5000), "5000–10000 ft": (5000, 10000),
            "10000–15000 ft": (10000, 15000), "15000–20000 ft": (15000, 20000),
            "20000–25000 ft": (20000, 25000), ">25000 ft": (25000, float("inf"))
        }
        selected_depth = st.sidebar.selectbox("Depth", ["All"] + list(depth_bins.keys()), key="filter_depth")
        if selected_depth != "All":
            low, high = depth_bins[selected_depth]
            filtered = filtered[(filtered["MD Depth"] >= low) & (filtered["MD Depth"] < high)]

    # Mud Weight bin selection for 'AMW'
    if "AMW" in filtered.columns and not filtered["AMW"].empty:
        mw_bins = {
            "<3": (0, 3), "3–6": (3, 6), "6–9": (6, 9),
            "9–11": (9, 11), "11–14": (11, 14), "14–30": (14, 30)
        }
        selected_mw = st.sidebar.selectbox("Average Mud Weight", ["All"] + list(mw_bins.keys()), key="filter_amw")
        if selected_mw != "All":
            low, high = mw_bins[selected_mw]
            filtered = filtered[(filtered["AMW"] >= low) & (filtered["AMW"] < high)]

    return filtered

