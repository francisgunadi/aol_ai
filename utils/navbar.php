<div class="sidebar w-64 overflow-y-auto">
    <div class="p-8">
        <div class="flex items-center gap-3 mb-8 nav-item" onclick="showPage('dashboard')">
            <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
                <span style="color: var(--deep-green); font-weight: bold; font-size: 20px;">🍴</span>
            </div>
            <h1 class="text-white font-bold text-xl">SmartBite</h1>
        </div>
        <nav class="space-y-2">
            <div class="nav-item active" onclick="showPage('dashboard')">
                <span class="font-medium">Dashboard</span>
            </div>
            <div class="nav-item" onclick="showPage('menu')">
                <span class="font-medium">Menu Management</span>
            </div>
            <div class="nav-item" onclick="showPage('pantry')">
                <span class="font-medium">Pantry Inventory</span>
            </div>
            <div class="nav-item" onclick="showPage('sales')">
                <span class="font-medium">Sales Upload</span>
            </div>
            <div class="nav-item" onclick="showPage('forecast')">
                <span class="font-medium">Forecasting</span>
            </div>
            <div class="nav-item" onclick="showPage('recommendations')">
                <span class="font-medium">Recommendations</span>
            </div>
            <div class="nav-item" onclick="showPage('settings')">
                <span class="font-medium">Settings</span>
            </div>
        </nav>
    </div>
</div>