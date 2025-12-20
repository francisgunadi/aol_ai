<div id="menu" class="page">
    <div class="mb-6 flex justify-between items-center">
        <h2 class="text-xl font-bold text-gray-900">Menu Items</h2>
        <div>
            <button class="btn-secondary mr-3" onclick="exportMenuCSV()">📥 Export Menu</button>
            <button class="btn-primary" onclick="openMenuModal()">+ Add Menu Item</button>
        </div>
    </div>
    <div class="bg-white rounded-lg p-6 mb-6">
        <h3 class="text-lg font-semibold mb-4">Upload Menu CSV</h3>
        <div class="border-2 border-dashed border-green-300 rounded-lg p-8 text-center">
            <input type="file" id="menuCSV" accept=".csv" class="hidden" onchange="handleMenuCSVUpload(event)">
            <button class="btn-secondary" onclick="document.getElementById('menuCSV').click()">📄 Choose CSV File</button>
            <p class="text-gray-500 text-sm mt-3">CSV Format: dish_name, type, profile, flavor, price, ingredient, amount, unit</p>
        </div>
    </div>
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Dish Name</th>
                    <th>Type</th>
                    <th>Profile</th>
                    <th>Flavor</th>
                    <th>Price</th>
                    <th>Ingredients</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody id="menuTable">
                <tr>
                    <td colspan="7" class="text-center text-gray-500 py-8">No menu items yet. Add one to get started.</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>

<!-- menu modal -->
<div id="menuModal" class="modal">
    <div class="modal-content">
        <h2 class="text-2xl font-bold mb-6 text-gray-900">Add Menu Item</h2>
        <div class="space-y-5">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Dish Name</label>
                <input type="text" id="menuDishName" class="form-input" placeholder="e.g., Grilled Salmon">
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Type</label>
                    <select id="menuType" class="form-input">
                        <option>Classic</option>
                        <option>Veggie</option>
                        <option>Supreme</option>
                        <option>Chicken</option>
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Price</label>
                    <input type="number" id="menuPrice" class="form-input" placeholder="0.00" step="0.01">
                </div>
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Profile</label>
                    <select id="menuProfile" class="form-input">
                        <option>Balanced</option>
                        <option>Light</option>
                        <option>Rich</option>
                        <option>Savory</option>
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Flavor</label>
                    <select id="menuFlavor" class="form-input">
                        <option>Mild</option>
                        <option>Fresh</option>
                        <option>Bold</option>
                    </select>
                </div>
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Dish Ingredients</label>
                <input type="text" id="menuIngredient" class="form-input" placeholder="e.g., Tomatoes, Olives">
            </div>
            <div class="pt-4">
                <button class="btn-primary w-full" onclick="addMenuItem()">Add Item</button>
                <button class="btn-secondary w-full mt-2" onclick="closeMenuModal()">Cancel</button>
            </div>
        </div>
    </div>
</div>