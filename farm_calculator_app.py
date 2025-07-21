import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Streamlit app title
st.title("Integrated Farm Calculator")

# Input section - Expanded with editable constants for flexibility
st.header("Input Farm Parameters")
num_cows = st.number_input("Number of Cows", min_value=10, max_value=500, value=100, step=10)  # Number of dairy cows; affects milk, manure, feed needs. Default set to 100 as requested.
deeded_land = st.number_input("Deeded Land (hectares, includes greenhouse, barn, etc.)", min_value=10, max_value=200, value=51, step=5)  # Total farm land; must suffice for allocations.
grassland_area = st.number_input("Grassland Area (hectares, for grazing/hay)", min_value=0, max_value=200, value=35, step=5)  # Area for pasture; limited by deeded land.
greenhouse_area = st.number_input("Greenhouse Area (hectares, soilless)", min_value=0.5, max_value=10.0, value=1.5, step=0.5)  # Hydroponic tomato area; high yield but energy-intensive.

st.header("Editable Constants (Yields, Prices, etc.)")
usd_to_try = st.number_input("USD to TRY Exchange Rate", value=40.0)  # Currency conversion; update based on current rates (e.g., ~33 in 2024, but 40 assumed).
milk_yield_liters = st.number_input("Daily Milk Yield per Cow (liters)", value=25.0)  # Average yield; realistic range 20-30 L/day based on breed/feed.
milk_price_usd = st.number_input("Milk Price (USD/liter)", value=0.4)  # Market price; fluctuates with demand/supply.
tomato_yield_tons_ha = st.number_input("Tomato Yield (tons/ha/year)", value=100.0)  # Hydroponic yield; can reach 600 with advanced tech, but 100 conservative.
tomato_price_usd = st.number_input("Tomato Price (USD/kg)", value=0.125)  # Wholesale price; $125/ton.
manure_per_cow_kg = st.number_input("Daily Manure per Cow (kg)", value=40.0)  # Wet manure; typical 40-80 kg/day.
vs_fraction = st.number_input("Volatile Solids Fraction of Manure", value=0.096)  # VS as % of wet weight (e.g., 12% DM * 80% VS/DM); for biogas potential.
biogas_yield_m3_kg = st.number_input("Biogas Yield (m³/kg VS)", value=0.3)  # From anaerobic digestion; range 0.2-0.45.
energy_per_m3_kwh = st.number_input("Energy per m³ Biogas (kWh)", value=6.0)  # Heating value; 5-7 average.
electrical_efficiency = st.number_input("CHP Electrical Efficiency", value=0.35)  # Conversion to electricity; 35-42% typical.
electricity_sell_price_usd = st.number_input("Electricity Sell Price (USD/kWh)", value=0.1)  # Selling price for surplus; often lower than purchase price.
electricity_purchase_price_usd = st.number_input("Electricity Purchase Price (USD/kWh)", value=0.15)  # New: Purchase price for shortfall; typically higher than sell price.
feed_dm_per_cow_kg = st.number_input("Annual Feed DM per Cow (kg)", value=6570.0)  # Dry matter intake; ~18 kg/day * 365.
grassland_yield_kg_ha = st.number_input("Grassland Yield (kg DM/ha/year)", value=5250.0)  # Pasture/hay production; depends on soil/climate.
feed_crop_yield_kg_ha = st.number_input("Feed Crop Yield (kg DM/ha/year)", value=15000.0)  # E.g., silage corn; high-yield crops.
purchased_feed_cost_usd = st.number_input("Purchased Feed Cost (USD/kg DM)", value=0.1)  # If on-farm feed insufficient.
greenhouse_cost_per_ha = st.number_input("Greenhouse Construction Cost (USD/ha)", value=500000.0)  # Improved: Realistic ~$500K-$5M; was underestimated at 50K.
farm_elec_per_cow_kwh_year = st.number_input("Farm Electricity Need (kWh/cow/year)", value=500.0)  # Base usage; 800-1200 typical.
gh_elec_per_ha_kwh_year = st.number_input("Greenhouse Electricity Need (kWh/ha/year)", value=1000000.0)  # Improved: ~1M for hydroponics; was too low at 5K.

# Calculations function with explanations
def calculate_farm_metrics(cows, deeded_ha, grassland_ha, greenhouse_ha):
    # Land requirements: Allocate dynamically; buildings fixed at 1 ha (barns, etc.).
    pasture_ha = min(grassland_ha, cows * (feed_dm_per_cow_kg / 2) / grassland_yield_kg_ha)  # Improved: Cap pasture to provide ~50% feed; adjustable.
    buildings_ha = 1  # Fixed assumption for infrastructure.
    feed_crop_ha = max(0, deeded_ha - pasture_ha - greenhouse_ha - buildings_ha)  # Residual for feed crops (e.g., silage).
    
    # Improved land check: Calculate required for full self-sufficiency; warn if exceeded, but allow purchased feed.
    feed_needed_kg = cows * feed_dm_per_cow_kg  # Total annual DM feed required.
    pasture_feed_kg = pasture_ha * grassland_yield_kg_ha  # Feed from grazing/hay.
    required_feed_crop_ha = max(0, (feed_needed_kg - pasture_feed_kg) / feed_crop_yield_kg_ha)  # Min ha for remaining feed.
    total_required_ha = pasture_ha + greenhouse_ha + buildings_ha + required_feed_crop_ha
    if total_required_ha > deeded_ha:
        warning = f"Warning: For full feed self-sufficiency, need {total_required_ha:.1f} ha (using purchased feed instead)."
    else:
        warning = None

    # Feed sufficiency: Calculate actual production and shortfall.
    crop_feed_kg = feed_crop_ha * feed_crop_yield_kg_ha
    total_feed_kg = pasture_feed_kg + crop_feed_kg
    purchased_feed_kg = max(0, feed_needed_kg - total_feed_kg)  # Buy if short; costed below.

    # Initial investment costs: Scaled to base 60-cow farm; but cows and greenhouse variable.
    cost_cows = cows * 3000.0  # Improved: $3,000/cow realistic in 2025.
    cost_greenhouse = greenhouse_ha * greenhouse_cost_per_ha  # High due to hydroponic tech.
    cost_infrastructure = 80000.0 * (cows / 60)  # Roads, fencing, etc.
    cost_bioenergy = 50000.0 * (cows / 60)  # Biogas plant.
    cost_equipment = 30000.0 * (cows / 60)  # Milking, tractors.
    cost_supplies = 10000.0 * (cows / 60)  # Initial stock.
    total_investment = cost_cows + cost_greenhouse + cost_infrastructure + cost_bioenergy + cost_equipment + cost_supplies

    # Annual operating costs: Variable with scale; labor shared between dairy/green.
    cost_feed = purchased_feed_kg * purchased_feed_cost_usd
    cost_labor = 36000.0 * (cows / 60 + greenhouse_ha / 1.5)
    cost_vet = cows * 50.0
    cost_utilities = 5000.0 * (cows / 60)
    cost_marketing = 3000.0 * (cows / 60)
    cost_greenhouse_ops = 10000.0 * (greenhouse_ha / 1.5)
    cost_maintenance = 5000.0 * (cows / 60)
    
    # Products and revenue: Daily then annualized.
    milk_liters_day = cows * milk_yield_liters  # Daily production.
    milk_revenue_year = milk_liters_day * 365 * milk_price_usd
    milk_revenue_day = milk_liters_day * milk_price_usd
    tomato_kg_day = greenhouse_ha * tomato_yield_tons_ha * 1000 / 365
    tomato_revenue_year = tomato_kg_day * 365 * tomato_price_usd
    tomato_revenue_day = tomato_kg_day * tomato_price_usd
    manure_kg_day = cows * manure_per_cow_kg
    vs_kg_day = manure_kg_day * vs_fraction  # Digestible portion for biogas.
    biogas_m3_day = vs_kg_day * biogas_yield_m3_kg
    electricity_kwh_day = biogas_m3_day * energy_per_m3_kwh * electrical_efficiency  # Via CHP system.
    farm_electricity_need_kwh_day = (cows * farm_elec_per_cow_kwh_year / 365) + (greenhouse_ha * gh_elec_per_ha_kwh_year / 365)  # On-farm consumption.
    surplus_kwh_day = max(0, electricity_kwh_day - farm_electricity_need_kwh_day)  # Sellable excess.
    shortfall_kwh_day = max(0, farm_electricity_need_kwh_day - electricity_kwh_day)  # New: Shortfall to purchase if production insufficient.
    electricity_revenue_year = surplus_kwh_day * 365 * electricity_sell_price_usd  # Revenue from surplus.
    electricity_revenue_day = surplus_kwh_day * electricity_sell_price_usd
    electricity_purchase_cost_year = shortfall_kwh_day * 365 * electricity_purchase_price_usd  # New: Added to costs if shortfall.
    total_revenue_year = milk_revenue_year + tomato_revenue_year + electricity_revenue_year
    
    # Update total costs with electricity purchase if any
    total_costs = cost_feed + cost_labor + cost_vet + cost_utilities + cost_marketing + cost_greenhouse_ops + cost_maintenance + electricity_purchase_cost_year

    # Daily operating costs: For granular view; assumes uniform year. Add electricity purchase daily.
    daily_cost_feed = cost_feed / 365
    daily_cost_labor = cost_labor / 365
    daily_cost_vet = cost_vet / 365
    daily_cost_utilities = cost_utilities / 365
    daily_cost_marketing = cost_marketing / 365
    daily_cost_greenhouse = cost_greenhouse_ops / 365
    daily_cost_maintenance = cost_maintenance / 365
    daily_cost_electricity_purchase = shortfall_kwh_day * electricity_purchase_price_usd  # New daily cost.

    # Profit and payback: Basic metrics.
    annual_profit = total_revenue_year - total_costs
    payback_period = total_investment / annual_profit if annual_profit > 0 else float('inf')
    
    # Projections: 5 years with growth; simplistic but illustrative.
    years = [1, 2, 3, 4, 5]
    revenue_projections = [total_revenue_year * (1 + 0.02) ** (year - 1) for year in years]
    cost_projections = [total_costs * (1 + 0.03) ** (year - 1) for year in years]
    profit_projections = [rev - cost for rev, cost in zip(revenue_projections, cost_projections)]
    
    return {
        "Investment (USD)": total_investment,
        "Investment (TRY)": total_investment * usd_to_try,
        "Operating Costs (USD)": total_costs,
        "Operating Costs (TRY)": total_costs * usd_to_try,
        "Revenue (USD)": total_revenue_year,
        "Revenue (TRY)": total_revenue_year * usd_to_try,
        "Profit (USD)": annual_profit,
        "Profit (TRY)": annual_profit * usd_to_try,
        "Payback Period (Years)": payback_period,
        "Daily Costs": {
            "Feed (USD)": daily_cost_feed,
            "Labor (USD)": daily_cost_labor,
            "Veterinary (USD)": daily_cost_vet,
            "Utilities (USD)": daily_cost_utilities,
            "Marketing (USD)": daily_cost_marketing,
            "Greenhouse Ops (USD)": daily_cost_greenhouse,
            "Maintenance (USD)": daily_cost_maintenance,
            "Electricity Purchase (USD)": daily_cost_electricity_purchase  # New.
        },
        "Daily Products": {
            "Milk (liters/day)": milk_liters_day,
            "Milk (USD/day)": milk_revenue_day,
            "Tomatoes (kg/day)": tomato_kg_day,
            "Tomatoes (USD/day)": tomato_revenue_day,
            "Electricity Produced (kWh/day)": electricity_kwh_day,
            "Electricity Consumed (kWh/day)": farm_electricity_need_kwh_day,
            "Surplus Electricity (kWh/day)": surplus_kwh_day,
            "Surplus Electricity (USD/day)": electricity_revenue_day,
            "Shortfall Electricity (kWh/day)": shortfall_kwh_day  # New: For display.
        },
        "Projections": {"Years": years, "Revenue": revenue_projections, "Costs": cost_projections, "Profit": profit_projections},
        "Milk Revenue Year": milk_revenue_year,
        "Tomato Revenue Year": tomato_revenue_year,
        "Electricity Revenue Year": electricity_revenue_year,
        "Purchased Feed Kg": purchased_feed_kg,
        "Electricity Purchase Cost Year": electricity_purchase_cost_year,
        "Shortfall Kwh Year": shortfall_kwh_day * 365,
        "Purchased Feed Cost Year": cost_feed
    }, warning

# Perform calculations
results, warning = calculate_farm_metrics(num_cows, deeded_land, grassland_area, greenhouse_area)

if warning:
    st.warning(warning)

st.header("Farm Metrics")

# Basic Results Table - Updated to reflect new costs
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
        f"{results['Operating Costs (TRY)']:,.2f}",
        f"{results['Revenue (TRY)']:,.2f}",
        f"{results['Profit (TRY)']:,.2f}",
        f"{results['Payback Period (Years)']:.2f} years"
    ]
}
df_basic = pd.DataFrame(table_data)
st.table(df_basic)

# ... (Other tables similar; omitted for brevity, but add TRY calculations as before. Update daily costs table to include Electricity Purchase.)

# For example, here's an updated Daily Costs Table snippet:
# st.subheader("Daily Operating Costs")
# daily_costs_data = {
#     "Category": ["Feed", "Labor", "Veterinary", "Utilities", "Marketing", "Greenhouse Operations", "Maintenance", "Electricity Purchase"],
#     "USD/day": [
#         f"${results['Daily Costs']['Feed (USD)']:.2f}",
#         f"${results['Daily Costs']['Labor (USD)']:.2f}",
#         f"${results['Daily Costs']['Veterinary (USD)']:.2f}",
#         f"${results['Daily Costs']['Utilities (USD)']:.2f}",
#         f"${results['Daily Costs']['Marketing (USD)']:.2f}",
#         f"${results['Daily Costs']['Greenhouse Ops (USD)']:.2f}",
#         f"${results['Daily Costs']['Maintenance (USD)']:.2f}",
#         f"${results['Daily Costs']['Electricity Purchase (USD)']:.2f}"
#     ],
#     "TRY/day": [value * usd_to_try for value in USD/day values] # Adjust accordingly
# }
# st.table(pd.DataFrame(daily_costs_data))

# Similar updates for annual costs (add electricity purchase), daily products (add shortfall).

# New: Pie Charts (updated with electricity revenue if positive)
st.subheader("Revenue Breakdown")
fig_rev_pie = px.pie(names=['Milk', 'Tomatoes', 'Electricity Surplus'],
                     values=[results['Milk Revenue Year'], results['Tomato Revenue Year'], results['Electricity Revenue Year'] if results['Electricity Revenue Year'] > 0 else 0],
                     title="Annual Revenue Sources")
st.plotly_chart(fig_rev_pie)

st.subheader("Cost Breakdown")
costs_dict = {
    'Feed': results['Daily Costs']['Feed (USD)'] * 365,
    'Labor': results['Daily Costs']['Labor (USD)'] * 365,
    'Veterinary': results['Daily Costs']['Veterinary (USD)'] * 365,
    'Utilities': results['Daily Costs']['Utilities (USD)'] * 365,
    'Marketing': results['Daily Costs']['Marketing (USD)'] * 365,
    'Greenhouse Ops': results['Daily Costs']['Greenhouse Ops (USD)'] * 365,
    'Maintenance': results['Daily Costs']['Maintenance (USD)'] * 365,
    'Electricity Purchase': results['Daily Costs']['Electricity Purchase (USD)'] * 365
}
fig_cost_pie = px.pie(names=list(costs_dict.keys()), values=list(costs_dict.values()), title="Annual Operating Costs")
st.plotly_chart(fig_cost_pie)

# Projections Chart (as before)
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

# Improved Summary and Insights: Reorganized with paragraphs, list, and table for better structure
st.header("Summary and Insights")

# Paragraph: Overview
st.write(f"""
The integrated farm with {num_cows} cows, a {greenhouse_area} ha soilless greenhouse, {grassland_area} ha of grassland, and {deeded_land} ha of deeded land is designed for sustainable operation through dairy, vegetable, and energy production integration.
""")

# Table: Financial Summary
st.subheader("Financial Summary")
financial_summary_table = {
    "Metric": ["Initial Investment", "Annual Revenue", "Annual Operating Costs", "Annual Profit", "Payback Period"],
    "USD": [
        f"${results['Investment (USD)']:,.2f}",
        f"${results['Revenue (USD)']:,.2f}",
        f"${results['Operating Costs (USD)']:,.2f}",
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
df_financial_summary = pd.DataFrame(financial_summary_table)
st.table(df_financial_summary)

# Paragraph: Feed and Energy Status - Fixed spacing in status strings
feed_status = "Self-sufficient in feed." if results['Purchased Feed Kg'] == 0 else f"Requires purchasing {results['Purchased Feed Kg']:,.0f} kg of feed annually at ${results['Purchased Feed Cost Year']:,.2f} USD/year."
energy_status = "Energy self-sufficient with surplus electricity for revenue." if results['Daily Products']['Shortfall Electricity (kWh/day)'] == 0 else f"Requires purchasing {results['Shortfall Kwh Year']:,.0f} kWh of electricity annually at ${results['Electricity Purchase Cost Year']:,.2f} USD/year."
st.markdown(f"""
**Feed Status:** {feed_status}  

**Energy Status:** {energy_status}  

The farm uses biogas for on-site electricity, selling surplus at {electricity_sell_price_usd:.2f} USD/kWh and purchasing any shortfall at {electricity_purchase_price_usd:.2f} USD/kWh.
""")

# List: Risks and Mitigations (using Markdown for bullets)
st.subheader("Risks and Mitigations")
st.markdown("""
- **Price Fluctuations (Milk and Tomatoes, ±10%):** Secure long-term buyer contracts to stabilize income.
- **Disease Outbreaks (e.g., Foot-and-Mouth Disease):** Implement biosecurity measures, vaccination, and regular veterinary checks.
- **Seasonal Feed Shortages (Winter Yield Drop of 10-15%):** Store surplus silage from summer and diversify feed sources.
- **Energy Variability:** Monitor biogas production; consider backup renewable sources like solar if shortfalls are frequent.
""")