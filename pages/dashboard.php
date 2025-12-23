<div id="dashboard" class="page active">
    <h2 class="text-4xl font-bold text-gray-900 mb-6" id="welcomeMessage">Welcome!</h2>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="stat-card">
            <h3>Total Menu Items</h3>
            <div class="number" id="menuCount">0</div>
        </div>
        <div class="stat-card">
            <h3>Pantry Ingredients</h3>
            <div class="number" id="pantryCount">0</div>
        </div>
        <div class="stat-card">
            <h3>Sales Records</h3>
            <div class="number" id="salesCount">0</div>
        </div>
        <div class="stat-card">
            <h3>Low Stock Items</h3>
            <div class="number" id="lowStockCount">0</div>
            <p class="text-xs text-gray-500 mt-2">⚠️ Needs attention</p>
        </div>
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white rounded-12 p-6 shadow-sm">
            <h2 class="text-lg font-bold text-gray-900 mb-4">Sales Trend (Last 30 Days)</h2>
            <div class="chart-container">
                <canvas id="salesChart"></canvas>
            </div>
        </div>
        <div class="bg-white rounded-12 p-6 shadow-sm">
            <h2 class="text-lg font-bold text-gray-900 mb-4">Top Performing Dishes</h2>
            <div id="topDishes" class="space-y-3">
                <p class="text-gray-500 text-sm">No sales data available yet</p>
            </div>
        </div>
    </div>
</div>