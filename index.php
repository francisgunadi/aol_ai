<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartBite - Restaurant Inventory Intelligence</title>
    <?php include "asset/css/style.php" ?>
    <script src="asset/js/javascript.js"></script>
</head>
<body>
    <div class="flex h-screen overflow-hidden">
        <!-- Sidebar Navigation -->
        <?php include "utils/navbar.php" ?>

        <!-- Main Content -->
        <div class="flex-1 flex flex-col overflow-hidden">
            <!-- Header -->
            <?php include "utils/header.php" ?>

            <!-- Content Area -->
            <div class="flex-1 overflow-y-auto p-8 bg-gray-50">
                <!-- Dashboard Page -->
                <?php include "pages/dashboard.php" ?>

                <!-- Menu Management Page -->
                <?php include "pages/menu.php" ?>

                <!-- Pantry Management Page -->
                <?php include "pages/pantry.php" ?>

                <!-- Ingredients Management Page -->
                <?php include "pages/ingredients.php" ?>

                <!-- Sales Upload Page -->
                <?php include "pages/salesUpload.php"?>

                <!-- Forecasting Page -->
                <?php include "pages/forecasting.php"?>

                <!-- Recommendations Page -->
                <?php include "pages/recommendation.php"?>

                <!-- Settings Page -->
                <?php include "pages/setting.php"?>

            </div>
        </div>
    </div>
</body>
<script>
    // Page Navigation
    function showPage(pageName) {
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        document.getElementById(pageName).classList.add('active');

        document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
        event.target.closest('.nav-item')?.classList.add('active');

        const titles = {
            dashboard: 'Dashboard',
            menu: 'Menu Management',
            pantry: 'Pantry Inventory',
            sales: 'Sales Upload',
            forecast: 'Sales Forecasting',
            recommendations: 'Ingredient Recommendations',
            settings: 'Settings & Export'
        };

        document.getElementById('pageTitle').textContent = titles[pageName];
        
        if (pageName === 'dashboard') updateDashboard();
        if (pageName === 'menu') updateMenuTable();
        if (pageName === 'pantry') updatePantryTable();
        if (pageName === 'ingredient') updateIngredientTable();
        if (pageName === 'sales') updateSalesTable();
        if (pageName === 'forecast'){
            forecastExportButton = document.getElementById('forecastExportButton');
            forecastExportButton.style.display = 'none';
            updateForecast();
        }
        if(pageName === 'settings') loadRestaurantInformation();
    }
</script>
</html>