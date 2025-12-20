<div id="pantry" class="page">
    <div class="mb-6 flex justify-between items-center">
        <h2 class="text-xl font-bold text-gray-900">Pantry Inventory</h2>
        <div>
            <button class="btn-secondary mr-3" onclick="exportPantryCSV()">📥 Export Pantry</button>
            <button class="btn-primary" onclick="openPantryModal()">+ Add Item</button>
        </div>
    </div>

    <div class="bg-white rounded-lg p-6 mb-6">
        <h3 class="text-lg font-semibold mb-4">Upload Pantry CSV</h3>
        <div class="border-2 border-dashed border-green-300 rounded-lg p-8 text-center">
            <input type="file" id="pantryCSV" accept=".csv" class="hidden" onchange="handlePantryCSVUpload(event)">
            <button class="btn-secondary" onclick="document.getElementById('pantryCSV').click()">📄 Choose CSV File</button>
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
            <tbody id="pantryTable">
                <tr>
                    <td colspan="5" class="text-center text-gray-500 py-8">No pantry items yet. Add one to get started.</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>

<!-- Pantry Modal -->
<div id="pantryModal" class="modal">
    <div class="modal-content">
        <h2 class="text-2xl font-bold mb-6 text-gray-900">Add Pantry Item</h2>
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">Ingredient Name</label>
                <input type="text" id="pantryIngredient" class="form-input" placeholder="e.g., Salmon">
            </div>
            <div class="grid grid-cols-2 gap-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Quantity</label>
                    <input type="number" id="pantryQuantity" class="form-input" placeholder="0" step="0.01">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Unit</label>
                    <select id="pantryUnit" class="form-input">
                        <option>g</option>
                        <option>ml</option>
                        <option>pieces</option>
                        <option>kg</option>
                        <option>l</option>
                    </select>
                </div>
            </div>
            <div class="pt-4">
                <button class="btn-primary w-full" onclick="addPantryItem()">Add Item</button>
                <button class="btn-secondary w-full mt-2" onclick="closePantryModal()">Cancel</button>
            </div>
        </div>
    </div>
</div>