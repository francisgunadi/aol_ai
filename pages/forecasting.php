 <div id="forecast" class="page">
    <div class="mb-6">
        <h2 class="text-xl font-bold text-gray-900">Sales Forecasting</h2>
        <p class="text-gray-500 text-sm mt-1">Forecast future sales and see total ingredient needs for the selected period.</p>
    </div>
    
    <div class="bg-white rounded-lg p-6 mb-6">
        <h3 class="text-lg font-semibold mb-4">Forecast Settings</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Forecast Days</label>
                <input type="number" id="forecastDays" class="form-input" value="7" min="1" max="365">
            </div>
            <div class="flex items-end">
                <button class="btn-primary w-full" onclick="runForecast()">🔮 Run Forecast</button>
            </div>
        </div>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white rounded-lg p-6">
            <h3 class="text-lg font-semibold mb-4">Ingredient Requirements</h3>
            <div id="forecastResults" class="space-y-3">
                <p class="text-gray-500 text-sm">Configure the horizon in days and run the forecast to see which ingredients you'll need and what to buy.</p>
            </div>
        </div>
        
        <div class="bg-white rounded-lg p-6">
            <h3 class="text-lg font-semibold mb-4">Model Confidence</h3>
            <div class="chart-container">
                <canvas id="confidenceChart"></canvas>
            </div>
        </div>
    </div>
</div>