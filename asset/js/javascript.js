    localStorage.clear()
    // Data Store
    const store = {
        menu: [],
        pantry: [],
        sales: [],
        ingredient: [],
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
            dish_name: document.getElementById('menuDishName').value,
            type: document.getElementById('menuType').value,
            profile: document.getElementById('menuProfile').value,
            flavor: document.getElementById('menuFlavor').value,
            price: parseFloat(document.getElementById('menuPrice').value),
            ingredient: document.getElementById('menuIngredient').value.split(',').map(item => item.trim())
        };

        if (dish.dish_name && !isNaN(dish.price)) {
            store.menu.push(dish);
            saveData();
            updateMenuTable();
            closeMenuModal();
        } else {
            alert('Please fill in all fields');
        }

        updateMenuItem("add", dish.dish_name, dish.type, dish.profile, dish.flavor, dish.price, dish.ingredient);
    }

    function updateMenuTable() {
        const tbody = document.getElementById('menuTable');
        if (store.menu.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-gray-500 py-8">No menu items yet. Add one to get started.</td></tr>';
            return;
        }
        
        tbody.innerHTML = store.menu.map(dish => `
            <tr>
                <td><strong>${dish.dish_name}</strong></td>
                <td>${dish.type}</td>
                <td><span class="badge badge-success">${dish.profile}</span></td>
                <td><span class="badge badge-success">${dish.flavor}</span></td>
                <td>$${dish.price.toFixed(2)}</td>
                <td><span class="text-xs text-gray-500">
                    ${Array.isArray(dish.ingredient) ?
                        dish.ingredient.map(item => `<li>${item}</li>`).join('') : ''
                    }
                </span></td>
                <td>
                    <button onclick="deleteMenuItem('${dish.dish_name}')" class="text-red-600 hover:text-red-800 font-medium">Delete</button>
                </td>
            </tr>
        `).join('');
        
        document.getElementById('menuCount').textContent = store.menu.length;
    }

    function updateMenuItem(action, dish_name, type, profile, flavor, price, ingredient) {
        const formData = new FormData();
        formData.append('action', action);
        formData.append('dish_name', dish_name);
        formData.append('type', type);
        formData.append('profile', profile);
        formData.append('flavor', flavor);
        formData.append('price', price);
        formData.append(
            'ingredient',
            Array.isArray(ingredient) ? ingredient.join(',') : ingredient
        );
    
        fetch('utils/update_menu.php', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error || !data.success) {
                const actionVerb = action === 'delete' ? 'deleting' : 'adding';
                console.error(`Error ${actionVerb} menu item on server:`, data.error || 'Operation failed');
                alert(`Error ${actionVerb} menu item on server: ` + (data.error || 'Operation failed'));
    
                if (action === 'add') {
                    // Remove from local store if add failed
                    store.menu = store.menu.filter(m => m.dish_name !== dish_name);
                    saveData();
                    updateMenuTable();
                } else if (action === 'delete') {
                    // In a more complete app, you might re‑fetch from server here
                }
            } else {
                const actionVerb = action === 'delete' ? 'deleted' : 'added';
                console.log(`Menu item ${actionVerb} on server:`, data.message || 'Operation completed');
            }
        })
        .catch(error => {
            console.error('Network/parse error when updating menu:', error);
        });
    }

    function deleteMenuItem(dish_name) {
        if (!confirm(`Are you sure you want to delete "${dish_name}"?`)) {
            return;
        }

        store.menu = store.menu.filter(m => m.dish_name !== dish_name);
        saveData();
        updateMenuTable();

        updateMenuItem("delete", dish_name, '', '', '', '', '');
    }

    function handleMenuCSVUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        // Show loading state
        const tbody = document.getElementById('menuTable');
        const originalContent = tbody.innerHTML;
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-gray-500 py-8">⏳ Uploading and processing file...</td></tr>';
        
        // Create FormData to upload file
        const formData = new FormData();
        formData.append('menuCSV', file);
        
        // Upload file to server
        fetch('utils/upload_sales.php', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            if (data.success && data.data) {
                // Convert processed JSON data to store format
                const processedData = Array.isArray(data.data) ? data.data : [];
                
                processedData.forEach(record => {
                    // Map the processed data to our store format
                    // Handle different possible column names
                    const dish = {
                        dish_name: record.dish_name || '',
                        type: record.type || '',
                        profile: record.profile || '',
                        flavor: record.flavor || '',
                        price: parseFloat(record.price || 0),
                        ingredient: record.ingredient || []
                    };
                    
                    if (dish.dish_name && !isNaN(dish.price)) {
                        store.menu.push(dish);
                    }
                });
                
                saveData();
                updateMenuTable();
                alert('Menu CSV imported successfully!');
            } else {
                throw new Error('No data received from server');
            }
        })
        .catch(error => {
            console.error('Upload error:', error);
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-red-500 py-8">❌ Error: ' + error.message + '</td></tr>';
            alert('Error uploading file: ' + error.message);
        });
        
        // Reset file input
        event.target.value = '';
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
            ingredient_name: document.getElementById('pantryIngredient').value,
            quantity: parseFloat(document.getElementById('pantryQuantity').value),
            unit: document.getElementById('pantryUnit').value
        };
        
        if (item.ingredient_name && !isNaN(item.quantity)) {
            store.pantry.push(item);
            saveData();
            updatePantryTable();
            closePantryModal();

            updatePantryItem("add", item.ingredient_name, item.quantity, item.unit);
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
            return `
                <tr>
                    <td><strong>${item.ingredient_name}</strong></td>
                    <td>${item.quantity}</td>
                    <td>${item.unit}</td>
                    <td>
                        <button onclick="deletePantryItem('${item.ingredient_name}')" class="text-red-600 hover:text-red-800 font-medium">Delete</button>
                        <button onclick="changePantryQuantity('${item.ingredient_name}', ${item.quantity})" class="text-green-600 hover:text-green-800 font-medium">Update</button>
                    </td>
                </tr>
            `;
        }).join('');
        
        document.getElementById('pantryCount').textContent = store.pantry.length;
    }

    function updatePantryItem(action, ingredient_name, quantity, unit){
        const formData = new FormData();
        formData.append('action', action);
        formData.append('ingredient_name', ingredient_name);
        formData.append('quantity', quantity);
        formData.append("unit", unit);
        
        fetch('utils/update_pantry.php', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error || !data.success) {
                // Revert local change if server update failed
                const actionVerb = action === 'delete' ? 'deleting' : 
                                  action === 'add' ? 'adding' : 'updating';
                console.error(`Error ${actionVerb} from server:`, data.error || 'Operation failed');
                alert(`Error ${actionVerb} item from server: ` + (data.error || 'Operation failed'));
                
                // Remove from local store if add failed
                if (action === 'add') {
                    store.pantry = store.pantry.filter(p => p.ingredient_name !== ingredient_name);
                    saveData();
                    updatePantryTable();
                } else {
                    // Reload data to sync with server for update/delete
                    loadData();
                }
            } else {
                // Success
                const actionVerb = action === 'delete' ? 'deleted' : 
                                  action === 'add' ? 'added' : 'updated';
                console.log(`Successfully ${actionVerb} from server:`, data.message || 'Operation completed');
            }
        })
        .catch(error => {
            console.error('Network/Parse error:', error);
            const actionVerb = action === 'delete' ? 'deleted' : 
                            action === 'add' ? 'added' : 'updated';
            // alert(`Error connecting to server. Item ${actionVerb} locally but may not be synced.`);
        });
    }

    function changePantryQuantity(ingredient_name, quantity){
        const new_quantity = prompt("Update the quantity for ${ingredient_name}", quantity);
        
        if (new_quantity === null) {
            return;
        }

        const parsedQuantity = parseFloat(new_quantity);
        if (isNaN(parsedQuantity) || parsedQuantity < 0) {
            alert('Please enter a valid positive number');
            return;
        }

        const item = store.pantry.find(p => p.ingredient_name === ingredient_name);
        if (!item) {
            alert('Item not found in pantry');
            return;
        }

        item.quantity = parsedQuantity;
        saveData();
        updatePantryTable();

        updatePantryItem("update", ingredient_name, parsedQuantity, '');
    }

    function deletePantryItem(ingredient_name) {
        if (!confirm(`Are you sure you want to delete "${ingredient_name}"?`)) {
            return;
        }

        store.pantry = store.pantry.filter(p => p.ingredient_name !== ingredient_name);
        saveData();
        updatePantryTable();

        updatePantryItem("delete", ingredient_name, 0, '')
    }

    function handlePantryCSVUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        // Show loading state
        const tbody = document.getElementById('pantryTable');
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-gray-500 py-8">⏳ Uploading and processing file...</td></tr>';
        
        // Create FormData to upload file
        const formData = new FormData();
        formData.append('pantryCSV', file);
        
        // Upload file to server
        fetch('utils/upload_sales.php', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            if (data.success && data.data) {
                // Convert processed JSON data to store format
                const processedData = Array.isArray(data.data) ? data.data : [];
                
                processedData.forEach(record => {
                    // Map the processed data to our store format
                    const item = {
                        ingredient_name: record.ingredient_name || record.name || '',
                        quantity: record.quantity || 0,
                        unit: record.unit || ''
                    };
                    store.pantry.push(item);
                });
                
                saveData();
                updatePantryTable();
                alert('Pantry CSV imported successfully!');
            } else {
                throw new Error('No data received from server');
            }
        })
        .catch(error => {
            console.error('Upload error:', error);
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-red-500 py-8">❌ Error: ' + error.message + '</td></tr>';
            alert('Error uploading file: ' + error.message);
        });
        
        // Reset file input
        event.target.value = '';
    }

    // Ingredient Management
    function openIngredientModal() {
        document.getElementById('ingredientModal').classList.add('active');
    }

    function closeIngredientModal() {
        document.getElementById('ingredientModal').classList.remove('active');
        document.getElementById('ingredientIngredient').value = '';
        document.getElementById('ingredientQuantity').value = '';
    }

    function addIngredientItem() {
        const item = {
            ingredient_name: document.getElementById('ingredientIngredient').value,
            quantity: parseFloat(document.getElementById('ingredientQuantity').value),
            unit: document.getElementById('ingredientUnit').value
        };
        
        if (item.ingredient_name && !isNaN(item.quantity)) {
            store.ingredient.push(item);
            saveData();
            updateIngredientTable();
            closeIngredientModal();

            updateIngredientItem("add", item.ingredient_name, item.quantity, item.unit);
        } else {
            alert('Please fill in all fields');
        }
    }

    function updateIngredientTable() {
        const tbody = document.getElementById('ingredientTable');
        if (store.ingredient.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-gray-500 py-8">No ingredient items yet. Add one to get started.</td></tr>';
            return;
        }
        
        tbody.innerHTML = store.ingredient.map(item => {
            return `
                <tr>
                    <td><strong>${item.ingredient_name}</strong></td>
                    <td>${item.quantity}</td>
                    <td>${item.unit}</td>
                    <td>
                        <button onclick="deleteIngredientItem('${item.ingredient_name}')" class="text-red-600 hover:text-red-800 font-medium">Delete</button>
                        <button onclick="changeIngredientQuantity('${item.ingredient_name}', ${item.quantity})" class="text-green-600 hover:text-green-800 font-medium">Update</button>
                    </td>
                </tr>
            `;
        }).join('');
    }

    function updateIngredientItem(action, ingredient_name, quantity, unit){
        const formData = new FormData();
        formData.append('action', action);
        formData.append('ingredient_name', ingredient_name);
        formData.append('quantity', quantity);
        formData.append("unit", unit);
        
        fetch('utils/update_ingredient.php', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error || !data.success) {
                // Revert local change if server update failed
                const actionVerb = action === 'delete' ? 'deleting' : 
                                  action === 'add' ? 'adding' : 'updating';
                console.error(`Error ${actionVerb} from server:`, data.error || 'Operation failed');
                alert(`Error ${actionVerb} item from server: ` + (data.error || 'Operation failed'));
                
                // Remove from local store if add failed
                if (action === 'add') {
                    store.ingredient = store.ingredient.filter(p => p.ingredient_name !== ingredient_name);
                    saveData();
                    updateIngredientTable();
                } else {
                    // Reload data to sync with server for update/delete
                    loadData();
                }
            } else {
                // Success
                const actionVerb = action === 'delete' ? 'deleted' : 
                                  action === 'add' ? 'added' : 'updated';
                console.log(`Successfully ${actionVerb} from server:`, data.message || 'Operation completed');
            }
        })
        .catch(error => {
            console.error('Network/Parse error:', error);
            const actionVerb = action === 'delete' ? 'deleted' : 
                            action === 'add' ? 'added' : 'updated';
            // alert(`Error connecting to server. Item ${actionVerb} locally but may not be synced.`);
        });
    }

    function changeIngredientQuantity(ingredient_name, quantity){
        const new_quantity = prompt("Update the quantity for ${ingredient_name}", quantity);
        
        if (new_quantity === null) {
            return;
        }

        const parsedQuantity = parseFloat(new_quantity);
        if (isNaN(parsedQuantity) || parsedQuantity < 0) {
            alert('Please enter a valid positive number');
            return;
        }

        const item = store.ingredient.find(p => p.ingredient_name === ingredient_name);
        if (!item) {
            alert('Item not found in ingredient');
            return;
        }

        item.quantity = parsedQuantity;
        saveData();
        updateIngredientTable();

        updateIngredientItem("update", ingredient_name, parsedQuantity, '');
    }

    function deleteIngredientItem(ingredient_name) {
        if (!confirm(`Are you sure you want to delete "${ingredient_name}"?`)) {
            return;
        }

        store.ingredient = store.ingredient.filter(p => p.ingredient_name !== ingredient_name);
        saveData();
        updateIngredientTable();

        updateIngredientItem("delete", ingredient_name, 0, '')
    }

    function handleIngredientCSVUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        // Show loading state
        const tbody = document.getElementById('ingredientTable');
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-gray-500 py-8">⏳ Uploading and processing file...</td></tr>';
        
        // Create FormData to upload file
        const formData = new FormData();
        formData.append('ingredientCSV', file);
        
        // Upload file to server
        fetch('utils/upload_sales.php', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            if (data.success && data.data) {
                // Convert processed JSON data to store format
                const processedData = Array.isArray(data.data) ? data.data : [];
                
                processedData.forEach(record => {
                    // Map the processed data to our store format
                    const item = {
                        ingredient_name: record.ingredient_name || record.name || '',
                        quantity: record.quantity || 0,
                        unit: record.unit || ''
                    };
                    store.ingredient.push(item);
                });
                
                saveData();
                updateIngredientTable();
                alert('Ingredient CSV imported successfully!');
            } else {
                throw new Error('No data received from server');
            }
        })
        .catch(error => {
            console.error('Upload error:', error);
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-red-500 py-8">❌ Error: ' + error.message + '</td></tr>';
            alert('Error uploading file: ' + error.message);
        });
        
        // Reset file input
        event.target.value = '';
    }

    // Sales Management
    function updateSalesTable() {
        const tbody = document.getElementById('salesTable');
        if (store.sales.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center text-gray-500 py-8">No sales data yet. Upload a CSV to get started.</td></tr>';
            if (document.getElementById('salesCount')) {
                document.getElementById('salesCount').textContent = '0';
            }
            return;
        }
        
        tbody.innerHTML = store.sales.slice(-10).map(sale => {
            // Handle both old format (dishName, quantitySold) and new format (dish_name, quantity/quantity_sold)
            const dishName = sale.dish_name || '';
            const quantity = sale.quantity || 0;
            const date = sale.date || '';
            
            return `
                <tr>
                    <td>${date}</td>
                    <td><strong>${dishName}</strong></td>
                    <td>${quantity}</td>
                    <td><span class="badge badge-success">✓ Recorded</span></td>
                </tr>
            `;
        }).join('');
        
        if (document.getElementById('salesCount')) {
            document.getElementById('salesCount').textContent = store.sales.length;
        }
    }

    function handleSalesCSVUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        // Show loading state
        const tbody = document.getElementById('salesTable');
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-gray-500 py-8">⏳ Uploading and processing file...</td></tr>';
        
        // Create FormData to upload file
        const formData = new FormData();
        formData.append('salesCSV', file);
        
        // Upload file to server
        fetch('utils/upload_sales.php', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            if (data.success && data.data) {
                // Convert processed JSON data to store format
                const processedData = Array.isArray(data.data) ? data.data : [];
                
                processedData.forEach(record => {
                    // Map the processed data to our store format
                    const sale = {
                        date: record.date || '',
                        dish_name: record.dish_name || '',
                        quantity: record.quantity || 0
                    };
                    store.sales.push(sale);
                });
                
                saveData();
                updateSalesTable();
                alert('Sales CSV imported successfully! ML models will be trained automatically.');
                updateDashboard();
            } else {
                throw new Error('No data received from server');
            }
        })
        .catch(error => {
            console.error('Upload error:', error);
            tbody.innerHTML = '<tr><td colspan="4" class="text-center text-red-500 py-8">❌ Error: ' + error.message + '</td></tr>';
            alert('Error uploading file: ' + error.message);
        });
        
        // Reset file input
        event.target.value = '';
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
            const allDates = [...new Set(store.sales.map(s => s.date))].sort();
            const last30DaysDates = allDates.slice(-30);
            const totals = last30DaysDates.map(d => 
                store.sales.filter(s => s.date === d)
                .reduce((sum, s) => sum + (s.quantity || 0), 0)
            )
            
            if (window.salesChartInstance) {
                window.salesChartInstance.destroy();
            }
            
            window.salesChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: last30DaysDates,
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
    async function runForecast() {
        const days = parseInt(document.getElementById('forecastDays').value);
        
        // if (!store.sales.length || !store.menu.length || !store.ingredient.length || !store.pantry.length) {
        //     alert('Please upload all the necessary first');
        //     return;
        // }

        const resultsDiv = document.getElementById('forecastResults');
        resultsDiv.innerHTML = '<p class=\"text-gray-500 text-sm\">Running forecast and computing ingredient needs...</p>';

        try {
            const response = await fetch('utils/run_forecast.php?days=' + encodeURIComponent(days), {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });

            if (!response.ok) {
                const text = await response.text();
                throw new Error('Forecast request failed: ' + text);
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Forecast script returned an error');
            }

            const ingredients = data.ingredients || [];
            const salesData = data.sales_data || [];

            // Store for potential reuse (e.g. exporting / other views)
            store.forecasts = ingredients;
            store.salesForecast = salesData;
            saveData();

            if (!ingredients.length) {
                resultsDiv.innerHTML = '<p class=\"text-gray-500 text-sm\">No ingredient requirements were generated.</p>';
                return;
            }

            // Build sales summary (per-dish totals)
            let salesSummaryHtml = '';
            if (salesData.length > 0) {
                const salesSummary = salesData.map(dish => {
                    const total = dish.points.reduce((sum, point) => sum + (point.predicted_quantity || 0), 0);
                    return { dish_name: dish.dish_name, total: total };
                });
                
                salesSummaryHtml = `
                    <div style="margin-bottom: 20px; padding: 12px; background-color: #f0f9ff; border-radius: 8px; border-left: 4px solid #3b82f6">
                        <div style="font-weight: 600; color: #111827; margin-bottom: 8px;">Forecasted Sales Summary (${days} days)</div>
                        <div style="font-size: 14px; color: #6b7280; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 8px;">
                            ${salesSummary.map(s => `
                                <div>
                                    <strong>${s.dish_name}:</strong> ${s.total.toFixed(1)} portions
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            }

            // Render ingredient table, highlighting ones that need to be bought
            const rowsHtml = ingredients.map(ing => {
                const needToBuy = ing.status === 'NEED_TO_BUY' || (ing.to_buy && ing.to_buy > 0);
                const rowBg = needToBuy ? '#fef2f2' : '#ecfdf5';
                const borderColor = needToBuy ? '#ef4444' : '#10b981';
                const statusLabel = needToBuy ? 'NEED TO BUY' : 'ENOUGH';

                return `
                    <div style="padding: 12px; background-color: ${rowBg}; border-radius: 8px; border-left: 4px solid ${borderColor}">
                        <div style="font-weight: 600; color: #111827">${ing.ingredient_name}</div>
                        <div style="font-size: 14px; color: #6b7280">
                            Required: <strong>${ing.required_qty.toFixed(2)}</strong> ${ing.unit || ''}
                            &nbsp;|&nbsp;
                            In stock: <strong>${ing.current_stock.toFixed(2)}</strong> ${ing.unit || ''}
                            &nbsp;|&nbsp;
                            To buy: <strong>${ing.to_buy.toFixed(2)}</strong> ${ing.unit || ''}
                            <span class="badge ${needToBuy ? 'badge-danger' : 'badge-success'}" style="margin-left: 8px">
                                ${statusLabel}
                            </span>
                        </div>
                    </div>
                `;
            }).join('');

            resultsDiv.innerHTML = salesSummaryHtml + rowsHtml;

            updateConfidenceChart();
        } catch (err) {
            console.error(err);
            resultsDiv.innerHTML = `<p class=\"text-red-500 text-sm\">Failed to run forecast: ${err.message}</p>`;
        }
    }

    function updateConfidenceChart() {
        if (!store.forecasts.length) return;
        
        const ctx = document.getElementById('confidenceChart');
        if (ctx) {
            // Interpret NEED_TO_BUY as \"high\" urgency, ENOUGH as low
            const needToBuyCount = store.forecasts.filter(f => f.status === 'NEED_TO_BUY').length;
            const enoughCount = store.forecasts.filter(f => f.status === 'ENOUGH').length;
            
            if (window.confidenceChartInstance) {
                window.confidenceChartInstance.destroy();
            }
            
            window.confidenceChartInstance = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Need To Buy', 'Enough Stock'],
                    datasets: [{
                        data: [needToBuyCount, enoughCount],
                        backgroundColor: ['#ef4444', '#10b981']
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
        
        // store.forecasts now holds ingredient-level recommendations from the Python model
        const recommendations = store.forecasts.map(f => `
            <div style="padding: 16px; background: ${f.status === 'NEED_TO_BUY' ? '#fef2f2' : '#ecfdf5'}; border-radius: 8px; border-left: 4px solid ${f.status === 'NEED_TO_BUY' ? '#ef4444' : '#10b981'}">
                <div style="font-weight: 600; color: #111827; margin-bottom: 4px;">${f.ingredient_name}</div>
                <div style="font-size: 14px; color: #6b7280">
                    Required: <strong>${f.required_qty.toFixed(2)}</strong> ${f.unit || ''},
                    In stock: <strong>${f.current_stock.toFixed(2)}</strong> ${f.unit || ''},
                    To buy: <strong>${f.to_buy.toFixed(2)}</strong> ${f.unit || ''}
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
