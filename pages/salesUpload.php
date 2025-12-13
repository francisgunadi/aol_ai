<div id="sales" class="page">
    <div class="mb-6">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Sales Data Upload</h2>
    </div>
    
    <div class="bg-white rounded-lg p-6 mb-6">
        <h3 class="text-lg font-semibold mb-4">Upload Sales CSV</h3>
        <div class="border-2 border-dashed border-green-300 rounded-lg p-8 text-center">
            <input type="file" id="salesCSV" accept=".csv" class="hidden" onchange="handleSalesCSVUpload(event)">
            <button class="btn-secondary" onclick="document.getElementById('salesCSV').click()">📄 Choose CSV File</button>
            <p class="text-gray-500 text-sm mt-3">CSV Format: date, dish_name, quantity_sold</p>
            <p class="text-gray-400 text-xs mt-2">Date Format: YYYY-MM-DD</p>
        </div>
    </div>
    
    <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded mb-6">
        <p class="text-sm text-gray-700"><strong>📌 Note:</strong> Uploading sales data will automatically train ML models for each dish. This may take up to 20 seconds for 30+ dishes.</p>
    </div>
    
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Dish</th>
                    <th>Quantity Sold</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody id="salesTable">
                <tr>
                    <td colspan="4" class="text-center text-gray-500 py-8">No sales data yet. Upload a CSV to get started.</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>