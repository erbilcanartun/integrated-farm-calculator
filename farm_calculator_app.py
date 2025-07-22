import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Streamlit app title
st.title("Integrated Farm Calculator")

# Use tabs for organization
tab1, tab2 = st.tabs(["Full Farm Calculator", "Isolated Calculations"])

with tab1:
    # Input section for full farm
    st.header("Input Farm Parameters")
    num_cows = st.number_input("Number of Cows", min_value=10, max_value=500, value=100, step=10, key="farm_cows")
    deeded_land = st.number_input("Deeded Land (hectares)", min_value=10, max_value=200, value=51, step=5, key="deeded_land")
    grassland_area = st.number_input("Grassland Area (hectares)", min_value=0, max_value=200, value=35, step=5, key="grassland_area")
    greenhouse_area = st.number_input("Greenhouse Area (hectares)", min_value=0.01, max_value=10.0, value=1.5, step=0.1, key="greenhouse_area")  # Updated min_value to 0.01 for smaller areas

    # Dairy product portions
    st.subheader("Dairy Product Allocation (% of Milk Production)")
    col1, col2, col3 = st.columns(3)
    with col1:
        pct_milk = st.slider("Raw Milk (%)", 0, 100, 100, key="pct_milk")
    with col2:
        pct_cheese = st.slider("Cheese (%)", 0, 100, 0, key="pct_cheese")
    with col3:
        pct_cream = st.slider("Cream (%)", 0, 100, 0, key="pct_cream")
    if pct_milk + pct_cheese + pct_cream != 100:
        st.error("Allocations must sum to 100%.")
    else:
        # Assumptions: Cheese yield 0.1 kg/L milk (10L/kg), Cream 0.04 kg/L (4% fat)
        # Prices: Milk $0.4/L, Cheese $5/kg, Cream $3/kg (adjustable below)
        cheese_yield_kg_per_l = 0.1
        cream_yield_kg_per_l = 0.04

    # Greenhouse product choice
    st.subheader("Greenhouse Product")
    product_options = ["Tomato", "Lettuce", "Strawberry", "Cucumber"]
    selected_product = st.selectbox("Select Product", product_options, key="selected_product")

    # Preset ranges for product yields (tons/ha/year) and prices (USD/kg) - used for display only
    product_ranges = {
        "Tomato": {"yield": "Low: 100, Mid: 300, High: 600", "price": "Low: 0.1, Mid: 0.25, High: 0.4", "mid_yield": 300.0, "mid_price": 0.25},
        "Lettuce": {"yield": "Low: 200, Mid: 350, High: 500", "price": "Low: 0.5, Mid: 1.0, High: 1.5", "mid_yield": 350.0, "mid_price": 1.0},
        "Strawberry": {"yield": "Low: 50, Mid: 75, High: 100", "price": "Low: 1.0, Mid: 2.0, High: 3.0", "mid_yield": 75.0, "mid_price": 2.0},
        "Cucumber": {"yield": "Low: 200, Mid: 350, High: 500", "price": "Low: 0.2, Mid: 0.35, High: 0.5", "mid_yield": 350.0, "mid_price": 0.35}
    }

    # Editable constants - only number_input with mid defaults, range indicated in label
    st.header("Editable Constants")
    
    # Currency
    usd_to_try = st.number_input("USD to TRY Exchange Rate (Low: 30, Mid: 40, High: 50)", value=40.0, step=1.0, key="usd_to_try")

    # Dairy
    milk_yield_liters = st.number_input("Daily Milk Yield per Cow (liters) (Low: 20, Mid: 25, High: 30)", value=25.0, key="milk_yield_liters")
    milk_price_usd = st.number_input("Milk Price (USD/liter) (Low: 0.3, Mid: 0.4, High: 0.5)", value=0.4, step=0.05, key="milk_price_usd")
    cheese_price_usd = st.number_input("Cheese Price (USD/kg) (Low: 4, Mid: 5, High: 6)", value=5.0, step=0.5, key="cheese_price_usd")
    cream_price_usd = st.number_input("Cream Price (USD/kg) (Low: 2, Mid: 3, High: 4)", value=3.0, step=0.5, key="cream_price_usd")

    # Greenhouse
    yield_tons_ha = st.number_input(f"{selected_product} Yield (tons/ha/year) ({product_ranges[selected_product]['yield']})", value=product_ranges[selected_product]["mid_yield"], step=10.0, key="yield_tons_ha")
    product_price_usd = st.number_input(f"{selected_product} Price (USD/kg) ({product_ranges[selected_product]['price']})", value=product_ranges[selected_product]["mid_price"], step=0.05, key="product_price_usd")

    # Biogas/Energy
    manure_per_cow_kg = st.number_input("Daily Manure per Cow (kg) (Low: 40, Mid: 60, High: 80)", value=60.0, step=5.0, key="manure_per_cow_kg")
    vs_fraction = st.number_input("Volatile Solids Fraction (Low: 0.08, Mid: 0.096, High: 0.12)", value=0.096, step=0.01, key="vs_fraction")
    biogas_yield_m3_kg = st.number_input("Biogas Yield (m³/kg VS) (Low: 0.2, Mid: 0.3, High: 0.45)", value=0.3, step=0.05, key="biogas_yield_m3_kg")
    energy_per_m3_kwh = st.number_input("Energy per m³ Biogas (kWh) (Low: 5, Mid: 6, High: 7)", value=6.0, step=0.5, key="energy_per_m3_kwh")
    electrical_efficiency = st.number_input("CHP Electrical Efficiency (Low: 0.3, Mid: 0.35, High: 0.4)", value=0.35, step=0.05, key="electrical_efficiency")
    electricity_sell_price_usd = st.number_input("Electricity Sell Price (USD/kWh) (Low: 0.08, Mid: 0.1, High: 0.12)", value=0.1, step=0.01, key="electricity_sell_price_usd")
    electricity_purchase_price_usd = st.number_input("Electricity Purchase Price (USD/kWh) (Low: 0.12, Mid: 0.15, High: 0.18)", value=0.15, step=0.01, key="electricity_purchase_price_usd")

    # Feed
    feed_dm_per_cow_kg = st.number_input("Annual Feed DM per Cow (kg) (Low: 6000, Mid: 6570, High: 7000)", value=6570.0, step=100.0, key="feed_dm_per_cow_kg")
    grassland_yield_kg_ha = st.number_input("Grassland Yield (kg DM/ha/year) (Low: 4000, Mid: 5250, High: 6500)", value=5250.0, step=250.0, key="grassland_yield_kg_ha")
    feed_crop_yield_kg_ha = st.number_input("Feed Crop Yield (kg DM/ha/year) (Low: 12000, Mid: 15000, High: 18000)", value=15000.0, step=1000.0, key="feed_crop_yield_kg_ha")
    purchased_feed_cost_usd = st.number_input("Purchased Feed Cost (USD/kg DM) (Low: 0.08, Mid: 0.1, High: 0.12)", value=0.1, step=0.01, key="purchased_feed_cost_usd")

    # Costs
    greenhouse_cost_per_ha = st.number_input("Greenhouse Construction Cost (USD/ha) (Low: 300000, Mid: 500000, High: 700000)", value=500000.0, step=50000.0, key="greenhouse_cost_per_ha")
    farm_elec_per_cow_kwh_year = st.number_input("Farm Electricity Need (kWh/cow/year) (Low: 400, Mid: 500, High: 600)", value=500.0, step=50.0, key="farm_elec_per_cow_kwh_year")
    gh_elec_per_ha_kwh_year = st.number_input("Greenhouse Electricity Need (kWh/ha/year) (Low: 500000, Mid: 1000000, High: 1500000)", value=1000000.0, step=100000.0, key="gh_elec_per_ha_kwh_year")

    if pct_milk + pct_cheese + pct_cream == 100:
        # Calculations function updated for dairy portions and product
        def calculate_farm_metrics(cows, deeded_ha, grassland_ha, greenhouse_ha):
            # Land requirements
            pasture_ha = min(grassland_ha, cows * (feed_dm_per_cow_kg / 2) / grassland_yield_kg_ha)
            buildings_ha = 1
            feed_crop_ha = max(0, deeded_ha - pasture_ha - greenhouse_ha - buildings_ha)
            
            # Land check
            feed_needed_kg = cows * feed_dm_per_cow_kg
            pasture_feed_kg = pasture_ha * grassland_yield_kg_ha
            required_feed_crop_ha = max(0, (feed_needed_kg - pasture_feed_kg) / feed_crop_yield_kg_ha)
            total_required_ha = pasture_ha + greenhouse_ha + buildings_ha + required_feed_crop_ha
            warning = f"Warning: For full feed self-sufficiency, need {total_required_ha:.1f} ha (using purchased feed instead)." if total_required_ha > deeded_ha else None

            # Feed sufficiency
            crop_feed_kg = feed_crop_ha * feed_crop_yield_kg_ha
            total_feed_kg = pasture_feed_kg + crop_feed_kg
            purchased_feed_kg = max(0, feed_needed_kg - total_feed_kg)

            # Investment costs
            cost_cows = cows * 3000.0
            cost_greenhouse = greenhouse_ha * greenhouse_cost_per_ha
            cost_infrastructure = 80000.0 * (cows / 60)
            cost_bioenergy = 50000.0 * (cows / 60)
            cost_equipment = 30000.0 * (cows / 60)
            cost_supplies = 10000.0 * (cows / 60)
            total_investment = cost_cows + cost_greenhouse + cost_infrastructure + cost_bioenergy + cost_equipment + cost_supplies

            # Operating costs
            cost_feed = purchased_feed_kg * purchased_feed_cost_usd
            cost_labor = 36000.0 * (cows / 60 + greenhouse_ha / 1.5)
            cost_vet = cows * 50.0
            cost_utilities = 5000.0 * (cows / 60)
            cost_marketing = 3000.0 * (cows / 60)
            cost_greenhouse_ops = 10000.0 * (greenhouse_ha / 1.5)
            cost_maintenance = 5000.0 * (cows / 60)
            
            # Dairy products and revenue
            milk_liters_day = cows * milk_yield_liters
            raw_milk_liters_day = milk_liters_day * (pct_milk / 100)
            cheese_kg_day = (milk_liters_day * (pct_cheese / 100)) * cheese_yield_kg_per_l
            cream_kg_day = (milk_liters_day * (pct_cream / 100)) * cream_yield_kg_per_l
            dairy_revenue_day = raw_milk_liters_day * milk_price_usd + cheese_kg_day * cheese_price_usd + cream_kg_day * cream_price_usd
            dairy_revenue_year = dairy_revenue_day * 365

            # Greenhouse product
            product_kg_day = greenhouse_ha * yield_tons_ha * 1000 / 365
            product_revenue_day = product_kg_day * product_price_usd
            product_revenue_year = product_revenue_day * 365

            # Biogas and electricity
            manure_kg_day = cows * manure_per_cow_kg
            vs_kg_day = manure_kg_day * vs_fraction
            biogas_m3_day = vs_kg_day * biogas_yield_m3_kg
            electricity_kwh_day = biogas_m3_day * energy_per_m3_kwh * electrical_efficiency
            farm_electricity_need_kwh_day = (cows * farm_elec_per_cow_kwh_year / 365) + (greenhouse_ha * gh_elec_per_ha_kwh_year / 365)
            surplus_kwh_day = max(0, electricity_kwh_day - farm_electricity_need_kwh_day)
            shortfall_kwh_day = max(0, farm_electricity_need_kwh_day - electricity_kwh_day)
            electricity_revenue_day = surplus_kwh_day * electricity_sell_price_usd
            electricity_revenue_year = electricity_revenue_day * 365
            electricity_purchase_cost_year = shortfall_kwh_day * 365 * electricity_purchase_price_usd
            electricity_purchase_day = shortfall_kwh_day * electricity_purchase_price_usd

            # Total revenue and costs
            total_revenue_year = dairy_revenue_year + product_revenue_year + electricity_revenue_year
            total_costs = cost_feed + cost_labor + cost_vet + cost_utilities + cost_marketing + cost_greenhouse_ops + cost_maintenance + electricity_purchase_cost_year

            # Daily costs
            daily_cost_feed = cost_feed / 365
            daily_cost_labor = cost_labor / 365
            daily_cost_vet = cost_vet / 365
            daily_cost_utilities = cost_utilities / 365
            daily_cost_marketing = cost_marketing / 365
            daily_cost_greenhouse = cost_greenhouse_ops / 365
            daily_cost_maintenance = cost_maintenance / 365
            daily_cost_electricity_purchase = electricity_purchase_day

            # Profit and payback
            annual_profit = total_revenue_year - total_costs
            payback_period = total_investment / annual_profit if annual_profit > 0 else float('inf')

            # Projections
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
                    "Electricity Purchase (USD)": daily_cost_electricity_purchase
                },
                "Daily Products": {
                    "Dairy (liters/day raw milk)": raw_milk_liters_day,
                    "Cheese (kg/day)": cheese_kg_day,
                    "Cream (kg/day)": cream_kg_day,
                    "Dairy (USD/day)": dairy_revenue_day,
                    f"{selected_product} (kg/day)": product_kg_day,
                    f"{selected_product} (USD/day)": product_revenue_day,
                    "Electricity Produced (kWh/day)": electricity_kwh_day,
                    "Electricity Consumed (kWh/day)": farm_electricity_need_kwh_day,
                    "Surplus Electricity (kWh/day)": surplus_kwh_day,
                    "Surplus Electricity (USD/day)": electricity_revenue_day,
                    "Shortfall Electricity (kWh/day)": shortfall_kwh_day
                },
                "Projections": {"Years": years, "Revenue": revenue_projections, "Costs": cost_projections, "Profit": profit_projections},
                "Dairy Revenue Year": dairy_revenue_year,
                "Product Revenue Year": product_revenue_year,
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
                f"{results['Operating Costs (TRY)']:,.2f}",
                f"{results['Revenue (TRY)']:,.2f}",
                f"{results['Profit (TRY)']:,.2f}",
                f"{results['Payback Period (Years)']:.2f} years"
            ]
        }
        df_basic = pd.DataFrame(table_data)
        st.table(df_basic)

        # Revenue Breakdown Pie
        st.subheader("Revenue Breakdown")
        fig_rev_pie = px.pie(names=['Dairy', selected_product, 'Electricity Surplus'],
                             values=[results['Dairy Revenue Year'], results['Product Revenue Year'], max(0, results['Electricity Revenue Year'])],
                             title="Annual Revenue Sources")
        st.plotly_chart(fig_rev_pie)

        # Cost Breakdown Pie
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

        # Projections
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

        # Summary and Insights
        st.header("Summary and Insights")
        st.write(f"""
        The integrated farm with {num_cows} cows, a {greenhouse_area} ha soilless greenhouse for {selected_product}, {grassland_area} ha of grassland, and {deeded_land} ha of deeded land is designed for sustainable operation through dairy, vegetable, and energy production integration.
        """)

        st.subheader("Financial Summary")
        df_financial_summary = pd.DataFrame(table_data)
        st.table(df_financial_summary)

        feed_status = "Self-sufficient in feed." if results['Purchased Feed Kg'] == 0 else f"Requires purchasing {results['Purchased Feed Kg']:,.0f} kg of feed annually at {results['Purchased Feed Cost Year']:,.2f} USD/year."
        energy_status = "Energy self-sufficient with surplus electricity for revenue." if results['Daily Products']['Shortfall Electricity (kWh/day)'] == 0 else f"Requires purchasing {results['Shortfall Kwh Year']:,.0f} kWh of electricity annually at {results['Electricity Purchase Cost Year']:,.2f} USD/year."
        st.markdown(f"""
        **Feed Status:** {feed_status}  

        **Energy Status:** {energy_status}  

        The farm uses biogas for on-site electricity, selling surplus at {electricity_sell_price_usd:.2f} USD/kWh and purchasing any shortfall at {electricity_purchase_price_usd:.2f} USD/kWh.
        """)

        st.subheader("Risks and Mitigations")
        st.markdown("""
        - **Price Fluctuations (Dairy and {selected_product}, ±10%):** Secure long-term buyer contracts to stabilize income.
        - **Disease Outbreaks (e.g., Foot-and-Mouth Disease):** Implement biosecurity measures, vaccination, and regular veterinary checks.
        - **Seasonal Feed Shortages (Winter Yield Drop of 10-15%):** Store surplus silage from summer and diversify feed sources.
        - **Energy Variability:** Monitor biogas production; consider backup renewable sources like solar if shortfalls are frequent.
        """.format(selected_product=selected_product))

with tab2:
    st.header("Isolated Calculations")

    # Isolated Energy Production from Cows
    st.subheader("Energy Production from Cows")
    iso_cows = st.number_input("Number of Cows for Calculation", min_value=10, max_value=500, value=100, step=10, key="iso_cows")
    iso_manure = st.number_input("Daily Manure per Cow (kg) (Low: 40, Mid: 60, High: 80)", value=60.0, step=5.0, key="iso_manure")
    iso_vs = st.number_input("VS Fraction (Low: 0.08, Mid: 0.096, High: 0.12)", value=0.096, step=0.01, key="iso_vs")
    iso_biogas = st.number_input("Biogas Yield (m³/kg VS) (Low: 0.2, Mid: 0.3, High: 0.45)", value=0.3, step=0.05, key="iso_biogas")
    iso_energy = st.number_input("Energy per m³ (kWh) (Low: 5, Mid: 6, High: 7)", value=6.0, step=0.5, key="iso_energy")
    iso_eff = st.number_input("Efficiency (Low: 0.3, Mid: 0.35, High: 0.4)", value=0.35, step=0.05, key="iso_eff")

    manure_day = iso_cows * iso_manure
    vs_day = manure_day * iso_vs
    biogas_day = vs_day * iso_biogas
    elec_day = biogas_day * iso_energy * iso_eff
    elec_month = elec_day * 30
    elec_year = elec_day * 365

    st.write(f"Daily Electricity: {elec_day:.2f} kWh")
    st.write(f"Monthly: {elec_month:.2f} kWh")
    st.write(f"Yearly: {elec_year:.2f} kWh")

    # Isolated Energy Consumption for Greenhouse
    st.subheader("Energy Consumption for Greenhouse")
    iso_gh_area = st.number_input("Greenhouse Area (hectares)", min_value=0.01, max_value=10.0, value=1.5, step=0.1, key="iso_gh")  # Updated min_value
    iso_gh_elec = st.number_input("Electricity Need (kWh/ha/year) (Low: 500000, Mid: 1000000, High: 1500000)", value=1000000.0, step=100000.0, key="iso_gh_elec")

    elec_year_gh = iso_gh_area * iso_gh_elec
    elec_month_gh = elec_year_gh / 12
    elec_day_gh = elec_year_gh / 365

    st.write(f"Daily Consumption: {elec_day_gh:.2f} kWh")
    st.write(f"Monthly: {elec_month_gh:.2f} kWh")
    st.write(f"Yearly: {elec_year_gh:.2f} kWh")