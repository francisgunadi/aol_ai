<div id="ingredient" class="page">
    <div class="mb-6 flex justify-between items-center">
        <h2 class="text-xl font-bold text-gray-900">Ingredient Inventory</h2>
        <div>
            <button class="btn-secondary mr-3" onclick="exportIngredientCSV()">📥 Export Ingredients list</button>
            <button class="btn-primary" onclick="openIngredientModal()">+ Add Item</button>
        </div>
    </div>

    <div class="bg-white rounded-lg p-6 mb-6">
        <h3 class="text-lg font-semibold mb-4">Upload Ingredients CSV</h3>
        <div class="border-2 border-dashed border-green-300 rounded-lg p-8 text-center">
            <input type="file" id="ingredientCSV" accept=".csv" class="hidden" onchange="handleIngredientCSVUpload(event)">
            <button class="btn-secondary" onclick="document.getElementById('ingredientCSV').click()">📄 Choose CSV File</button>
            <p class="text-gray-500 text-sm mt-3">CSV Format: ingredient_name, quantity, unit</p>
        </div>
    </div>

    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Ingredient</th>
                    <th>Quantity</th>
                    <th>Unit</th>
                    <th colspan="2">Actions</th>
                </tr>
            </thead>
            <tbody id="ingredientTable">
                <tr>
                    <td colspan="5" class="text-center text-gray-500 py-8">No ingredients yet. Add one to get started.</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>

<!-- Ingredient Modal -->
<div id="ingredientModal" class="modal">
    <div class="modal-content">
        <h2 class="text-2xl font-bold mb-6 text-gray-900">Add Ingredient</h2>
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Ingredient Name</label>
                <input type="text" id="ingredientIngredient" class="form-input" placeholder="e.g., Salmon">
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
                    <input type="number" id="ingredientQuantity" class="form-input" placeholder="0" step="0.01">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Unit</label>
                    <select id="ingredientUnit" class="form-input">
                        <option>g</option>
                        <option>ml</option>
                        <option>pieces</option>
                        <option>kg</option>
                        <option>l</option>
                    </select>
                </div>
            </div>
            <div class="pt-4">
                <button class="btn-primary w-full" onclick="addIngredientItem()">Add Ingredient</button>
                <button class="btn-secondary w-full mt-2" onclick="closeIngredientModal()">Cancel</button>
            </div>
        </div>
    </div>
</div>