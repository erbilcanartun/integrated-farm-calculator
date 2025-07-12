# Integrated Farm Calculator

## Overview
The **Integrated Farm Calculator** is a web application built with [Streamlit](https://streamlit.io/) to assist in planning a self-sufficient farm in Turkey. It takes user inputs such as the number of cows, greenhouse area, and total land area, and calculates key financial metrics, including initial investment, annual operating costs, revenue, profit, and payback period. The app also provides 5-year financial projections and visualizes them with an interactive plot. Calculations are performed using Python, leveraging data from a 60-cow farm model with biogas production and a soilless greenhouse for tomatoes.

### Features
- **Inputs:** Number of cows (10–500), greenhouse area (0.5–10 ha), total land area (10–200 ha).
- **Outputs:**
  - **Table:** Initial investment, annual costs, revenue, profit, and payback period in USD and TRY (1 USD = 40 TRY).
  - **Plot:** 5-year projections for revenue, costs, and profit using Plotly.
  - **Summary Text:** Overview of financial metrics and risk insights.
- **Backend:** Python calculations for costs, revenues, biogas energy, and projections.
- **Deployment:** Hosted on Streamlit Community Cloud for remote access.

### Assumptions
- Based on a 60-cow farm model with Holstein-Friesian cows (25 liters/cow/day, $0.4/liter milk).
- Soilless greenhouse produces 100 tons/ha/year of tomatoes ($0.125/kg).
- Biogas from manure generates electricity ($0.1/kWh surplus).
- Costs and revenues scale linearly from the base model.
- Projections assume 2% annual revenue growth and 3% cost growth.

## Installation
To run the app locally, follow these steps:

### Prerequisites
- Python 3.8+
- Git (for cloning the repository)
- A code editor (e.g., VS Code)

### Steps
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-username/integrated-farm-calculator.git
   cd integrated-farm-calculator
   ```

2. **Install Dependencies:**
   Create a virtual environment and install required packages:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the App Locally:**
   ```bash
   streamlit run farm_calculator_app.py
   ```
   The app will open in your browser at `http://localhost:8501`.

### Requirements
The `requirements.txt` file includes:
```
streamlit
pandas
plotly
numpy
```

## Usage
1. **Access the App:**
   - Locally: Run the app as described above.
   - Remotely: Visit the deployed app URL (e.g., `https://your-app-name.streamlit.app`) after deployment.
2. **Enter Inputs:**
   - Number of cows (e.g., 60).
   - Greenhouse area in hectares (e.g., 1.5).
   - Total land area in hectares (e.g., 50).
3. **View Outputs:**
   - **Table:** Displays financial metrics in USD and TRY.
   - **Plot:** Shows 5-year projections for revenue, costs, and profit.
   - **Summary Text:** Provides investment, profit, payback period, and risk insights.
4. **Error Handling:** If the land area is insufficient for the specified cows and greenhouse, an error message is displayed.

## Deployment
To make the app accessible from another computer without running code locally, deploy it to **Streamlit Community Cloud**:

1. **Create a GitHub Repository:**
   - Push the project files (`farm_calculator_app.py`, `requirements.txt`) to a public GitHub repository.

2. **Sign Up for Streamlit Community Cloud:**
   - Go to [Streamlit Community Cloud](https://streamlit.io/cloud) and sign in with GitHub.

3. **Deploy the App:**
   - Connect your repository to Streamlit Community Cloud.
   - Select the `farm_calculator_app.py` file as the main script.
   - Deploy the app, which will generate a public URL (e.g., `https://your-app-name.streamlit.app`).

4. **Access Remotely:**
   - Share the URL with users to access the app from any device with a browser.

## Project Structure
```
integrated-farm-calculator/
│
├── farm_calculator_app.py  # Main Streamlit app code
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Example Output
For inputs: 60 cows, 1.5 ha greenhouse, 50 ha land:
- **Table:**
  | Metric                  | USD          | TRY            |
  |-------------------------|--------------|----------------|
  | Initial Investment      | $279,000.00  | 11,160,000.00  |
  | Annual Operating Costs  | $65,480.00   | 2,619,200.00   |
  | Annual Revenue          | $230,628.00  | 9,225,120.00   |
  | Annual Profit           | $165,148.00  | 6,605,920.00   |
  | Payback Period          | 1.57 years   | 1.57 years     |
- **Plot:** Interactive line plot showing revenue, costs, and profit over 5 years.
- **Summary:** Details investment, profit, payback, and risks like price fluctuations and disease.

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make changes and commit (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

Please ensure code follows PEP 8 style guidelines and includes comments for clarity.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact
For questions or feedback, please open an issue on GitHub or contact [your-email@example.com](mailto:your-email@example.com).