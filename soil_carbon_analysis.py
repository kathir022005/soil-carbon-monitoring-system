
import os
from flask import Flask, jsonify, send_file
from flask_cors import CORS
import mysql.connector
import pandas as pd

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database Configuration
db_config = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "12345",
    "database": "soil_carbon"
}

def get_db_connection():
    """
    Establish a database connection with error handling
    """
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL Platform: {e}")
        return None

def fetch_soil_data():
    """
    Fetch soil data from the database and calculate SOC stock
    """
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                location, 
                latitude, 
                longitude, 
                depth_cm, 
                carbon_percentage, 
                bulk_density,
                ROUND(bulk_density * depth_cm * (carbon_percentage / 100), 2) AS soc_stock 
            FROM soil_data
        """)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except mysql.connector.Error as e:
        print(f"Error fetching data: {e}")
        return []

@app.route('/')
def index():
    """
    Serve the HTML file directly
    """
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
    <title>Soil Carbon Monitoring Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
    <link href="https://unpkg.com/leaflet/dist/leaflet.css" rel="stylesheet"/>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet"/>
    <style>
        body { 
            font-family: 'Roboto', sans-serif; 
        }
        #map { 
            height: 300px; 
        }
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #2d3748;
        }
        ::-webkit-scrollbar-thumb {
            background: #4a5568;
            border-radius: 4px;
        }
    </style>
</head>
<body class="bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
    <div class="min-h-screen flex flex-col">
        <header class="bg-white dark:bg-gray-800 shadow-md py-4">
            <div class="container mx-auto flex justify-between items-center px-6">
                <h1 class="text-2xl font-bold flex items-center">
                    <i class="fas fa-seedling mr-3 text-green-600"></i>
                    Soil Carbon Monitoring Dashboard
                </h1>
                <div class="flex items-center space-x-4">
                    <button id="toggleDarkMode" class="focus:outline-none hover:bg-gray-200 dark:hover:bg-gray-700 p-2 rounded-full transition-colors">
                        <i class="fas fa-moon text-xl"></i>
                    </button>
                    <button id="exportCSV" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md transition-colors flex items-center">
                        <i class="fas fa-file-csv mr-2"></i>Export CSV
                    </button>
                    <button id="exportPDF" class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-md transition-colors flex items-center">
                        <i class="fas fa-file-pdf mr-2"></i>Export PDF
                    </button>
                </div>
            </div>
        </header>

        <main class="flex-grow container mx-auto px-6 py-8">
            <div class="mb-6 flex items-center space-x-4">
                <div class="flex-grow">
                    <input 
                        id="searchInput" 
                        class="w-full p-4 rounded-md border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500" 
                        placeholder="Search by location, carbon %, or SOC stock..." 
                        type="text"
                    />
                </div>
                <div>
                    <select id="filterSelect" class="p-4 rounded-md border border-gray-300 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="">All Locations</option>
                    </select>
                </div>
            </div>

            <div class="bg-white dark:bg-gray-800 shadow-md rounded-md overflow-hidden">
                <div class="overflow-x-auto">
                    <table class="min-w-full leading-normal">
                        <thead>
                            <tr>
                                <th class="px-5 py-3 border-b-2 border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-700 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Location</th>
                                <th class="px-5 py-3 border-b-2 border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-700 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Carbon %</th>
                                <th class="px-5 py-3 border-b-2 border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-700 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Depth (cm)</th>
                                <th class="px-5 py-3 border-b-2 border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-700 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Bulk Density</th>
                                <th class="px-5 py-3 border-b-2 border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-700 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">SOC Stock</th>
                            </tr>
                        </thead>
                        <tbody id="dataTable">
                            <!-- Data will be loaded dynamically -->
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-white dark:bg-gray-800 shadow-md rounded-md p-6">
                    <h2 class="text-xl font-semibold mb-4 flex items-center">
                        <i class="fas fa-chart-bar mr-3 text-blue-600"></i>
                        Carbon % Histogram
                    </h2>
                    <canvas id="carbonChart"></canvas>
                </div>

                <div class="bg-white dark:bg-gray-800 shadow-md rounded-md p-6">
                    <h2 class="text-xl font-semibold mb-4 flex items-center">
                        <i class="fas fa-map-marked-alt mr-3 text-green-600"></i>
                        Sample Locations Map
                    </h2>
                    <div id="map"></div>
                </div>
            </div>
        </main>
    </div>

    <script>
        // Fetch and Render Data
        async function fetchData() {
            try {
                const response = await fetch('/api/soil_data');
                const data = await response.json();
                populateTable(data);
                renderChart(data);
                loadMap(data);
                populateFilterOptions(data);
            } catch (error) {
                console.error('Error fetching data:', error);
                document.getElementById('dataTable').innerHTML = `
                    <tr><td colspan="5" class="text-center text-red-500 p-4">
                        Unable to load data. Please try again later.
                    </td></tr>
                `;
            }
        }

        function populateTable(data) {
            const table = document.getElementById("dataTable");
            table.innerHTML = data.map(row => `
                <tr class="hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
                    <td class="px-5 py-5 border-b border-gray-200 dark:border-gray-700 text-sm">${row.location}</td>
                    <td class="px-5 py-5 border-b border-gray-200 dark:border-gray-700 text-sm">${row.carbon_percentage}%</td>
                    <td class="px-5 py-5 border-b border-gray-200 dark:border-gray-700 text-sm">${row.depth_cm} cm</td>
                    <td class="px-5 py-5 border-b border-gray-200 dark:border-gray-700 text-sm">${row.bulk_density} g/cm³</td>
                    <td class="px-5 py-5 border-b border-gray-200 dark:border-gray-700 text-sm">${row.soc_stock} Mg/ha</td>
                </tr>
            `).join('');
        }

        function getColorGradient(value, minValue, maxValue) {
            // Normalize the value between 0 and 1
            const normalized = (value - minValue) / (maxValue - minValue);
            
            // Create a color gradient from red (low carbon) to green (high carbon)
            const red = Math.round(255 * (1 - normalized));
            const green = Math.round(255 * normalized);
            
            return `rgb(${red}, ${green}, 0)`;
        }
        
        function renderChart(data) {
            // Find min and max carbon percentages for color scaling
            const carbonPercentages = data.map(d => d.carbon_percentage);
            const minCarbon = Math.min(...carbonPercentages);
            const maxCarbon = Math.max(...carbonPercentages);
        
            const ctx = document.getElementById('carbonChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.map(d => d.location),
                    datasets: [{
                        label: 'Carbon %',
                        data: carbonPercentages,
                        backgroundColor: carbonPercentages.map(value => 
                            getColorGradient(value, minCarbon, maxCarbon)
                        ),
                        borderColor: 'rgba(0,0,0,0.1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Carbon Percentage'
                            }
                        }
                    }
                }
            });
        }
        
        function loadMap(data) {
            // Find min and max carbon percentages for color scaling
            const carbonPercentages = data.map(d => d.carbon_percentage);
            const minCarbon = Math.min(...carbonPercentages);
            const maxCarbon = Math.max(...carbonPercentages);
        
            const map = L.map('map').setView([data[0].latitude, data[0].longitude], 5);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
            
            data.forEach(d => {
                const markerColor = getColorGradient(d.carbon_percentage, minCarbon, maxCarbon);
                
                // Create a custom icon with the color gradient
                const icon = L.divIcon({
                    className: 'custom-marker',
                    html: `<div style="background-color: ${markerColor}; 
                           width: 20px; 
                           height: 20px; 
                           border-radius: 50%; 
                           border: 2px solid rgba(0,0,0,0.3);"></div>`,
                    iconSize: [20, 20],
                    iconAnchor: [10, 10]
                });
        
                L.marker([d.latitude, d.longitude], { icon: icon })
                    .addTo(map)
                    .bindPopup(`
                        <strong>${d.location}</strong><br>
                        Carbon %: ${d.carbon_percentage}%<br>
                        SOC Stock: ${d.soc_stock} Mg/ha<br>
                        <div style="background-color: ${markerColor}; 
                            width: 100%; 
                            height: 10px; 
                            margin-top: 5px;"></div>
                    `);
            });
        }

        function populateFilterOptions(data) {
            const filterSelect = document.getElementById('filterSelect');
            const uniqueLocations = [...new Set(data.map(d => d.location))];
            
            filterSelect.innerHTML = `
                <option value="">All Locations</option>
                ${uniqueLocations.map(loc => `<option value="${loc}">${loc}</option>`).join('')}
            `;

            filterSelect.addEventListener('change', (e) => {
                const selectedLocation = e.target.value;
                const rows = document.querySelectorAll('#dataTable tr');
                
                rows.forEach(row => {
                    const locationCell = row.querySelector('td:first-child');
                    row.style.display = selectedLocation === '' || locationCell.textContent === selectedLocation ? '' : 'none';
                });
            });
        }

        // Dark Mode Toggle
        document.getElementById('toggleDarkMode').addEventListener('click', () => {
            document.documentElement.classList.toggle('dark');
            localStorage.setItem('darkMode', document.documentElement.classList.contains('dark'));
        });

        // Search functionality
        document.getElementById('searchInput').addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const rows = document.querySelectorAll('#dataTable tr');
            
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                const matchFound = Array.from(cells).some(cell => 
                    cell.textContent.toLowerCase().includes(searchTerm)
                );
                row.style.display = matchFound ? '' : 'none';
            });
        });

        // Export buttons (placeholder functionality)
        document.getElementById('exportCSV').addEventListener('click', async () => {
            try {
                const response = await fetch('/api/export/csv');
                const result = await response.json();
                alert(result.message);
            } catch (error) {
                console.error('CSV Export error:', error);
            }
        });

        document.getElementById('exportPDF').addEventListener('click', async () => {
            try {
                const response = await fetch('/api/export/pdf');
                const result = await response.json();
                alert(result.message);
            } catch (error) {
                console.error('PDF Export error:', error);
            }
        });

        // Initial data load
        fetchData();
    </script>
</body>
</html>
    '''

@app.route('/api/soil_data')
def get_soil_data():
    """
    API endpoint to retrieve soil data
    """
    soil_data = fetch_soil_data()
    return jsonify(soil_data)

@app.route('/api/export/csv')
def export_csv():
    """
    Export soil data to CSV
    """
    soil_data = fetch_soil_data()
    df = pd.DataFrame(soil_data)
    csv_path = os.path.join('exports', f'soil_carbon_data_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv')
    
    # Ensure exports directory exists
    os.makedirs('exports', exist_ok=True)
    
    df.to_csv(csv_path, index=False)
    return jsonify({"message": "CSV exported successfully", "path": csv_path})

@app.route('/api/export/pdf')
def export_pdf():
    """
    Export soil data to PDF (using reportlab)
    """
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
    from reportlab.lib import colors

    soil_data = fetch_soil_data()
    df = pd.DataFrame(soil_data)
    
    pdf_path = os.path.join('exports', f'soil_carbon_data_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.pdf')
    
    # Ensure exports directory exists
    os.makedirs('exports', exist_ok=True)
    
    # Prepare data for PDF
    data = [list(df.columns)] + df.values.tolist()
    
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    table = Table(data)
    
    # Add style
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    
    doc.build([table])
    
    return jsonify({"message": "PDF exported successfully", "path": pdf_path})

if __name__ == '__main__':
    app.run(debug=True, port=5000)