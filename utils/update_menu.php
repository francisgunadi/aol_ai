<?php
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

// Get the action and ingredient name from POST data
$action = $_POST['action'] ?? '';
$dish_name = $_POST['dish_name'] ?? '';
$ingredient = $_POST['ingredient'] ?? '';
$flavor = $_POST['flavor'] ?? '';
$profile = $_POST['profile'] ?? '';
$price = $_POST['price'] ?? '';
$type = $_POST['type'] ?? '';

if (empty($action) || empty($dish_name || (empty($ingredient) && empty($flavor) && empty($profile) && empty($price) && empty($type) && $action === "add"))) {
    http_response_code(400);
    echo json_encode(['error' => 'Missing required parameters']);
    exit;
}

$csvPath = __DIR__ . '/../upload/csv/menu.csv';
$jsonPath = __DIR__ . '/../upload/cleaned/menu.json';

if ($action === 'delete') {
    // Update JSON file
    if (file_exists($jsonPath)) {
        $jsonData = json_decode(file_get_contents($jsonPath), true);
        if ($jsonData !== null && is_array($jsonData)) {
            $jsonData = array_filter($jsonData, function($item) use ($dish_name) {
                return ($item['dish_name'] ?? '') !== $dish_name;
            });
            $jsonData = array_values($jsonData); // Re-index array
            file_put_contents($jsonPath, json_encode($jsonData, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
        }
    }
    
    // Update CSV file
    if (file_exists($csvPath)) {
        $lines = file($csvPath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        if (!empty($lines)) {
            $header = $lines[0];
            $dataLines = array_slice($lines, 1);
            $delimiter = ';';
            
            // Filter out the line with matching ingredient_name
            $filteredLines = array_filter($dataLines, function($line) use ($dish_name, $delimiter) {
                $parts = str_getcsv($line, $delimiter);
                return (trim($parts[0] ?? '') !== $dish_name);
            });
            
            // Rebuild CSV with header
            $newContent = $header . "\n" . implode("\n", $filteredLines);
            if (!empty($filteredLines)) {
                $newContent .= "\n";
            }
            file_put_contents($csvPath, $newContent);
        }
    }
    
    echo json_encode([
        'success' => true,
        'message' => 'Menu deleted successfully'
    ]);

} else if($action === "add"){
    $menu_exist = false;

    if(file_exists($jsonPath)){
        $jsonData = json_decode(file_get_contents($jsonPath), true);
        if($jsonData === null){
            $jsonData = [];
        }
        
        foreach ($jsonData as $item) {
            if (($item['dish_name'] ?? '') === $dish_name) {
                $menu_exist = true;
                break;
            }
        }

        if(!$menu_exist){
            $newItem = [
            "dish_name" => $dish_name,
            "price" => $price,
            "flavor" => $flavor,
            "profile" => $profile,
            "type" => $type,
            "ingredient" => $ingredient
        ];

        $jsonData[] = $newItem;
        file_put_contents($jsonPath, json_encode($jsonData, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
        }
    }else {
        $newItem = [
            "dish_name" => $dish_name,
            "price" => $price,
            "flavor" => $flavor,
            "profile" => $profile,
            "type" => $type,
            "ingredient" => $ingredient
        ];
        $jsonData = [$newItem];
        file_put_contents($jsonPath, json_encode($jsonData, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    }

    if(file_exists($csvPath)){
        $lines = file($csvPath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        $delimiter = ';';

        if(!empty($lines)){
            $header = $lines[0];
            $dataLines = array_slice($lines, 1);

            $existsInCSV = false;
            foreach ($dataLines as $line) {
                $parts = str_getcsv($line, $delimiter);
                if (trim($parts[0] ?? '') === $dish_name) {
                    $existsInCSV = true;
                    break;
                }
            }

            if (!$existsInCSV && !$menuExists) {
                $newLine = $dish_name . $delimiter . $type . $delimiter . $profile . $delimiter . $flavor . $delimiter . floatval($price) . $delimiter . $ingredient;
                $dataLines[] = $newLine;
                $newContent = $header . "\n" . implode("\n", $dataLines) . "\n";
                file_put_contents($csvPath, $newContent);
            }
        } 

    } else {
        $delimiter = ';';
        $header = "dish_name" . $delimiter . "type" . $delimiter . "profile" . $delimiter . "flavor" . $delimiter . "price" . $delimiter . "ingredient";
        $newLine = $dish_name . $delimiter . $type . $delimiter . $profile . $delimiter . $flavor . $delimiter . floatval($price) . $delimiter . $ingredient;
        $newContent = $header . "\n" . $newLine . "\n";
        file_put_contents($csvPath, $newContent);
    }

    echo json_encode([
        'success' => true,
        'message' => 'Menu added successfully'
    ]);

} else {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid action']);
}
?>