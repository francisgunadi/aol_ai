<?php
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

// Get the action and ingredient name from POST data
$action = $_POST['action'] ?? '';
$ingredient_name = $_POST['ingredient_name'] ?? '';
$quantity = $_POST['quantity'] ?? '';
$unit = $_POST['unit'] ?? '';

if (empty($action) || empty($ingredient_name || (empty($quantity) && $action === "update") || (empty($unit) && $action === "add"))) {
    http_response_code(400);
    echo json_encode(['error' => 'Missing required parameters']);
    exit;
}

$csvPath = __DIR__ . '/../upload/csv/ingredient.csv';
$jsonPath = __DIR__ . '/../upload/cleaned/ingredient.json';

if ($action === 'delete') {
    // Update JSON file
    if (file_exists($jsonPath)) {
        $jsonData = json_decode(file_get_contents($jsonPath), true);
        if ($jsonData !== null && is_array($jsonData)) {
            $jsonData = array_filter($jsonData, function($item) use ($ingredient_name) {
                return ($item['ingredient_name'] ?? '') !== $ingredient_name;
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
            $filteredLines = array_filter($dataLines, function($line) use ($ingredient_name, $delimiter) {
                $parts = str_getcsv($line, $delimiter);
                return (trim($parts[0] ?? '') !== $ingredient_name);
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
        'message' => 'Pantry item deleted successfully'
    ]);
} else if($action === "update"){
    if (file_exists($jsonPath)) {
        $jsonData = json_decode(file_get_contents($jsonPath), true);
        if ($jsonData !== null && is_array($jsonData)) {
            foreach ($jsonData as &$item) {
                if (($item['ingredient_name'] ?? '') === $ingredient_name) {
                    $item['quantity'] = floatval($quantity);
                    break;
                }
            }
            unset($item);
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

            $updatedLines = array_map(function($line) use ($ingredient_name, $quantity, $delimiter) {
                $parts = str_getcsv($line, $delimiter);
                if (trim($parts[0] ?? '') === $ingredient_name) {
                    // Update quantity (index 1) while keeping ingredient_name (0) and unit (2)
                    $parts[1] = floatval($quantity);
                    return implode($delimiter, $parts);
                }
                return $line;
            }, $dataLines);
            
            // Rebuild CSV with header
            $newContent = $header . "\n" . implode("\n", $updatedLines) . "\n";
            file_put_contents($csvPath, $newContent);
        }
    }

    echo json_encode([
        'success' => true,
        'message' => 'Pantry item quantity updated successfully'
    ]);
} else if($action === "add"){
    $ingredient_exist = false;

    if(file_exists($jsonPath)){
        $jsonData = json_decode(file_get_contents($jsonPath), true);
        if($jsonData === null){
            $jsonData = [];
        }
        
        foreach ($jsonData as $item) {
            if (($item['ingredient_name'] ?? '') === $ingredient_name) {
                $ingredient_exist = true;
                break;
            }
        }

        if(!$ingredient_exist){
            $newItem = [
            "ingredient_name" => $ingredient_name,
            "quantity" => $quantity,
            "unit" => $unit
        ];

        $jsonData[] = $newItem;
        file_put_contents($jsonPath, json_encode($jsonData, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
        }
    }else {
        $newItem = [
            'ingredient_name' => $ingredient_name,
            'quantity' => floatval($quantity),
            'unit' => $unit
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
                if (trim($parts[0] ?? '') === $ingredient_name) {
                    $existsInCSV = true;
                    break;
                }
            }

            if (!$existsInCSV && !$ingredientExists) {
                $newLine = $ingredient_name . $delimiter . floatval($quantity) . $delimiter . $unit;
                $dataLines[] = $newLine;
                $newContent = $header . "\n" . implode("\n", $dataLines) . "\n";
                file_put_contents($csvPath, $newContent);
            }
        } 

    } else {
        $delimiter = ';';
        $header = "ingredient_name" . $delimiter . "quantity" . $delimiter . "unit";
        $newLine = $ingredient_name . $delimiter . floatval($quantity) . $delimiter . $unit;
        $newContent = $header . "\n" . $newLine . "\n";
        file_put_contents($csvPath, $newContent);
    }

    echo json_encode([
        'success' => true,
        'message' => 'Pantry item quantity added successfully'
    ]);

} else {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid action']);
}
?>