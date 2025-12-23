<?php
header('Content-Type: application/json');

// Allow only GET or POST
if ($_SERVER['REQUEST_METHOD'] !== 'GET' && $_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
    exit;
}

// Read forecast horizon in DAYS from query or POST, default to 7
$days = 7;
if (isset($_GET['days'])) {
    $days = (int) $_GET['days'];
} elseif (isset($_POST['days'])) {
    $days = (int) $_POST['days'];
}

if ($days <= 0) {
    $days = 7;
}

// Build paths
$pythonScript = __DIR__ . '/forecast.py';

if (!file_exists($pythonScript)) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'Forecast script not found']);
    exit;
}

// Use the same virtualenv Python interpreter as upload_sales.php
$pythonCmd = 'C:\\Users\\Lenovo\\Documents\\Riccy\\uni\\AI\\aol2\\req\\Scripts\\python.exe';

// Convert paths for Python
$pythonScriptForPython = str_replace('\\', '/', $pythonScript);

$command = escapeshellarg($pythonCmd) . ' ' . escapeshellarg($pythonScriptForPython) . ' --days ' . (int)$days;

$output = [];
$returnVar = 0;
exec($command . ' 2>&1', $output, $returnVar);

if ($returnVar !== 0) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => 'Failed to run forecast script',
        'details' => implode("\n", $output),
    ]);
    exit;
}

$jsonRaw = implode("\n", $output);
$data = json_decode($jsonRaw, true);

if ($data === null) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => 'Failed to parse forecast JSON',
        'details' => $jsonRaw,
    ]);
    exit;
}

// If Python returned an error payload with success=false, propagate it
if (isset($data['success']) && $data['success'] === false) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => $data['error'] ?? 'Forecast script reported an error',
    ]);
    exit;
}

// Normal success path
$ingredients = $data['ingredients'] ?? [];
$salesData = $data['sales_data'] ?? [];

echo json_encode([
    'success' => true,
    'ingredients' => $ingredients,
    'sales_data' => $salesData
]);

?>
