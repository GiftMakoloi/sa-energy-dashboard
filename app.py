import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="SA Energy Dashboard",
    page_icon="⚡",
    layout="wide"
)

# --- Title ---
st.title("⚡ South African Energy Dashboard")
st.caption("Built by Gift Makoloi | MSc Financial Engineering Candidate")
st.markdown("---")

# --- 1. FETCH LIVE LOAD-SHEDDING STATUS ---
st.header("📢 Live Load-shedding Status")

# Using a public, free API for Eskom load-shedding
# Source: https://developer.eskom.co.za/ (using a free, community-maintained endpoint for demo)
try:
    # This is a sample public endpoint. In a real scenario, you might use a more official API.
    # For this example, we'll simulate a fetch. A real API call would look like:
    # response = requests.get("https://api.example.com/eskom/status")
    # data = response.json()
    
    # For demonstration, we'll create a placeholder. 
    # You can replace this with a real API endpoint later.
    st.info("ℹ️ This section demonstrates the concept. Replace the `api_url` with a real Eskom API endpoint.")
    
    # Simulated data for demonstration
    load_shedding_stage = "Stage 4"
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    col1, col2 = st.columns(2)
    col1.metric("Current Stage", load_shedding_stage)
    col2.metric("Last Updated", last_updated)
    
except Exception as e:
    st.error(f"Could not fetch load-shedding data: {e}")

st.markdown("---")

# --- 2. ENERGY DATA VISUALIZATION ---
st.header("📊 Energy Generation Mix")
st.caption("Sample data for demonstration. Replace with live data from an energy API.")

# Sample data for the energy mix
data = {
    "Source": ["Coal", "Renewables", "Nuclear", "Gas", "Other"],
    "Percentage": [70, 15, 8, 5, 2]
}
df = pd.DataFrame(data)

# Display a bar chart
st.bar_chart(df.set_index("Source"))

# Display a table
st.subheader("Data Table")
st.dataframe(df)

st.markdown("---")

# --- 3. ADDITIONAL FEATURES (Placeholder) ---
st.header("🔮 Future Features")
st.write("""
- **Historical Trends:** View load-shedding patterns over the past month.
- **Cost Analysis:** Estimate the financial impact of load-shedding on businesses.
- **Renewable Energy Tracker:** Monitor solar and wind energy production.
""")

st.caption("Built with ❤️ using Streamlit and Python.")
