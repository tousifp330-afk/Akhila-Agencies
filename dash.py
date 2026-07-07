import os
import pandas as pd
import plotly.express as px
import streamlit as strl

# 1. LIVE FILE CONFIGURATION (YOUR VERIFIED GOOGLE SHEETS LINK)
EXCEL_PATH = "https://docs.google.com/spreadsheets/d/1mbxgLLMNQhp087UDFHu0jQitrtfS_QGDfcCmDAd0HHw/export?format=xlsx"

# Set up clean browser tab configurations
strl.set_page_config(page_title="Inventory Analytics Dashboard", layout="wide")

strl.title("📦 Inventory Control & Analytics Dashboard")
strl.markdown("---")

# 2. LOAD DATA DIRECTLY FROM GOOGLE SHEETS URL
try:
    # Read from the very top of the sheet without skipping rows
    df = pd.read_excel(EXCEL_PATH)
except Exception as e:
    strl.error(f"❌ Error downloading data from Google Sheets: {e}")
    strl.stop()

# 3. AUTOMATICALLY CLEAN HEADERS AND DATA ROWS
# Clear out entirely empty spacer rows or columns
df.dropna(how='all', inplace=True)

# Trim spaces from current column names
df.columns = [str(c).strip() for c in df.columns]

# Backup check: If the real headers are stuck in the first row of data, pull them up
if 'Product' not in df.columns and len(df) > 0:
    df.columns = [str(x).strip() for x in df.iloc[0]]
    df = df[1:]

# Standardize data strings across all columns to clear formatting bugs
for col in df.columns:
    df[col] = df[col].astype(str).str.strip()

# Safely force vital numerical columns to behave as real math numbers
numeric_cols = ['Closing Stock', 'Value', 'Rate']
for c in numeric_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c].str.replace(',', ''), errors='coerce').fillna(0)

# 4. SIDEBAR FILTRATION CONTROLS
strl.sidebar.header("Filter Configuration")

product_filter = strl.sidebar.multiselect(
    "Select Products:",
    options=sorted(df['Product'].unique()) if 'Product' in df.columns else [],
    default=[]
)

# Apply dynamic filtering
filtered_df = df.copy()
if product_filter:
    filtered_df = filtered_df[filtered_df['Product'].isin(product_filter)]

# 5. CORE KPI HIGHLIGHT CARDS
total_items = len(filtered_df)
total_value = filtered_df['Value'].sum() if 'Value' in filtered_df.columns else 0.0

kpi1, kpi2 = strl.columns(2)
with kpi1:
    strl.metric(label="Total Unique Tracked Lines", value=f"{total_items:,}")
with kpi2:
    strl.metric(label="Total Inventory Assets Value", value=f"₹{total_value:,.2f}")

strl.markdown("---")

# 6. GRAPHICAL REPRESENTATION
strl.subheader("Visual Analytics Ledger")
if 'Product' in filtered_df.columns and 'Value' in filtered_df.columns and not filtered_df.empty:
    fig = px.bar(
        filtered_df.sort_values(by='Value', ascending=False).head(15),
        x='Product',
        y='Value',
        title="Top 15 High-Value Stock Commodities Valuation",
        labels={'Value': 'Asset Valuation (INR)', 'Product': 'Stock Item Name'},
        template="plotly_white",
        color='Value',
        color_continuous_scale=px.colors.sequential.Blues
    )
    strl.plotly_chart(fig, use_container_width=True)
else:
    strl.info("Select specific product filters on the left panel to populate charts.")

# 7. COMPREHENSIVE DATA GRID INDEX
strl.subheader("Complete Live Stock Ledger Reference Table")
strl.dataframe(filtered_df, use_container_width=True)