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
    deeded_land = st.number_input("Deeded Land (hectares)", min_value=10, max_value=200, value=51, step=5)
    grassland_area = st.number_input("Grassland Area (hectares)", min_value=0, max_value=200, value=35, step=5)
    greenhouse_area = st.number_input("Greenhouse Area (hectares)", min_value=0.5, max_value=10.0, value=1.5, step=0.5)

    # Dairy product portions
    st.subheader("Dairy Product Allocation (% of Milk Production)")
    col1, col2, col3 = st.columns(3)
    with col1:
        pct_milk = st.slider("Raw Milk (%)", 0, 100, 100)
    with col2:
        pct_cheese = st.slider("Cheese (%)", 0, 100, 0)
    with col3:
        pct_cream = st.slider("Cream (%)", 0, 100, 0)
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
    selected_product = st.selectbox("Select Product", product_options)

    # Preset ranges for product yields (tons/ha/year) and prices (USD/kg)
    product_presets = {
        "Tomato": {"yield": {"low": 100.0, "mid": 300.0, "high": 600.0}, "price": {"low": 0.1, "mid": 0.25, "high": 0.4}},
        "Lettuce": {"yield": {"low": 200.0, "mid": 350.0, "high": 500.0}, "price": {"low": 0.5, "mid": 1.0, "high": 1.5}},
        "Strawberry": {"yield": {"low": 50.0, "mid": 75.0, "high": 100.0}, "price": {"low": 1.0, "mid": 2.0, "high": 3.0}},
        "Cucumber": {"yield": {"low": 200.0, "mid": 350.0, "high": 500.0}, "price": {"low": 0.2, "mid": 0.35, "high": 0.5}}
    }

    # Editable constants with presets
    st.header("Editable Constants with Presets")
    preset_options = ["Low", "Mid", "High", "Custom"]

    # Function to get value with preset
    def get_value_with_preset(label, presets, default_mid, min_val=0.0, step=0.1, key=None):
        preset = st.selectbox(f"{label} Preset", preset_options, index=1, key=key)  # Default Mid
        if preset == "Custom":
            return st.number_input(f"{label} (Custom)", value=default_mid, min_value=min_val, step=step, key=key+"_custom")
        else:
            return presets[preset.lower()]

    # Currency
    usd_to_try = get_value_with_preset("USD to TRY Exchange Rate", {"low": 30.0, "mid": 40.0, "high": 50.0}, 40.0, step=1.0)

    # Dairy
    milk_yield_liters = get_value_with_preset("Daily Milk Yield per Cow (liters)", {"low": 20.0, "mid": 25.0, "high": 30.0}, 25.0)
    milk_price_usd = get_value_with_preset("Milk Price (USD/liter)", {"low": 0.3, "mid": 0.4, "high": 0.5}, 0.4, step=0.05)
    cheese_price_usd = get_value_with_preset("Cheese Price (USD/kg)", {"low": 4.0, "mid": 5.0, "high": 6.0}, 5.0, step=0.5)
    cream_price_usd = get_value_with_preset("Cream Price (USD/kg)", {"low": 2.0, "mid": 3.0, "high": 4.0}, 3.0, step=0.5)

    # Greenhouse
    yield_tons_ha = get_value_with_preset(f"{selected_product} Yield (tons/ha/year)", product_presets[selected_product]["yield"], product_presets[selected_product]["yield"]["mid"])
    product_price_usd = get_value_with_preset(f"{selected_product} Price (USD/kg)", product_presets[selected_product]["price"], product_presets[selected_product]["price"]["mid"], step=0.05)

    # Biogas/Energy
    manure_per_cow_kg = get_value_with_preset("Daily Manure per Cow (kg)", {"low": 40.0, "mid": 60.0, "high": 80.0}, 40.0, step=5.0)
    vs_fraction = get_value_with_preset("Volatile Solids Fraction", {"low": 0.08, "mid": 0.096, "high": 0.12}, 0.096, step=0.01)
    biogas_yield_m3_kg = get_value_with_preset("Biogas Yield (m³/kg VS)", {"low": 0.2, "mid": 0.3, "high": 0.45}, 0.3, step=0.05)
    energy_per_m3_kwh = get_value_with_preset("Energy per m³ Biogas (kWh)", {"low": 5.0, "mid": 6.0, "high": 7.0}, 6.0, step=0.5)
    electrical_efficiency = get_value_with_preset("CHP Electrical Efficiency", {"low": 0.3, "mid": 0.35, "high": 0.4}, 0.35, step=0.05)
    electricity_sell_price_usd = get_value_with_preset("Electricity Sell Price (USD/kWh)", {"low": 0.08, "mid": 0.1, "high": 0.12}, 0.1, step=0.01)
    electricity_purchase_price_usd = get_value_with_preset("Electricity Purchase Price (USD/kWh)", {"low": 0.12, "mid": 0.15, "high": 0.18}, 0.15, step=0.01)

    # Feed
    feed_dm_per_cow_kg = get_value_with_preset("Annual Feed DM per Cow (kg)", {"low": 6000.0, "mid": 6570.0, "high": 7000.0}, 6570.0, step=100.0)
    grassland_yield_kg_ha = get_value_with_preset("Grassland Yield (kg DM/ha/year)", {"low": 4000.0, "mid": 5250.0, "high": 6500.0}, 5250.0, step=250.0)
    feed_crop_yield_kg_ha = get_value_with_preset("Feed Crop Yield (kg DM/ha/year)", {"low": 12000.0, "mid": 15000.0, "high": 18000.0}, 15000.0, step=1000.0)
    purchased_feed_cost_usd = get_value_with_preset("Purchased Feed Cost (USD/kg DM)", {"low": 0.08, "mid": 0.1, "high": 0.12}, 0.1, step=0.01)

    # Costs
    greenhouse_cost_per_ha = get_value_with_preset("Greenhouse Construction Cost (USD/ha)", {"low": 300000.0, "mid": 500000.0, "high": 700000.0}, 500000.0, step=50000.0)
    farm_elec_per_cow_kwh_year = get_value_with_preset("Farm Electricity Need (kWh/cow/year)", {"low": 400.0, "mid": 500.0, "high": 600.0}, 500.0, step=50.0)
    gh_elec_per_ha_kwh_year = get_value_with_preset("Greenhouse Electricity Need (kWh/ha/year)", {"low": 500000.0, "mid": 1000000.0, "high": 1500000.0}, 1000000.0, step=100000.0)

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

        feed_status = "Self-sufficient in feed." if results['Purchased Feed Kg'] == 0 else f"Requires purchasing {results['Purchased Feed Kg']:,.0f} kg of feed annually at ${results['Purchased Feed Cost Year']:,.2f} USD/year."
        energy_status = "Energy self-sufficient with surplus electricity for revenue." if results['Daily Products']['Shortfall Electricity (kWh/day)'] == 0 else f"Requires purchasing {results['Shortfall Kwh Year']:,.0f} kWh of electricity annually at ${results['Electricity Purchase Cost Year']:,.2f} USD/year."
        st.markdown(f"""
        **Feed Status:** {feed_status}  

        **Energy Status:** {energy_status}  

        The farm uses biogas for on-site electricity, selling surplus at ${electricity_sell_price_usd:.2f} USD/kWh and purchasing any shortfall at ${electricity_purchase_price_usd:.2f} USD/kWh.
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
    iso_manure = get_value_with_preset("Daily Manure per Cow (kg)", {"low": 40.0, "mid": 60.0, "high": 80.0}, 40.0, key="iso_manure")
    iso_vs = get_value_with_preset("VS Fraction", {"low": 0.08, "mid": 0.096, "high": 0.12}, 0.096, key="iso_vs")
    iso_biogas = get_value_with_preset("Biogas Yield (m³/kg VS)", {"low": 0.2, "mid": 0.3, "high": 0.45}, 0.3, key="iso_biogas")
    iso_energy = get_value_with_preset("Energy per m³ (kWh)", {"low": 5.0, "mid": 6.0, "high": 7.0}, 6.0, key="iso_energy")
    iso_eff = get_value_with_preset("Efficiency", {"low": 0.3, "mid": 0.35, "high": 0.4}, 0.35, key="iso_eff")

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
    iso_gh_area = st.number_input("Greenhouse Area (hectares)", min_value=0.5, max_value=10.0, value=1.5, step=0.5, key="iso_gh")
    iso_gh_elec = get_value_with_preset("Electricity Need (kWh/ha/year)", {"low": 500000.0, "mid": 1000000.0, "high": 1500000.0}, 1000000.0, key="iso_gh_elec")

    elec_year_gh = iso_gh_area * iso_gh_elec
    elec_month_gh = elec_year_gh / 12
    elec_day_gh = elec_year_gh / 365

    st.write(f"Daily Consumption: {elec_day_gh:.2f} kWh")
    st.write(f"Monthly: {elec_month_gh:.2f} kWh")
    st.write(f"Yearly: {elec_year_gh:.2f} kWh")