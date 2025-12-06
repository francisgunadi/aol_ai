<div id="settings" class="page">
    <div class="mb-6">
        <h2 class="text-xl font-bold text-gray-900">Settings & Export</h2>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white rounded-lg p-6">
            <h3 class="text-lg font-semibold mb-4">Data Export</h3>
            <div class="space-y-3">
                <button class="btn-secondary w-full" onclick="exportMenuCSV()">📥 Export Menu</button>
                <button class="btn-secondary w-full" onclick="exportPantryCSV()">📥 Export Pantry</button>
                <button class="btn-secondary w-full" onclick="exportSalesCSV()">📥 Export Sales</button>
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