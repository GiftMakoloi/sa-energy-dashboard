import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ============================================================
# SA ENERGY MARKET & GRID RISK INTELLIGENCE PLATFORM
# ============================================================

st.set_page_config(
    page_title="SA Energy Market & Grid Risk",
    page_icon="⚡",
    layout="wide"
)

# ============================================================
# HEADER / PROFESSIONAL BRANDING
# ============================================================

st.title("⚡ SA Energy Market & Grid Risk Intelligence")

st.caption(
    "Built by Gift Makoloi | DevOps Engineer • Software Engineer • "
    "AI Product Manager • Digital Social Scientist"
)

st.caption("📧 giftmakoloi@gmail.com")

st.markdown("---")

st.info(
    "⚠️ Educational quantitative-energy model. "
    "The simulated outputs are not official Eskom forecasts, "
    "electricity-market prices, or financial advice."
)

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ Model Configuration")

simulation_years = st.sidebar.slider(
    "Forecast Horizon (Years)",
    min_value=1,
    max_value=10,
    value=5
)

num_simulations = st.sidebar.selectbox(
    "Monte Carlo Simulations",
    [500, 1000, 2500, 5000],
    index=1
)

seed = st.sidebar.number_input(
    "Simulation Seed",
    min_value=1,
    max_value=999999,
    value=42,
    step=1
)

st.sidebar.markdown("---")

# ============================================================
# GRID ASSUMPTIONS
# ============================================================

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
        min_value=0.0,
        max_value=10.0,
        value=2.0,
        step=0.5
    ) / 100
)

coal_share = (
    st.sidebar.slider(
        "Coal Generation Share (%)",
        min_value=30.0,
        max_value=90.0,
        value=70.0,
        step=1.0
    ) / 100
)

renewable_share = (
    st.sidebar.slider(
        "Renewable Generation Share (%)",
        min_value=5.0,
        max_value=60.0,
        value=20.0,
        step=1.0
    ) / 100
)

generation_volatility = (
    st.sidebar.slider(
        "Generation Volatility (%)",
        min_value=2.0,
        max_value=30.0,
        value=10.0,
        step=1.0
    ) / 100
)

st.sidebar.markdown("---")

# ============================================================
# ELECTRICITY ECONOMICS
# ============================================================

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
        min_value=0.0,
        max_value=20.0,
        value=8.0,
        step=0.5
    ) / 100
)

tariff_volatility = (
    st.sidebar.slider(
        "Tariff Volatility (%)",
        min_value=1.0,
        max_value=30.0,
        value=8.0,
        step=1.0
    ) / 100
)

st.sidebar.markdown("---")

# ============================================================
# BUSINESS ENERGY EXPOSURE
# ============================================================

st.sidebar.header("🏢 Business Energy Exposure")

monthly_consumption = st.sidebar.number_input(
    "Monthly Electricity Consumption (kWh)",
    min_value=100,
    max_value=10000000,
    value=20000,
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
# RANDOM NUMBER GENERATOR
# ============================================================

rng = np.random.default_rng(seed)

# ============================================================
# GENERATE ENERGY DATA
# ============================================================

days = 365

dates = pd.date_range(
    end=datetime.now(),
    periods=days,
    freq="D"
)

# Seasonal electricity-demand pattern

seasonality = (
    1
    + 0.08
    * np.sin(
        np.arange(days)
        * 2
        * np.pi
        / 365
    )
)

random_demand = rng.normal(
    0,
    0.025,
    days
)

demand = (
    base_demand
    / 365
    * seasonality
    * (1 + random_demand)
)

demand = np.maximum(
    demand,
    0
)

# ============================================================
# RENEWABLE GENERATION
# ============================================================

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

# ============================================================
# COAL GENERATION
# ============================================================

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

# ============================================================
# OTHER GENERATION
# ============================================================

other_output = np.maximum(
    demand
    - renewable_output
    - coal_output,
    0
)

# ============================================================
# DATAFRAME
# ============================================================

energy_df = pd.DataFrame(
    {
        "Date": dates,
        "Demand (GWh)": demand,
        "Coal (GWh)": coal_output,
        "Renewables (GWh)": renewable_output,
        "Other (GWh)": other_output
    }
)

# ============================================================
# GRID HEALTH MODEL
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

# Grid risk score
energy_df["Grid Risk Score"] = np.clip(
    100
    - energy_df["Reserve Margin"] * 100,
    0,
    100
)

# ============================================================
# GRID HEALTH DASHBOARD
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
        risk_label = "LOW"
    elif risk < 60:
        risk_label = "MODERATE"
    else:
        risk_label = "HIGH"

    st.metric(
        "Grid Risk",
        risk_label,
        f"{risk:.1f}/100"
    )

# ============================================================
# GENERATION MIX
# ============================================================

st.markdown("---")

st.header("⚡ Estimated Generation Mix")

generation_totals = pd.DataFrame(
    {
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
    }
)

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
        name="Demand",
        mode="lines"
    )
)

fig_generation.add_trace(
    go.Scatter(
        x=energy_df["Date"],
        y=energy_df["Available Generation"],
        name="Available Generation",
        mode="lines"
    )
)

fig_generation.update_layout(
    height=500,
    title="Electricity Supply-Demand Relationship",
    xaxis_title="Date",
    yaxis_title="Energy (GWh)",
    hovermode="x unified"
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
    height=450,
    xaxis_title="Date",
    yaxis_title="Renewable Generation (GWh)"
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

fig_risk.add_hline(
    y=30,
    line_dash="dot",
    annotation_text="Moderate Risk Threshold"
)

fig_risk.update_layout(
    height=450,
    yaxis_title="Risk Score",
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

    total_cost = 0.0
    shortage_days = 0

    for year in range(simulation_years):

        # Demand uncertainty

        demand_shock = rng.normal(
            demand_growth,
            0.015
        )

        simulated_demand *= (
            1 + demand_shock
        )

        # Tariff uncertainty

        tariff_shock = rng.normal(
            tariff_growth,
            tariff_volatility
        )

        simulated_tariff *= (
            1 + tariff_shock
        )

        # Business consumption exposure

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

        # ----------------------------------------------------
        # Grid shortage simulation
        # ----------------------------------------------------

        simulated_generation = (
            coal_share
            + renewable_share
            + rng.normal(
                0,
                generation_volatility
            )
        )

        reserve_margin = (
            simulated_generation
            - 0.90
        )

        if reserve_margin < 0:

            shortage_days += 30

            backup_expense = (
                annual_consumption
                * 0.10
                * backup_cost
            )

            electricity_cost += (
                backup_expense
            )

        total_cost += electricity_cost

    forecast_results.append(
        {
            "Simulation": simulation + 1,
            "Total Energy Cost": total_cost,
            "Final Tariff": simulated_tariff,
            "Shortage Days": shortage_days,
            "Final Demand": simulated_demand
        }
    )

forecast_df = pd.DataFrame(
    forecast_results
)

# ============================================================
# MONTE CARLO STATISTICS
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

# ============================================================
# ENERGY COST METRICS
# ============================================================

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
# ENERGY COST DISTRIBUTION
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
    xaxis_title="Cumulative Electricity Cost (R)",
    yaxis_title="Number of Simulations"
)

st.plotly_chart(
    fig_cost,
    use_container_width=True
)

# ============================================================
# TARIFF DISTRIBUTION
# ============================================================

st.subheader("📊 Future Electricity Tariff Distribution")

fig_tariff = px.histogram(
    forecast_df,
    x="Final Tariff",
    nbins=50,
    title="Simulated Electricity Tariff at Forecast Horizon"
)

fig_tariff.add_vline(
    x=np.median(forecast_df["Final Tariff"]),
    line_dash="dash",
    annotation_text="Median Tariff"
)

fig_tariff.update_layout(
    height=450,
    xaxis_title="Final Tariff (R/kWh)",
    yaxis_title="Number of Simulations"
)

st.plotly_chart(
    fig_tariff,
    use_container_width=True
)

# ============================================================
# QUANTITATIVE ENERGY RISK
# ============================================================

st.header("📉 Energy Financial Risk")

var_95 = np.percentile(
    forecast_df["Total Energy Cost"],
    95
)

tail_scenarios = forecast_df[
    forecast_df["Total Energy Cost"] >= var_95
]

expected_shortfall = (
    tail_scenarios["Total Energy Cost"].mean()
)

cost_volatility = (
    forecast_df["Total Energy Cost"].std()
)

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
        f"R{cost_volatility:,.0f}"
    )

st.write(
    """
**Value-at-Risk (VaR)** estimates the energy-cost level that
is exceeded in approximately 5% of simulated scenarios.

**Expected Shortfall (ES)** estimates the average cost within
those extreme 5% scenarios.

These measures connect electricity-system uncertainty to
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
    0.00,
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

    sensitivity_values.append(
        {
            "Tariff Change": change,
            "Tariff": scenario_tariff,
            "Annual Cost": annual_cost
        }
    )

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
    xaxis_title="Tariff Change",
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

st.header("🧠 Energy Risk Assessment")

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

**95% Cost VaR:**
R{var_95:,.0f}

**Expected Shortfall:**
R{expected_shortfall:,.0f}

**Estimated shortage probability:**
{shortage_probability * 100:.1f}%

The model transforms electricity-system uncertainty into
measurable financial risk.
"""
)

# ============================================================
# KEY INSIGHTS
# ============================================================

st.header("💡 Key Model Insights")

insight_col1, insight_col2 = st.columns(2)

with insight_col1:

    st.markdown(
        f"""
### ⚡ Grid

- Estimated demand: **{latest['Demand (GWh)']:,.0f} GWh**
- Available generation: **{latest['Available Generation']:,.0f} GWh**
- Reserve margin: **{latest['Reserve Margin'] * 100:.1f}%**
- Grid risk score: **{latest['Grid Risk Score']:.1f}/100**
"""
    )

with insight_col2:

    st.markdown(
        f"""
### 💰 Financial Risk

- Median projected energy cost: **R{cost_median:,.0f}**
- 95% Cost VaR: **R{var_95:,.0f}**
- Expected Shortfall: **R{expected_shortfall:,.0f}**
- Shortage probability: **{shortage_probability * 100:.1f}%**
"""
    )

# ============================================================
# MODEL ASSUMPTIONS
# ============================================================

st.markdown("---")

with st.expander("📚 Model Assumptions & Limitations"):

    st.markdown(
        """
### Current model

This application is a quantitative energy-risk prototype.

It demonstrates:

- Stochastic electricity demand
- Renewable generation variability
- Supply-demand analysis
- Reserve-margin modelling
- Grid-risk scoring
- Electricity tariff uncertainty
- Monte Carlo simulation
- Value-at-Risk
- Expected Shortfall
- Sensitivity analysis
- Business electricity-cost exposure

### Important limitations

The simulated generation and demand data are **not official
Eskom measurements**.

A production version should connect to verified sources such as:

- Eskom
- NERSA
- South African government energy datasets
- Municipal electricity data
- Reputable electricity-market data providers

The current model does not fully model:

- Individual power-station outages
- Transmission constraints
- Battery dispatch optimisation
- Weather forecasts
- Electricity-market clearing prices
- Exact municipal tariffs
- Sector-specific load profiles
- Wheeling agreements
- Embedded generation
- Rooftop solar
- Battery degradation
- Ancillary services
- Detailed Eskom system constraints

Therefore, results should be interpreted as **scenario estimates**
rather than official forecasts.
"""
    )

# ============================================================
# TECHNICAL MODEL
# ============================================================

with st.expander("🔬 Technical Model Details"):

    st.markdown(
        """
### Monte Carlo Simulation

The model generates thousands of possible future energy-market
scenarios.

Each scenario contains uncertainty in:

1. Electricity demand
2. Electricity tariffs
3. Renewable generation
4. Grid reserve conditions
5. Backup-generation requirements

### Value-at-Risk

The 95% Cost VaR is calculated as the 95th percentile of the
simulated cumulative energy-cost distribution.

### Expected Shortfall

Expected Shortfall is calculated as the mean cost of simulations
above the 95% VaR threshold.

### Reserve Margin

The simplified reserve margin is:

Reserve Margin =
(Available Generation - Demand) / Demand

### Grid Risk Score

The dashboard converts reserve conditions into a simplified
0–100 risk score.

Higher values indicate greater simulated grid stress.
"""
    )

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "⚡ SA Energy Market & Grid Risk Intelligence Platform"
)

st.caption(
    "Built with Python • Streamlit • Pandas • NumPy • Plotly • "
    "Monte Carlo Simulation • Energy Risk Analytics"
)

st.caption(
    "Built by Gift Makoloi | DevOps Engineer • Software Engineer • "
    "AI Product Manager • Digital Social Scientist"
)

st.caption("📧 Contact: giftmakoloi@gmail.com")
