🌱 Soil Carbon Monitoring System

This is a simple Python project for monitoring soil carbon data. It allows storing, viewing, and analyzing soil carbon levels with charts and maps. The project is built using Flask, MySQL (HeidiSQL), Leaflet.js, and Chart.js.

📖 Project Overview

Input soil carbon data (with latitude & longitude).

Show records in a clean table format.

Visualize soil carbon trends using charts.

Display monitoring points on an interactive map.

Export data to CSV and PDF reports for offline use.

🛠️ Tech Stack

Python (Flask) → Backend server

MySQL (HeidiSQL) → Database

HTML, CSS, JavaScript → Frontend design

Leaflet.js → Map visualization

Chart.js → Charts and graphs

ReportLab → Export PDF reports

📂 Project Structure
soil-carbon-monitoring-system/
│── static/              # CSS, JS, images
│── templates/           # HTML files
│── soil_carbon_analysis.py   # Main Python script (Flask app)
│── requirements.txt     # List of Python dependencies
│── README.md            # Project documentation

🚀 How to Run the Project
Step 1: Install Python

Make sure Python is installed on your computer. You can check by running:

python --version

Step 2: Install the Required Libraries
pip install flask mysql-connector-python reportlab

Step 3: Run the Application

Go to the folder where soil_carbon_analysis.py is located and run:

python soil_carbon_analysis.py

Step 4: Open in Browser

After running, open your browser and go to:

http://127.0.0.1:5000

📊 Example Workflow

Add soil carbon data into the system.

View records in tables.

Check soil carbon values on the map.

Analyze the chart trends.

Export results as CSV or PDF.

📌 Future Improvements

Add AI-based prediction of soil carbon.

Connect with IoT soil sensors for real-time data.

Improve user login and authentication.

🤝 Contributing

This is a learning project. Feel free to fork the repository and improve the code.
