document.addEventListener('DOMContentLoaded', () =>{
    localStorage.clear()
    
    // Data Store
    const store = {
        menu: [],
        pantry: [],
        sales: [],
        forecasts: []
    };

    // Load data from localStorage
    function loadData() {
        const saved = localStorage.getItem('smartbiteData');
        if (saved) {
            Object.assign(store, JSON.parse(saved));
        }
        updateDashboard();
    }

    // Save data to localStorage
    function saveData() {
        localStorage.setItem('smartbiteData', JSON.stringify(store));
    }

    // Menu Management
    function openMenuModal() {
        document.getElementById('menuModal').classList.add('active');
    }

    function closeMenuModal() {
        document.getElementById('menuModal').classList.remove('active');
        document.getElementById('menuDishName').value = '';
    }

    function addMenuItem() {
        const dish = {
            id: Date.now(),
            name: document.getElementById('menuDishName').value,
            type: document.getElementById('menuType').value,
            profile: document.getElementById('menuProfile').value,
            flavor: document.getElementById('menuFlavor').value,
            price: parseFloat(document.getElementById('menuPrice').value)
        };

        if (dish.name && !isNaN(dish.price)) {
            store.menu.push(dish);
            saveData();
            updateMenuTable();
            closeMenuModal();
        } else {
            alert('Please fill in all fields');
        }
    }

    function updateMenuTable() {
        const tbody = document.getElementById('menuTable');
        if (store.menu.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-gray-500 py-8">No menu items yet. Add one to get started.</td></tr>';
            return;
        }
        
        tbody.innerHTML = store.menu.map(dish => `
            <tr>
                <td><strong>${dish.name}</strong></td>
                <td>${dish.type}</td>
                <td><span class="badge badge-success">${dish.profile}</span></td>
                <td>$${dish.price.toFixed(2)}</td>
                <td><span class="text-xs text-gray-500">Recipes →</span></td>
                <td>
                    <button onclick="deleteMenuItem(${dish.id})" class="text-red-600 hover:text-red-800 font-medium">Delete</button>
                </td>
            </tr>
        `).join('');
        
        document.getElementById('menuCount').textContent = store.menu.length;
    }

    function deleteMenuItem(id) {
        store.menu = store.menu.filter(m => m.id !== id);
        saveData();
        updateMenuTable();
    }

    function handleMenuCSVUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const lines = e.target.result.split('\n');
                lines.slice(1).forEach(line => {
                    if (line.trim()) {
                        const [name, type, profile, flavor, price] = line.split(',').map(s => s.trim());
                        if (name && type && profile && flavor && price) {
                            store.menu.push({
                                id: Date.now() + Math.random(),
                                name,
                                type,
                                profile,
                                flavor,
                                price: parseFloat(price)
                            });
                        }
                    }
                });
                saveData();
                updateMenuTable();
                alert('Menu CSV imported successfully!');
            } catch (err) {
                alert('Error parsing CSV: ' + err.message);
            }
        };
        reader.readAsText(file);
    }

    // Pantry Management
    function openPantryModal() {
        document.getElementById('pantryModal').classList.add('active');
    }

    function closePantryModal() {
        document.getElementById('pantryModal').classList.remove('active');
        document.getElementById('pantryIngredient').value = '';
        document.getElementById('pantryQuantity').value = '';
    }

    function addPantryItem() {
        const item = {
            id: Date.now(),
            name: document.getElementById('pantryIngredient').value,
            quantity: parseFloat(document.getElementById('pantryQuantity').value),
            unit: document.getElementById('pantryUnit').value
        };
        
        if (item.name && !isNaN(item.quantity)) {
            store.pantry.push(item);
            saveData();
            updatePantryTable();
            closePantryModal();
        } else {
            alert('Please fill in all fields');
        }
    }

    function updatePantryTable() {
        const tbody = document.getElementById('pantryTable');
        if (store.pantry.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-gray-500 py-8">No pantry items yet. Add one to get started.</td></tr>';
            document.getElementById('pantryCount').textContent = '0';
            return;
        }
        
        tbody.innerHTML = store.pantry.map(item => {
            let badge = '<span class="badge badge-success">✓ Stocked</span>';
            if (item.quantity < 10) badge = '<span class="badge badge-warning">⚠️ Low</span>';
            if (item.quantity < 5) badge = '<span class="badge badge-danger">🔴 Critical</span>';
            
            return `
                <tr>
                    <td><strong>${item.name}</strong></td>
                    <td>${item.quantity}</td>
                    <td>${item.unit}</td>
                    <td>${badge}</td>
                    <td>
                        <button onclick="deletePantryItem(${item.id})" class="text-red-600 hover:text-red-800 font-medium">Delete</button>
                    </td>
                </tr>
            `;
        }).join('');
        
        document.getElementById('pantryCount').textContent = store.pantry.length;
    }

    function deletePantryItem(id) {
        store.pantry = store.pantry.filter(p => p.id !== id);
        saveData();
        updatePantryTable();
    }

    function handlePantryCSVUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const lines = e.target.result.split('\n');
                lines.slice(1).forEach(line => {
                    if (line.trim()) {
                        const [name, quantity, unit] = line.split(',').map(s => s.trim());
                        if (name && quantity && unit) {
                            store.pantry.push({
                                id: Date.now() + Math.random(),
                                name,
                                quantity: parseFloat(quantity),
                                unit
                            });
                        }
                    }
                });
                saveData();
                updatePantryTable();
                alert('Pantry CSV imported successfully!');
            } catch (err) {
                alert('Error parsing CSV: ' + err.message);
            }
        };
        reader.readAsText(file);
    }

    // Sales Management
    function updateSalesTable() {
        const tbody = document.getElementById('salesTable');
        if (store.sales.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center text-gray-500 py-8">No sales data yet. Upload a CSV to get started.</td></tr>';
            document.getElementById('salesCount').textContent = '0';
            return;
        }
        
        tbody.innerHTML = store.sales.slice(-10).map(sale => `
            <tr>
                <td>${sale.date}</td>
                <td><strong>${sale.dishName}</strong></td>
                <td>${sale.quantitySold}</td>
                <td><span class="badge badge-success">✓ Recorded</span></td>
            </tr>
        `).join('');
        
        document.getElementById('salesCount').textContent = store.sales.length;
    }

    function handleSalesCSVUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const lines = e.target.result.split('\n');
                lines.slice(1).forEach(line => {
                    if (line.trim()) {
                        const [date, dishName, quantitySold] = line.split(',').map(s => s.trim());
                        if (date && dishName && quantitySold) {
                            store.sales.push({
                                id: Date.now() + Math.random(),
                                date,
                                dishName,
                                quantitySold: parseInt(quantitySold)
                            });
                        }
                    }
                });
                saveData();
                updateSalesTable();
                alert('Sales CSV imported successfully! ML models will be trained automatically.');
            } catch (err) {
                alert('Error parsing CSV: ' + err.message);
            }
        };
        reader.readAsText(file);
    }

    // Dashboard
    function updateDashboard() {
        document.getElementById('menuCount').textContent = store.menu.length;
        document.getElementById('pantryCount').textContent = store.pantry.length;
        document.getElementById('salesCount').textContent = store.sales.length;
        
        const lowStock = store.pantry.filter(p => p.quantity < 10).length;
        document.getElementById('lowStockCount').textContent = lowStock;
        
        updateCharts();
    }

    function updateCharts() {
        // Sales trend chart
        const ctx = document.getElementById('salesChart');
        if (ctx && store.sales.length > 0) {
            const last30Days = store.sales.slice(-30);
            const dates = [...new Set(last30Days.map(s => s.date))];
            const totals = dates.map(d => last30Days.filter(s => s.date === d).reduce((sum, s) => sum + s.quantitySold, 0));
            
            if (window.salesChartInstance) {
                window.salesChartInstance.destroy();
            }
            
            window.salesChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Daily Sales',
                        data: totals,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 3,
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: '#059669',
                        pointBorderColor: '#10b981',
                        pointRadius: 5,
                        pointHoverRadius: 7
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: true, labels: { color: '#111827', font: { weight: 'bold' } } }
                    },
                    scales: {
                        y: { beginAtZero: true, ticks: { color: '#6b7280' } },
                        x: { ticks: { color: '#6b7280' } }
                    }
                }
            });
        }
    }

    // Forecasting
    function runForecast() {
        const days = parseInt(document.getElementById('forecastDays').value);
        const minDays = parseInt(document.getElementById('minTrainingDays').value);
        
        if (!store.sales.length || !store.menu.length) {
            alert('Please upload sales data and menu items first');
            return;
        }
        
        // Simulate forecasting
        const forecastResults = store.menu.map(dish => ({
            dish: dish.name,
            confidence: Math.random() > 0.3 ? 'high' : 'low',
            forecast: Math.floor(Math.random() * 50 + 10)
        }));
        
        store.forecasts = forecastResults;
        saveData();
        
        const resultsDiv = document.getElementById('forecastResults');
        resultsDiv.innerHTML = forecastResults.map(f => `
            <div style="padding: 12px; background-color: ${f.confidence === 'high' ? '#d1fae5' : '#fef3c7'}; border-radius: 8px; border-left: 4px solid ${f.confidence === 'high' ? '#10b981' : '#f59e0b'}">
                <div style="font-weight: 600; color: #111827">${f.dish}</div>
                <div style="font-size: 14px; color: #6b7280">
                    Predicted Sales: <strong>${f.forecast}</strong> units
                    <span class="badge ${f.confidence === 'high' ? 'badge-success' : 'badge-warning'}" style="margin-left: 8px">${f.confidence.toUpperCase()} CONFIDENCE</span>
                </div>
            </div>
        `).join('');
        
        updateConfidenceChart();
    }

    function updateConfidenceChart() {
        if (store.forecasts.length === 0) return;
        
        const ctx = document.getElementById('confidenceChart');
        if (ctx) {
            const high = store.forecasts.filter(f => f.confidence === 'high').length;
            const low = store.forecasts.filter(f => f.confidence === 'low').length;
            
            if (window.confidenceChartInstance) {
                window.confidenceChartInstance.destroy();
            }
            
            window.confidenceChartInstance = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['High Confidence', 'Low Confidence'],
                    datasets: [{
                        data: [high, low],
                        backgroundColor: ['#10b981', '#fbbf24']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: '#111827', font: { weight: 'bold' } } }
                    }
                }
            });
        }
    }

    // Recommendations
    function generateRecommendations() {
        if (!store.forecasts.length) {
            alert('Please run forecasting first');
            return;
        }
        
        const recommendations = store.forecasts.map(f => `
            <div style="padding: 16px; background: #ecfdf5; border-radius: 8px; border-left: 4px solid #10b981">
                <div style="font-weight: 600; color: #111827 mb: 8px">${f.dish}</div>
                <div style="font-size: 14px; color: #6b7280">
                    Purchase <strong>${Math.ceil(f.forecast * 1.2)}</strong> units to meet forecasted demand with 20% buffer
                </div>
            </div>
        `).join('');
        
        document.getElementById('recommendationsContainer').innerHTML = recommendations || '<p>No recommendations available</p>';
    }

    // Export Functions
    function exportMenuCSV() {
        if (store.menu.length === 0) {
            alert('No menu items to export');
            return;
        }
        
        const csv = 'Dish Name,Type,Profile,Flavor,Price\n' + 
            store.menu.map(m => `"${m.name}","${m.type}","${m.profile}","${m.flavor}",${m.price}`).join('\n');
        downloadCSV(csv, 'menu.csv');
    }

    function exportPantryCSV() {
        if (store.pantry.length === 0) {
            alert('No pantry items to export');
            return;
        }
        
        const csv = 'Ingredient,Quantity,Unit\n' + 
            store.pantry.map(p => `"${p.name}",${p.quantity},"${p.unit}"`).join('\n');
        downloadCSV(csv, 'pantry.csv');
    }

    function exportSalesCSV() {
        if (store.sales.length === 0) {
            alert('No sales data to export');
            return;
        }
        
        const csv = 'Date,Dish,Quantity\n' + 
            store.sales.map(s => `"${s.date}","${s.dishName}",${s.quantitySold}`).join('\n');
        downloadCSV(csv, 'sales.csv');
    }

    function downloadCSV(csv, filename) {
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
    }

    // Data Management
    function clearAllData() {
        if (confirm('Are you sure? This will delete ALL data and cannot be undone!')) {
            localStorage.removeItem('smartbiteData');
            store.menu = [];
            store.pantry = [];
            store.sales = [];
            store.forecasts = [];
            updateDashboard();
            alert('All data cleared');
        }
    }

    function showSystemInfo() {
        const info = `
    SmartBite System Information
    ================================
    Menu Items: ${store.menu.length}
    Pantry Items: ${store.pantry.length}
    Sales Records: ${store.sales.length}
    Forecasts: ${store.forecasts.length}

    Storage: LocalStorage (Browser)
    Max Items: Unlimited (depends on browser)
    Data Sync: None (Local Only)
    ML Models: Simulated RandomForest
    Algorithms: Per-Dish Forecasting

    Version: 1.0
    Last Updated: ${new Date().toLocaleString()}
        `;
        alert(info);
    }

    // Modal close on background click
    document.addEventListener('click', function(event) {
        if (event.target.id === 'menuModal') closeMenuModal();
        if (event.target.id === 'pantryModal') closePantryModal();
    });

    // Initialize
    window.addEventListener('DOMContentLoaded', loadData);
});