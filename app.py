import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ============================================================
# SA ENERGY MARKET & GRID RISK INTELLIGENCE PLATFORM
# ============================================================

st.set_page_config(
    page_title="SA Energy Market & Grid Risk",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ SA Energy Market & Grid Risk Intelligence")
st.caption(
    "Built by Gift Makoloi | MSc Financial Engineering Candidate | "
    "Energy Analytics • Monte Carlo • Risk Modelling"
)

st.markdown("---")

st.info(
    "Educational quantitative-energy model. "
    "The simulated outputs are not official Eskom forecasts."
)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ Model Configuration")

simulation_years = st.sidebar.slider(
    "Forecast Horizon (Years)",
    1,
    10,
    5
)

num_simulations = st.sidebar.selectbox(
    "Monte Carlo Simulations",
    [500, 1000, 2500, 5000],
    index=1
)

seed = st.sidebar.number_input(
    "Simulation Seed",
    1,
    999999,
    42
)

st.sidebar.markdown("---")

st.sidebar.header("🏭 Grid Assumptions")

base_demand = st.sidebar.number_input(
    "Current Annual Electricity Demand (GWh)",
    min_value=1000,
    max_value=500000,
    value=220000,
    step=1000
)

demand_growth = (
    st.sidebar.slider(
        "Annual Demand Growth (%)",
        0.0,
        10.0,
        2.0,
        0.5
    ) / 100
)

coal_share = (
    st.sidebar.slider(
        "Coal Generation Share (%)",
        30.0,
        90.0,
        70.0,
        1.0
    ) / 100
)

renewable_share = (
    st.sidebar.slider(
        "Renewable Generation Share (%)",
        5.0,
        60.0,
        20.0,
        1.0
    ) / 100
)

generation_volatility = (
    st.sidebar.slider(
        "Generation Volatility (%)",
        2.0,
        30.0,
        10.0,
        1.0
    ) / 100
)

st.sidebar.markdown("---")

st.sidebar.header("💰 Electricity Economics")

current_tariff = st.sidebar.number_input(
    "Current Electricity Tariff (R/kWh)",
    min_value=0.10,
    max_value=10.00,
    value=2.50,
    step=0.05
)

tariff_growth = (
    st.sidebar.slider(
        "Expected Tariff Growth (%)",
        0.0,
        20.0,
        8.0,
        0.5
    ) / 100
)

tariff_volatility = (
    st.sidebar.slider(
        "Tariff Volatility (%)",
        1.0,
        30.0,
        8.0,
        1.0
    ) / 100
)

st.sidebar.markdown("---")

st.sidebar.header("🏢 Business Exposure")

monthly_consumption = st.sidebar.number_input(
    "Monthly Electricity Consumption (kWh)",
    min_value=100,
    max_value=10_000_000,
    value=20_000,
    step=100
)

backup_cost = st.sidebar.number_input(
    "Backup Generation Cost (R/kWh)",
    min_value=0.0,
    max_value=20.0,
    value=4.50,
    step=0.10
)

# ============================================================
# GENERATE HISTORICAL-STYLE ENERGY DATA
# ============================================================

rng = np.random.default_rng(seed)

days = 365

dates = pd.date_range(
    end=datetime.now(),
    periods=days,
    freq="D"
)

# Seasonal demand pattern
seasonality = (
    1
    + 0.08 * np.sin(
        np.arange(days) * 2 * np.pi / 365
    )
)

random_demand = rng.normal(
    0,
    0.025,
    days
)

demand = (
    base_demand / 365
    * seasonality
    * (1 + random_demand)
)

# Renewable generation
renewable_output = (
    renewable_share
    * demand
    * (
        1
        + rng.normal(
            0,
            generation_volatility,
            days
        )
    )
)

renewable_output = np.maximum(
    renewable_output,
    0
)

# Coal generation
coal_output = (
    coal_share
    * demand
    * (
        1
        + rng.normal(
            0,
            generation_volatility / 2,
            days
        )
    )
)

coal_output = np.maximum(
    coal_output,
    0
)

# Other generation
other_output = np.maximum(
    demand
    - renewable_output
    - coal_output,
    0
)

energy_df = pd.DataFrame({
    "Date": dates,
    "Demand (GWh)": demand,
    "Coal (GWh)": coal_output,
    "Renewables (GWh)": renewable_output,
    "Other (GWh)": other_output
})

# ============================================================
# GRID RISK MODEL
# ============================================================

energy_df["Available Generation"] = (
    energy_df[
        [
            "Coal (GWh)",
            "Renewables (GWh)",
            "Other (GWh)"
        ]
    ].sum(axis=1)
)

energy_df["Reserve Margin"] = (
    (
        energy_df["Available Generation"]
        - energy_df["Demand (GWh)"]
    )
    / energy_df["Demand (GWh)"]
)

# Risk score
energy_df["Grid Risk Score"] = np.clip(
    100
    - energy_df["Reserve Margin"] * 100,
    0,
    100
)

# ============================================================
# DASHBOARD METRICS
# ============================================================

st.header("📊 Grid Health Dashboard")

latest = energy_df.iloc[-1]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Estimated Demand",
        f"{latest['Demand (GWh)']:,.0f} GWh"
    )

with col2:
    st.metric(
        "Available Generation",
        f"{latest['Available Generation']:,.0f} GWh"
    )

with col3:
    st.metric(
        "Reserve Margin",
        f"{latest['Reserve Margin'] * 100:.1f}%"
    )

with col4:

    risk = latest["Grid Risk Score"]

    if risk < 30:
        label = "LOW"
    elif risk < 60:
        label = "MODERATE"
    else:
        label = "HIGH"

    st.metric(
        "Grid Risk",
        label,
        f"{risk:.1f}/100"
    )

# ============================================================
# GENERATION MIX
# ============================================================

st.markdown("---")

st.header("⚡ Estimated Generation Mix")

generation_totals = pd.DataFrame({
    "Source": [
        "Coal",
        "Renewables",
        "Other"
    ],
    "Generation": [
        energy_df["Coal (GWh)"].sum(),
        energy_df["Renewables (GWh)"].sum(),
        energy_df["Other (GWh)"].sum()
    ]
})

fig_mix = px.pie(
    generation_totals,
    names="Source",
    values="Generation",
    title="Estimated Electricity Generation Mix"
)

st.plotly_chart(
    fig_mix,
    use_container_width=True
)

# ============================================================
# DEMAND VS GENERATION
# ============================================================

st.header("📈 Demand vs Available Generation")

fig_generation = go.Figure()

fig_generation.add_trace(
    go.Scatter(
        x=energy_df["Date"],
        y=energy_df["Demand (GWh)"],
        name="Demand"
    )
)

fig_generation.add_trace(
    go.Scatter(
        x=energy_df["Date"],
        y=energy_df["Available Generation"],
        name="Available Generation"
    )
)

fig_generation.update_layout(
    height=500,
    title="Electricity Supply-Demand Relationship",
    yaxis_title="GWh"
)

st.plotly_chart(
    fig_generation,
    use_container_width=True
)

# ============================================================
# RENEWABLE VARIABILITY
# ============================================================

st.header("☀️ Renewable Energy Variability")

fig_renewables = px.line(
    energy_df,
    x="Date",
    y="Renewables (GWh)",
    title="Simulated Renewable Generation"
)

fig_renewables.update_layout(
    height=450
)

st.plotly_chart(
    fig_renewables,
    use_container_width=True
)

# ============================================================
# GRID RISK
# ============================================================

st.header("🚨 Grid Risk Indicator")

fig_risk = px.line(
    energy_df,
    x="Date",
    y="Grid Risk Score",
    title="Estimated Grid Stress / Risk Score"
)

fig_risk.add_hline(
    y=60,
    line_dash="dash",
    annotation_text="High Risk Threshold"
)

fig_risk.update_layout(
    height=450,
    yaxis_range=[0, 100]
)

st.plotly_chart(
    fig_risk,
    use_container_width=True
)

# ============================================================
# MONTE CARLO ENERGY FORECAST
# ============================================================

st.markdown("---")

st.header("🎲 Monte Carlo Energy Market Forecast")

forecast_results = []

for simulation in range(num_simulations):

    simulated_demand = base_demand
    simulated_tariff = current_tariff

    total_cost = 0
    shortage_days = 0

    for year in range(simulation_years):

        demand_shock = rng.normal(
            demand_growth,
            0.015
        )

        tariff_shock = rng.normal(
            tariff_growth,
            tariff_volatility
        )

        simulated_demand *= (
            1 + demand_shock
        )

        simulated_tariff *= (
            1 + tariff_shock
        )

        annual_consumption = (
            monthly_consumption
            * 12
            * (
                simulated_demand
                / base_demand
            )
        )

        electricity_cost = (
            annual_consumption
            * simulated_tariff
        )

        # Estimate shortage probability
        reserve_margin = (
            renewable_share
            * (
                1
                + rng.normal(
                    0,
                    generation_volatility
                )
            )
            + coal_share
            - 0.90
        )

        if reserve_margin < 0:
            shortage_days += 30

            backup_expense = (
                annual_consumption
                * 0.10
                * backup_cost
            )

            electricity_cost += backup_expense

        total_cost += electricity_cost

    forecast_results.append({
        "Simulation": simulation + 1,
        "Total Energy Cost": total_cost,
        "Final Tariff": simulated_tariff,
        "Shortage Days": shortage_days,
        "Final Demand": simulated_demand
    })

forecast_df = pd.DataFrame(
    forecast_results
)

# ============================================================
# MONTE CARLO METRICS
# ============================================================

cost_median = forecast_df[
    "Total Energy Cost"
].median()

cost_p10 = np.percentile(
    forecast_df["Total Energy Cost"],
    10
)

cost_p90 = np.percentile(
    forecast_df["Total Energy Cost"],
    90
)

shortage_probability = np.mean(
    forecast_df["Shortage Days"] > 0
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Median Energy Cost",
        f"R{cost_median:,.0f}"
    )

with col2:
    st.metric(
        "10th Percentile",
        f"R{cost_p10:,.0f}"
    )

with col3:
    st.metric(
        "90th Percentile",
        f"R{cost_p90:,.0f}"
    )

with col4:
    st.metric(
        "Shortage Probability",
        f"{shortage_probability * 100:.1f}%"
    )

# ============================================================
# COST DISTRIBUTION
# ============================================================

st.subheader("💰 Distribution of Future Energy Costs")

fig_cost = px.histogram(
    forecast_df,
    x="Total Energy Cost",
    nbins=60,
    title="Monte Carlo Distribution of Cumulative Energy Costs"
)

fig_cost.add_vline(
    x=cost_median,
    line_dash="dash",
    annotation_text="Median"
)

fig_cost.update_layout(
    height=500,
    xaxis_title="Cumulative Electricity Cost (R)"
)

st.plotly_chart(
    fig_cost,
    use_container_width=True
)

# ============================================================
# TARIFF FORECAST
# ============================================================

st.subheader("📊 Future Electricity Tariff Distribution")

fig_tariff = px.histogram(
    forecast_df,
    x="Final Tariff",
    nbins=50,
    title="Simulated Electricity Tariff at Forecast Horizon"
)

fig_tariff.update_layout(
    height=450,
    xaxis_title="Final Tariff (R/kWh)"
)

st.plotly_chart(
    fig_tariff,
    use_container_width=True
)

# ============================================================
# RISK ANALYSIS
# ============================================================

st.header("📉 Energy Financial Risk")

var_95 = np.percentile(
    forecast_df["Total Energy Cost"],
    95
)

expected_shortfall = forecast_df[
    forecast_df["Total Energy Cost"] >= var_95
]["Total Energy Cost"].mean()

risk_col1, risk_col2, risk_col3 = st.columns(3)

with risk_col1:
    st.metric(
        "95% Cost VaR",
        f"R{var_95:,.0f}"
    )

with risk_col2:
    st.metric(
        "Expected Shortfall",
        f"R{expected_shortfall:,.0f}"
    )

with risk_col3:
    st.metric(
        "Cost Volatility",
        f"R{forecast_df['Total Energy Cost'].std():,.0f}"
    )

st.write(
    """
**Value-at-Risk (VaR)** estimates the energy-cost level that is
exceeded in approximately 5% of simulated scenarios.

**Expected Shortfall** estimates the average cost within those
extreme 5% scenarios.

These metrics connect the electricity problem directly to
quantitative financial risk management.
"""
)

# ============================================================
# ENERGY COST SENSITIVITY
# ============================================================

st.header("🔬 Energy Cost Sensitivity")

sensitivity_values = []

tariff_scenarios = [
    -0.20,
    -0.10,
    0,
    0.10,
    0.20,
    0.30
]

for change in tariff_scenarios:

    scenario_tariff = (
        current_tariff
        * (1 + change)
    )

    annual_cost = (
        monthly_consumption
        * 12
        * scenario_tariff
    )

    sensitivity_values.append({
        "Tariff Change": change,
        "Tariff": scenario_tariff,
        "Annual Cost": annual_cost
    })

sensitivity_df = pd.DataFrame(
    sensitivity_values
)

fig_sensitivity = px.line(
    sensitivity_df,
    x="Tariff Change",
    y="Annual Cost",
    markers=True,
    title="Annual Electricity Cost Sensitivity to Tariff Changes"
)

fig_sensitivity.update_layout(
    height=450,
    xaxis_tickformat=".0%",
    yaxis_title="Annual Electricity Cost (R)"
)

st.plotly_chart(
    fig_sensitivity,
    use_container_width=True
)

# ============================================================
# BUSINESS DECISION SUPPORT
# ============================================================

st.markdown("---")

st.header("🧠 Financial Engineering Interpretation")

if shortage_probability < 0.20:

    risk_message = (
        "The simulated probability of a supply-shortage scenario "
        "is relatively low under the selected assumptions."
    )

elif shortage_probability < 0.50:

    risk_message = (
        "The model indicates a moderate probability of supply "
        "stress. Energy resilience measures may deserve further "
        "financial evaluation."
    )

else:

    risk_message = (
        "The model indicates a high probability of supply stress "
        "under the selected assumptions."
    )

st.success(
    f"""
### Energy Risk Assessment

{risk_message}

**Median cumulative energy cost:**
R{cost_median:,.0f}

**95% cost VaR:**
R{var_95:,.0f}

**Expected Shortfall:**
R{expected_shortfall:,.0f}

**Estimated shortage probability:**
{shortage_probability * 100:.1f}%

The model demonstrates how electricity-system uncertainty can
be transformed into measurable financial risk.
"""
)

# ============================================================
# PROJECT LIMITATIONS
# ============================================================

with st.expander("📚 Model Assumptions & Limitations"):

    st.markdown(
        """
### Current model

This application is a quantitative energy-risk prototype.

It demonstrates:

- stochastic electricity demand
- renewable generation variability
- supply-demand analysis
- reserve-margin modelling
- grid-risk scoring
- electricity tariff uncertainty
- Monte Carlo simulation
- Value-at-Risk
- Expected Shortfall
- sensitivity analysis
- business electricity-cost exposure

### Important limitations

The simulated generation and demand data are NOT official
Eskom measurements.

A production version should connect to verified sources such as:

- Eskom
- NERSA
- South African government energy datasets
- municipal electricity data
- reputable electricity-market data providers

The model also does not currently model:

- individual power-station outages
- transmission constraints
- battery dispatch optimisation
- weather forecasts
- electricity-market clearing prices
- exact municipal tariffs
- load profiles by sector
- wheeling agreements
- embedded generation
- rooftop solar
- battery degradation
- ancillary services
- detailed Eskom system constraints
        """
    )

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "Built with Python • Streamlit • Pandas • NumPy • Plotly • "
    "Monte Carlo Simulation • Energy Risk Analytics"
)

st.caption(
    "SA Energy Market & Grid Risk Intelligence Platform"
)
