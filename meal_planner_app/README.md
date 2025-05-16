# مولد خطة الوجبات الغذائية (Meal Plan Generator)

This Streamlit app generates PDF meal plans with Arabic language support. Users can create personalized meal plans, add food items with nutritional information, and export the plan as a professionally designed PDF.

## Features

- Arabic language support with right-to-left (RTL) text
- Dynamic meal planning interface
- Automatic macronutrient calculations
- Beautiful PDF generation with custom styling
- Mobile-friendly responsive design

## Local Setup

1. Clone this repository:
   ```
   git clone https://github.com/your-username/meal-planner-app.git
   cd meal-planner-app
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

4. Open your browser and navigate to `http://localhost:8501`

## Deploying to Streamlit Cloud

1. Create a GitHub repository and push your code:
   ```
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/your-username/meal-planner-app.git
   git push -u origin main
   ```

2. Sign up for a free account at [Streamlit Cloud](https://streamlit.io/cloud)

3. Create a new app in Streamlit Cloud:
   - Click on "New app"
   - Connect your GitHub repository
   - Select the repository, branch, and main file path (`app.py`)
   - Click "Deploy"

4. Your app will be available at a URL like: `https://your-username-meal-planner-app-app-randomstring.streamlit.app`

## Requirements

- Python 3.8+
- Streamlit
- Pandas
- NumPy
- ReportLab
- Arabic-Reshaper
- Python-Bidi

## License

MIT 