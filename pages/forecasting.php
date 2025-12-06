 <div id="forecast" class="page">
    <div class="mb-6">
        <h2 class="text-xl font-bold text-gray-900">Sales Forecasting</h2>
        <p class="text-gray-500 text-sm mt-1">Predict future dish sales using machine learning</p>
    </div>
    
    <div class="bg-white rounded-lg p-6 mb-6">
        <h3 class="text-lg font-semibold mb-4">Forecast Settings</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Forecast Days</label>
                <input type="number" id="forecastDays" class="form-input" value="7" min="1" max="30">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Minimum Training Days</label>
                <input type="number" id="minTrainingDays" class="form-input" value="10" min="1">
            </div>
            <div class="flex items-end">
                <button class="btn-primary w-full" onclick="runForecast()">🔮 Run Forecast</button>
            </div>
        </div>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white rounded-lg p-6">
            <h3 class="text-lg font-semibold mb-4">Forecast Results</h3>
            <div id="forecastResults" class="space-y-3">
                <p class="text-gray-500 text-sm">Configure settings and run forecast to see results</p>
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