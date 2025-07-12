import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Streamlit app title
st.title("Integrated Intelligent Farm Calculator")

# Input section
st.header("Input Farm Parameters")
num_cows = st.number_input("Number of Cows", min_value=10, max_value=500, value=60, step=10)
greenhouse_area = st.number_input("Greenhouse Area (hectares)", min_value=0.5, max_value=10.0, value=1.5, step=0.5)
land_area = st.number_input("Total Land Area (hectares)", min_value=10, max_value=200, value=50, step=5)

# Constants
USD_TO_TRY = 40
MILK_YIELD_LITERS = 25
MILK_PRICE_USD = 0.4
TOMATO_YIELD_TONS_HA = 100
TOMATO_PRICE_USD = 0.125
MANURE_PER_COW_KG = 40
VS_FRACTION = 0.12 * 0.8
BIOGAS_YIELD_M3_KG = 0.3
ENERGY_PER_M3_KWH = 6
ELECTRICAL_EFFICIENCY = 0.35
ELECTRICITY_PRICE_USD = 0.1

# Calculations
def calculate_farm_metrics(cows, greenhouse_ha, land_ha):
    # Feed land requirement
    pasture_ha = cows * 0.625  # 0.625 ha/cow for pasture
    feed_crop_ha = cows * 0.219  # 0.219 ha/cow for crops
    buildings_ha = 1
    total_required_ha = pasture_ha + feed_crop_ha + greenhouse_ha + buildings_ha
    
    # Check land sufficiency
    if total_required_ha > land_ha:
        return None, "Error: Land area insufficient. Need {:.1f} ha, provided {:.1f} ha.".format(total_required_ha, land_ha)
    
    # Initial investment costs
    cost_cows = cows * 1500
    cost_greenhouse = greenhouse_ha * 50000
    cost_infrastructure = 80000 * (cows / 60)  # Scaled from 60-cow base
    cost_bioenergy = 50000 * (cows / 60)
    cost_equipment = 30000 * (cows / 60)
    cost_supplies = 10000 * (cows / 60)
    total_investment = cost_cows + cost_greenhouse + cost_infrastructure + cost_bioenergy + cost_equipment + cost_supplies
    
    # Annual operating costs
    cost_feed = cows * 65.7  # Scaled from $3942 for 60 cows
    cost_labor = 36000 * (cows / 60 + greenhouse_ha / 1.5) / 2  # Adjusted for scale
    cost_vet = cows * 50
    cost_utilities = 5000 * (cows / 60)
    cost_marketing = 3000 * (cows / 60)
    cost_greenhouse_ops = 10000 * (greenhouse_ha / 1.5)
    cost_maintenance = 5000 * (cows / 60)
    total_costs = cost_feed + cost_labor + cost_vet + cost_utilities + cost_marketing + cost_greenhouse_ops + cost_maintenance
    
    # Revenue
    milk_revenue = cows * MILK_YIELD_LITERS * 365 * MILK_PRICE_USD
    tomato_revenue = greenhouse_ha * TOMATO_YIELD_TONS_HA * 1000 * TOMATO_PRICE_USD
    # Biogas revenue
    manure_kg_day = cows * MANURE_PER_COW_KG
    vs_kg_day = manure_kg_day * VS_FRACTION
    biogas_m3_day = vs_kg_day * BIOGAS_YIELD_M3_KG
    electricity_kwh_day = biogas_m3_day * ENERGY_PER_M3_KWH * ELECTRICAL_EFFICIENCY
    farm_electricity_need_kwh_day = (cows * 500 / 365) + (greenhouse_ha * 5000 / 365)  # 500 kWh/cow/year, 5000 kWh/ha/year
    surplus_kwh_year = max(0, (electricity_kwh_day - farm_electricity_need_kwh_day) * 365)
    electricity_revenue = surplus_kwh_year * ELECTRICITY_PRICE_USD
    total_revenue = milk_revenue + tomato_revenue + electricity_revenue
    
    # Profit and payback
    annual_profit = total_revenue - total_costs
    payback_period = total_investment / annual_profit if annual_profit > 0 else float('inf')
    
    # Projections (5 years, 2% revenue growth, 3% cost growth)
    years = [1, 2, 3, 4, 5]
    revenue_projections = [total_revenue * (1 + 0.02) ** (year - 1) for year in years]
    cost_projections = [total_costs * (1 + 0.03) ** (year - 1) for year in years]
    profit_projections = [rev - cost for rev, cost in zip(revenue_projections, cost_projections)]
    
    return {
        "Investment (USD)": total_investment,
        "Investment (TRY)": total_investment * USD_TO_TRY,
        "Operating Costs (USD)": total_costs,
        "Operating Costs (TRY)": total_costs * USD_TO_TRY,
        "Revenue (USD)": total_revenue,
        "Revenue (TRY)": total_revenue * USD_TO_TRY,
        "Profit (USD)": annual_profit,
        "Profit (TRY)": annual_profit * USD_TO_TRY,
        "Payback Period (Years)": payback_period,
        "Projections": {"Years": years, "Revenue": revenue_projections, "Costs": cost_projections, "Profit": profit_projections}
    }, None

# Perform calculations
results, error = calculate_farm_metrics(num_cows, greenhouse_area, land_area)

# Display results
if error:
    st.error(error)
else:
    st.header("Farm Metrics")
    
    # Table
    table_data = {
        "Metric": ["Initial Investment", "Annual Operating Costs", "Annual Revenue", "Annual Profit", "Payback Period"],
        "USD": [
            f"${results['Investment (USD)']:,.2f}",
            f"${results['Operating Costs (USD)']:,.2f}",
            f"${results['Revenue (USD)']:,.2f}",
            f"${results['Profit (USD)']:,.2f}",
            f"{results['Payback Period (Years)']:.2f} years"
        ],
        "TRY": [
            f"{results['Investment (TRY)']:,.2f}",
            f"{results['Operating Costs (TRY)']:,.2f}",
            f"{results['Revenue (TRY)']:,.2f}",
            f"{results['Profit (TRY)']:,.2f}",
            f"{results['Payback Period (Years)']:.2f} years"
        ]
    }
    df = pd.DataFrame(table_data)
    st.table(df)
    
    # Plot
    projection_data = pd.DataFrame({
        "Year": results["Projections"]["Years"],
        "Revenue (USD)": results["Projections"]["Revenue"],
        "Costs (USD)": results["Projections"]["Costs"],
        "Profit (USD)": results["Projections"]["Profit"]
    })
    fig = px.line(projection_data, x="Year", y=["Revenue (USD)", "Costs (USD)", "Profit (USD)"],
                  title="5-Year Financial Projections",
                  labels={"value": "Amount (USD)", "variable": "Metric"})
    st.plotly_chart(fig)
    
    # Summary text
    st.header("Summary")
    st.write(f"""
    The integrated farm with {num_cows} cows and a {greenhouse_area} ha soilless greenhouse on {land_area} ha of land requires an initial investment of ${results['Investment (USD)']:,.2f} ({results['Investment (TRY)']:,.2f} TRY). 
    It generates an annual revenue of ${results['Revenue (USD)']:,.2f} ({results['Revenue (TRY)']:,.2f} TRY) from milk, tomatoes, and surplus electricity, with operating costs of ${results['Operating Costs (USD)']:,.2f} ({results['Operating Costs (TRY)']:,.2f} TRY), yielding an annual profit of ${results['Profit (USD)']:,.2f} ({results['Profit (TRY)']:,.2f} TRY). 
    The payback period is {results['Payback Period (Years)']:.2f} years. 
    Over 5 years, revenue and profit are expected to grow modestly, assuming stable market conditions. Risks include milk price fluctuations, disease outbreaks, and seasonal feed shortages, which can be mitigated with contracts, biosecurity, and feed storage.
    """)