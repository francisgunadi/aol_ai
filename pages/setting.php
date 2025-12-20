<div id="settings" class="page">
    <div class="mb-6">
        <h2 class="text-xl font-bold text-gray-900">Settings</h2>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white rounded-lg p-6">
            <h3 class="text-lg font-semibold mb-4">Restaurant Profile</h3>
            <div class="space-y-5">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Restaurant Name</label>
                    <input type="text" id="restaurantName" class="form-input" placeholder="e.g. Pizza Hut">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Year of Establishment</label>
                    <input type="text" id="restaurantYear" class="form-input" placeholder="e.g. 2016">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Customer Capacity</label>
                    <input type="text" id="restaurantCapacity" class="form-input" placeholder="Measured in seats">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Cuisine Specialty</label>
                    <input type="text" id="restaurantCuisine" class="form-input" placeholder="e.g. Italian">
                </div>
                <button class="btn-primary" onclick="saveRestaurantInformation()">Save Restaurant Info</button>
            </div>
        </div>
        
        <div class="bg-white rounded-lg p-6">
            <h3 class="text-lg font-semibold mb-4">Data Management</h3>
            <div class="space-y-3">
                <button class="btn-secondary w-full" onclick="clearAllData()" style="color: #dc2626; border-color: #dc2626;">🗑️ Clear All Data</button>
                <button class="btn-secondary w-full" onclick="showSystemInfo()">ℹ️ System Information</button>
            </div>
        </div>
    </div>

    <div class="bg-amber-50 border-l-4 border-amber-500 p-4 rounded mt-6">
        <p class="text-sm text-gray-700"><strong>⚠️ Important:</strong> All data is stored locally in your browser. Clearing your browser data or using an incognito window will result in data loss. Export regularly!</p>
    </div>
    </div>