import os
import pandas as pd
import plotly.express as px
import streamlit as strl

# Set up clean browser tab configurations
strl.set_page_config(page_title="Inventory Analytics Dashboard", layout="wide")

# 1. LIVE FILE PATH CONFIGURATION
EXCEL_PATH = "https://docs.google.com/spreadsheets/d/1mbxgLLMNQhp087UDFHu6N_zO5O4f9DkX_Oszm_N7vFs/export?format=xlsx"

strl.title("📦 Inventory Control & Analytics Dashboard")
strl.markdown("---")
strl.title("📦 Inventory Control & Analytics Dashboard")
strl.markdown("---")

# 2. LOAD DATA DIRECTLY FROM GOOGLE SHEETS URL
try:
    df = pd.read_excel(EXCEL_PATH, skiprows=2)
except Exception as e:
    strl.error(f"❌ Error downloading data from Google Sheets: {e}")
    strl.stop()

# 3. CLEAN AND FORMAT DATA
# (Your original code for processing 'df' continues directly below here...)
        
        # FIX: Force any other object/mix columns like RATE or VALUE to text format so they never crash the UI
        for col in df.columns:
            if col not in ['PRODUCT', 'UNITS']:
                df[col] = df[col].astype(str).str.strip().replace(r'^\s*$', '0', regex=True)

        ALERT_THRESHOLD = 10
        
        # 3. HIGH-LEVEL METRIC CARDS
        total_items = len(df)
        total_volume = df['UNITS'].sum()
        low_stock_df = df[df['UNITS'] <= ALERT_THRESHOLD]
        
        col1, col2, col3 = strl.columns(3)
        with col1:
            strl.metric(label="Total Distinct Products", value=f"{total_items} Items")
        with col2:
            strl.metric(label="Total Available Volume", value=f"{total_volume} Units")
        with col3:
            strl.metric(label="Critical Low Stock Alerts", value=f"{len(low_stock_df)} Products")
            
        strl.markdown("---")
        
        # 4. SPLIT LAYOUT: CHART & ALERTS
        left_col, right_col = strl.columns([2, 1])
        
        with left_col:
            strl.subheader("📊 Stock Level Distribution")
            fig = px.bar(df.head(15), x='UNITS', y='PRODUCT', orientation='h', 
                         labels={'UNITS': 'Stock Quantities', 'PRODUCT': 'Product Name'},
                         color='UNITS', color_continuous_scale='Blues')
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, margin=dict(l=0, r=0, t=30, b=0))
            strl.plotly_chart(fig, width='stretch')
            
        with right_col:
            strl.subheader("⚠️ Reorder Flag List")
            if not low_stock_df.empty:
                strl.dataframe(low_stock_df[['PRODUCT', 'UNITS']].sort_values('UNITS'), width='stretch', hide_index=True)
            else:
                strl.success("✅ All product stock levels are healthy!")
                
        strl.markdown("---")
        
        # 5. MASTER SEARCH INTERFACE
        strl.subheader("🔍 Global Inventory Search Ledger")
        search_query = strl.text_input("Type item brand name or size descriptor to filter down immediately:")
        
        if search_query:
            filtered_df = df[df['PRODUCT'].astype(str).str.contains(search_query, case=False, na=False)]
            strl.dataframe(filtered_df, width='stretch')
        else:
            strl.dataframe(df, width='stretch')
            
    else:
        strl.warning("⚠️ Column Check Failed: Ensure your Excel file contains 'PRODUCT' and 'UNITS'.")