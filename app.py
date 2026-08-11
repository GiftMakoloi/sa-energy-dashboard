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

# --- 1. LIVE LOAD-SHEDDING STATUS (Simple API) ---
st.header("📢 Live Load-shedding Status")

ESKOM_STATUS_URL = "https://loadshedding.eskom.co.za/LoadShedding/GetStatus"

try:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    response = requests.get(ESKOM_STATUS_URL, headers=headers, timeout=10)
    
    if response.status_code == 200:
        raw_status = response.text.strip()
        
        if raw_status == "0":
            stage_display = "No Load-shedding 😊"
            stage_value = "0"
        elif raw_status in ["1", "2", "3", "4", "5", "6", "7", "8"]:
            stage_display = f"Stage {raw_status} ⚠️"
            stage_value = raw_status
        else:
            stage_display = f"Unknown status: {raw_status}"
            stage_value = "Unknown"
        
        last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        col1, col2 = st.columns(2)
        col1.metric("Current Stage", stage_display)
        col2.metric("Last Updated", last_updated)
        
        if stage_value not in ["0", "Unknown"]:
            st.warning(f"⚠️ Load-shedding Stage {stage_value} is currently active. Plan accordingly.")
        else:
            st.success("✅ No load-shedding currently reported.")
    else:
        st.error(f"⚠️ Could not fetch load-shedding status. API returned status code: {response.status_code}")

except Exception as e:
    st.warning(f"⚠️ Could not fetch load-shedding data: {e}")

st.markdown("---")

# --- 2. SUBURB SCHEDULE LOOKUP (Using Eskom API Structure) ---
st.header("🔍 Load-Shedding Schedule Lookup")
st.caption("Find out when your area will be affected by load-shedding.")

# --- Province Selection (Static Keys) ---
provinces = {
    "1": "Eastern Cape",
    "2": "Free State",
    "3": "Gauteng",
    "4": "KwaZulu-Natal",
    "5": "Limpopo",
    "6": "Mpumalanga",
    "7": "North West",
    "8": "Northern Cape",
    "9": "Western Cape"
}

# --- Municipalities for Gauteng (Province ID: 3) ---
# In a real implementation, you would fetch this dynamically from the API
gauteng_municipalities = {
    "306": "City of Johannesburg (Eskom-supplied zones)",
    "307": "City of Tshwane (Eskom-supplied zones)",
    "305": "Ekurhuleni Metropolitan Municipality",
    "304": "Emfuleni Local Municipality",
    "308": "Lesedi Local Municipality",
    "309": "Mogale City Local Municipality",
    "310": "Merafong City Local Municipality",
    "311": "Rand West City Local Municipality"
}

# --- Build the lookup interface ---
col1, col2, col3 = st.columns(3)

with col1:
    selected_province_key = st.selectbox(
        "Select Province",
        options=list(provinces.keys()),
        format_func=lambda x: provinces[x]
    )
    st.caption(f"Province ID: {selected_province_key}")

with col2:
    # For now, only Gauteng has municipality data. This will expand later.
    if selected_province_key == "3":
        selected_municipality_key = st.selectbox(
            "Select Municipality",
            options=list(gauteng_municipalities.keys()),
            format_func=lambda x: gauteng_municipalities[x]
        )
        st.caption(f"Municipality ID: {selected_municipality_key}")
    else:
        st.selectbox(
            "Select Municipality",
            options=["Data not yet available for this province"],
            disabled=True
        )
        selected_municipality_key = None

with col3:
    # Placeholder for suburb selection
    if selected_municipality_key:
        # In a real implementation, you would fetch suburbs from the API
        # using the municipality ID
        st.text_input(
            "Enter Suburb Name (e.g., Sandton, Soweto, Midrand)",
            placeholder="Type suburb name..."
        )
    else:
        st.text_input(
            "Enter Suburb Name",
            placeholder="Select a province and municipality first",
            disabled=True
        )

st.caption("ℹ️ Note: This is a demonstration of the API structure. A full implementation would include dynamic fetching of municipalities and suburbs from Eskom's servers.")

st.markdown("---")

# --- 3. ENERGY GENERATION MIX (Static Data) ---
st.header("📊 South Africa Energy Generation Mix")
st.caption("Data source: Eskom (2023/2024 annual report - approximate values)")

data = {
    "Source": ["Coal", "Renewables", "Nuclear", "Gas/Diesel", "Other"],
    "Percentage": [70, 15, 8, 5, 2]
}
df = pd.DataFrame(data)

col1, col2 = st.columns([2, 1])
with col1:
    st.bar_chart(df.set_index("Source"))
with col2:
    st.dataframe(df, hide_index=True)

st.markdown("---")

# --- 4. FUTURE FEATURES ---
st.header("🔮 Features in Development")
st.write("""
- **Dynamic Municipality Fetching:** Automatically load municipalities based on the selected province.
- **Suburb Search:** Type a suburb name and get its specific load-shedding schedule.
- **Historical Trends:** View load-shedding patterns over the past month.
- **Financial Impact Calculator:** Estimate the cost of load-shedding for your business.
- **Notification Alerts:** Get reminded when your area is about to be affected.
""")

st.markdown("---")
st.caption("Built with ❤️ using Streamlit and Python by Gift Makoloi")
