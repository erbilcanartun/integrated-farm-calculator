import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Streamlit app title
st.title("Integrated Farm Calculator")

# Input section
st.header("Input Farm Parameters")
num_cows = st.number_input("Number of Cows", min_value=10, max_value=500, value=60, step=10)
deeded_land = st.number_input("Deeded Land (hectares, includes greenhouse, barn, etc.)", min_value=10, max_value=200, value=50, step=5)
grassland_area = st.number_input("Grassland Area (hectares, for grazing/hay)", min_value=0, max_value=200, value=35, step=5)
greenhouse_area = st.number_input("Greenhouse Area (hectares, soilless)", min_value=0.5, max_value=10.0, value=1.5, step=0.5)

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
FEED_DM_PER_COW_KG = 6570  # kg DM/year/cow
GRASSLAND_YIELD_KG_HA = 5250  # kg DM/ha/year
FEED_CROP_YIELD_KG_HA = 15000  # kg DM/ha/year
PURCHASED_FEED_COST_USD = 0.1  # USD/kg DM

# Calculations
def calculate_farm_metrics(cows, deeded_ha, grassland_ha, greenhouse_ha):
    # Land requirements
    pasture_ha = min(grassland_ha, cows * 0.625)  # Max usable pasture
    buildings_ha = 1
    feed_crop_ha = max(0, deeded_ha - pasture_ha - greenhouse_ha - buildings_ha)
    total_required_ha = pasture_ha + greenhouse_ha + buildings_ha + (cows * 0.219 if feed_crop_ha < cows * 0.219 else feed_crop_ha)
    
    # Check land sufficiency
    if total_required_ha > deeded_ha:
        return None, f"Error: Deeded land insufficient. Need {total_required_ha:.1f} ha, provided {deeded_ha:.1f} ha."
    
    # Feed sufficiency
    feed_needed_kg = cows * FEED_DM_PER_COW_KG
    pasture_feed_kg = pasture_ha * GRASSLAND_YIELD_KG_HA
    crop_feed_kg = feed_crop_ha * FEED_CROP_YIELD_KG_HA
    total_feed_kg = pasture_feed_kg + crop_feed_kg
    purchased_feed_kg = max(0, feed_needed_kg - total_feed_kg)
    
    # Initial investment costs
    cost_cows = cows * 1500
    cost_greenhouse = greenhouse_ha * 50000
    cost_infrastructure = 80000 * (cows / 60)
    cost_bioenergy = 50000 * (cows / 60)
    cost_equipment = 30000 * (cows / 60)
    cost_supplies = 10000 * (cows / 60)
    total_investment = cost_cows + cost_greenhouse + cost_infrastructure + cost_bioenergy + cost_equipment + cost_supplies
    
    # Annual operating costs
    cost_feed = purchased_feed_kg * PURCHASED_FEED_COST_USD
    cost_labor = 36000 * (cows / 60 + greenhouse_ha / 1.5) / 2
    cost_vet = cows * 50
    cost_utilities = 5000 * (cows / 60)
    cost_marketing = 3000 * (cows / 60)
    cost_greenhouse_ops = 10000 * (greenhouse_ha / 1.5)
    cost_maintenance = 5000 * (cows / 60)
    total_costs = cost_feed + cost_labor + cost_vet + cost_utilities + cost_marketing + cost_greenhouse_ops + cost_maintenance
    
    # Daily operating costs
    daily_cost_feed = cost_feed / 365
    daily_cost_labor = cost_labor / 365
    daily_cost_vet = cost_vet / 365
    daily_cost_utilities = cost_utilities / 365
    daily_cost_marketing = cost_marketing / 365
    daily_cost_greenhouse = cost_greenhouse_ops / 365
    daily_cost_maintenance = cost_maintenance / 365
    
    # Products and revenue
    milk_liters_day = cows * MILK_YIELD_LITERS
    milk_revenue_year = milk_liters_day * 365 * MILK_PRICE_USD
    milk_revenue_day = milk_liters_day * MILK_PRICE_USD
    tomato_kg_day = greenhouse_ha * TOMATO_YIELD_TONS_HA * 1000 / 365
    tomato_revenue_year = tomato_kg_day * 365 * TOMATO_PRICE_USD
    tomato_revenue_day = tomato_kg_day * TOMATO_PRICE_USD
    manure_kg_day = cows * MANURE_PER_COW_KG
    vs_kg_day = manure_kg_day * VS_FRACTION
    biogas_m3_day = vs_kg_day * BIOGAS_YIELD_M3_KG
    electricity_kwh_day = biogas_m3_day * ENERGY_PER_M3_KWH * ELECTRICAL_EFFICIENCY
    farm_electricity_need_kwh_day = (cows * 500 / 365) + (greenhouse_ha * 5000 / 365)
    surplus_kwh_day = max(0, electricity_kwh_day - farm_electricity_need_kwh_day)
    electricity_revenue_year = surplus_kwh_day * 365 * ELECTRICITY_PRICE_USD
    electricity_revenue_day = surplus_kwh_day * ELECTRICITY_PRICE_USD
    total_revenue_year = milk_revenue_year + tomato_revenue_year + electricity_revenue_year
    total_revenue_day = milk_revenue_day + tomato_revenue_day + electricity_revenue_day
    
    # Profit and payback
    annual_profit = total_revenue_year - total_costs
    payback_period = total_investment / annual_profit if annual_profit > 0 else float('inf')
    
    # Projections (5 years, 2% revenue growth, 3% cost growth)
    years = [1, 2, 3, 4, 5]
    revenue_projections = [total_revenue_year * (1 + 0.02) ** (year - 1) for year in years]
    cost_projections = [total_costs * (1 + 0.03) ** (year - 1) for year in years]
    profit_projections = [rev - cost for rev, cost in zip(revenue_projections, cost_projections)]
    
    return {
        "Investment (USD)": total_investment,
        "Investment (TRY)": total_investment * USD_TO_TRY,
        "Operating Costs (USD)": total_costs,
        "Operating Costs (TRY)": total_costs * USD_TO_TRY,
        "Revenue (USD)": total_revenue_year,
        "Revenue (TRY)": total_revenue_year * USD_TO_TRY,
        "Profit (USD)": annual_profit,
        "Profit (TRY)": annual_profit * USD_TO_TRY,
        "Payback Period (Years)": payback_period,
        "Daily Costs": {
            "Feed (USD)": daily_cost_feed,
            "Labor (USD)": daily_cost_labor,
            "Veterinary (USD)": daily_cost_vet,
            "Utilities (USD)": daily_cost_utilities,
            "Marketing (USD)": daily_cost_marketing,
            "Greenhouse Ops (USD)": daily_cost_greenhouse,
            "Maintenance (USD)": daily_cost_maintenance
        },
        "Daily Products": {
            "Milk (liters/day)": milk_liters_day,
            "Milk (USD/day)": milk_revenue_day,
            "Tomatoes (kg/day)": tomato_kg_day,
            "Tomatoes (USD/day)": tomato_revenue_day,
            "Electricity Produced (kWh/day)": electricity_kwh_day,
            "Electricity Consumed (kWh/day)": farm_electricity_need_kwh_day,
            "Surplus Electricity (kWh/day)": surplus_kwh_day,
            "Surplus Electricity (USD/day)": electricity_revenue_day
        },
        "Projections": {"Years": years, "Revenue": revenue_projections, "Costs": cost_projections, "Profit": profit_projections}
    }, None

# Perform calculations
results, error = calculate_farm_metrics(num_cows, deeded_land, grassland_area, greenhouse_area)

# Display results
if error:
    st.error(error)
else:
    st.header("Farm Metrics")
    
    # Basic Results Table
    st.subheader("Basic Financial Results")
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
            f"{results['Revenue (TRY)']:,.2f}",
            f"{results['Operating Costs (TRY)']:,.2f}",
            f"{results['Profit (TRY)']:,.2f}",
            f"{results['Payback Period (Years)']:.2f} years"
        ]
    }
    df_basic = pd.DataFrame(table_data)
    st.table(df_basic)
    
    # Daily Costs Table
    st.subheader("Daily Operating Costs")
    daily_costs_data = {
        "Category": ["Feed", "Labor", "Veterinary", "Utilities", "Marketing", "Greenhouse Operations", "Maintenance"],
        "USD/day": [
            f"${results['Daily Costs']['Feed (USD)']:.2f}",
            f"${results['Daily Costs']['Labor (USD)']:.2f}",
            f"${results['Daily Costs']['Veterinary (USD)']:.2f}",
            f"${results['Daily Costs']['Utilities (USD)']:.2f}",
            f"${results['Daily Costs']['Marketing (USD)']:.2f}",
            f"${results['Daily Costs']['Greenhouse Ops (USD)']:.2f}",
            f"${results['Daily Costs']['Maintenance (USD)']:.2f}"
        ],
        "TRY/day": [
            f"{results['Daily Costs']['Feed (USD)'] * USD_TO_TRY:.2f}",
            f"{results['Daily Costs']['Labor (USD)'] * USD_TO_TRY:.2f}",
            f"{results['Daily Costs']['Veterinary (USD)'] * USD_TO_TRY:.2f}",
            f"{results['Daily Costs']['Utilities (USD)'] * USD_TO_TRY:.2f}",
            f"{results['Daily Costs']['Marketing (USD)'] * USD_TO_TRY:.2f}",
            f"{results['Daily Costs']['Greenhouse Ops (USD)'] * USD_TO_TRY:.2f}",
            f"{results['Daily Costs']['Maintenance (USD)'] * USD_TO_TRY:.2f}"
        ]
    }
    df_daily_costs = pd.DataFrame(daily_costs_data)
    st.table(df_daily_costs)
    
    # Daily Products Table
    st.subheader("Daily Products and Revenue")
    daily_products_data = {
        "Product": ["Milk", "Tomatoes", "Electricity Produced", "Electricity Consumed", "Surplus Electricity"],
        "Quantity": [
            f"{results['Daily Products']['Milk (liters/day)']:.2f} liters",
            f"{results['Daily Products']['Tomatoes (kg/day)']:.2f} kg",
            f"{results['Daily Products']['Electricity Produced (kWh/day)']:.2f} kWh",
            f"{results['Daily Products']['Electricity Consumed (kWh/day)']:.2f} kWh",
            f"{results['Daily Products']['Surplus Electricity (kWh/day)']:.2f} kWh"
        ],
        "Value (USD/day)": [
            f"${results['Daily Products']['Milk (USD/day)']:.2f}",
            f"${results['Daily Products']['Tomatoes (USD/day)']:.2f}",
            "-",
            "-",
            f"${results['Daily Products']['Surplus Electricity (USD/day)']:.2f}"
        ],
        "Value (TRY/day)": [
            f"{results['Daily Products']['Milk (USD/day)'] * USD_TO_TRY:.2f}",
            f"{results['Daily Products']['Tomatoes (USD/day)'] * USD_TO_TRY:.2f}",
            "-",
            "-",
            f"{results['Daily Products']['Surplus Electricity (USD/day)'] * USD_TO_TRY:.2f}"
        ]
    }
    df_daily_products = pd.DataFrame(daily_products_data)
    st.table(df_daily_products)
    
    # Annual Costs Table
    st.subheader("Annual Operating Costs Breakdown")
    annual_costs_data = {
        "Category": ["Feed", "Labor", "Veterinary", "Utilities", "Marketing", "Greenhouse Operations", "Maintenance"],
        "USD/year": [
            f"${results['Daily Costs']['Feed (USD)'] * 365:.2f}",
            f"${results['Daily Costs']['Labor (USD)'] * 365:.2f}",
            f"${results['Daily Costs']['Veterinary (USD)'] * 365:.2f}",
            f"${results['Daily Costs']['Utilities (USD)'] * 365:.2f}",
            f"${results['Daily Costs']['Marketing (USD)'] * 365:.2f}",
            f"${results['Daily Costs']['Greenhouse Ops (USD)'] * 365:.2f}",
            f"${results['Daily Costs']['Maintenance (USD)'] * 365:.2f}"
        ],
        "TRY/year": [
            f"{results['Daily Costs']['Feed (USD)'] * 365 * USD_TO_TRY:.2f}",
            f"{results['Daily Costs']['Labor (USD)'] * 365 * USD_TO_TRY:.2f}",
            f"{results['Daily Costs']['Veterinary (USD)'] * 365 * USD_TO_TRY:.2f}",
            f"{results['Daily Costs']['Utilities (USD)'] * 365 * USD_TO_TRY:.2f}",
            f"{results['Daily Costs']['Marketing (USD)'] * 365 * USD_TO_TRY:.2f}",
            f"{results['Daily Costs']['Greenhouse Ops (USD)'] * 365 * USD_TO_TRY:.2f}",
            f"{results['Daily Costs']['Maintenance (USD)'] * 365 * USD_TO_TRY:.2f}"
        ]
    }
    df_annual_costs = pd.DataFrame(annual_costs_data)
    st.table(df_annual_costs)
    
    # Annual Earnings Table
    st.subheader("Annual Revenue Breakdown")
    annual_earnings_data = {
        "Source": ["Milk", "Tomatoes", "Surplus Electricity"],
        "USD/year": [
            f"${results['Daily Products']['Milk (USD/day)'] * 365:.2f}",
            f"${results['Daily Products']['Tomatoes (USD/day)'] * 365:.2f}",
            f"${results['Daily Products']['Surplus Electricity (USD/day)'] * 365:.2f}"
        ],
        "TRY/year": [
            f"{results['Daily Products']['Milk (USD/day)'] * 365 * USD_TO_TRY:.2f}",
            f"{results['Daily Products']['Tomatoes (USD/day)'] * 365 * USD_TO_TRY:.2f}",
            f"{results['Daily Products']['Surplus Electricity (USD/day)'] * 365 * USD_TO_TRY:.2f}"
        ]
    }
    df_annual_earnings = pd.DataFrame(annual_earnings_data)
    st.table(df_annual_earnings)
    
    # Plot
    st.subheader("5-Year Financial Projections")
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
    st.header("Summary and Insights")
    feed_status = "Self-sufficient in feed." if purchased_feed_kg == 0 else f"Requires purchasing {purchased_feed_kg:,.0f} kg of feed annually at ${purchased_feed_kg * PURCHASED_FEED_COST_USD:,.2f}."
    st.write(f"""
    The integrated farm with {num_cows} cows, a {greenhouse_area} ha soilless greenhouse, {grassland_area} ha of grassland, and {deeded_land} ha of deeded land requires an initial investment of ${results['Investment (USD)']:,.2f} ({results['Investment (TRY)']:,.2f} TRY). 
    It generates an annual revenue of ${results['Revenue (USD)']:,.2f} ({results['Revenue (TRY)']:,.2f} TRY) from milk, tomatoes, and surplus electricity, with operating costs of ${results['Operating Costs (USD)']:,.2f} ({results['Operating Costs (TRY)']:,.2f} TRY), yielding an annual profit of ${results['Profit (USD)']:,.2f} ({results['Profit (TRY)']:,.2f} TRY). 
    The payback period is {results['Payback Period (Years)']:.2f} years. 
    {feed_status}
    Risks include milk and tomato price fluctuations (±10%), disease outbreaks (e.g., foot-and-mouth disease), and seasonal feed shortages (winter yield drop of 10-15%). Mitigations include securing long-term buyer contracts, implementing biosecurity, and storing silage. The farm is energy self-sufficient via biogas, with surplus electricity enhancing revenue.
    """)