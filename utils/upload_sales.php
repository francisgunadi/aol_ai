<?php
header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

// Determine file type from form field name (salesCSV, pantryCSV, menuCSV)
$fileType = null;
$fileKey = null;

if (isset($_FILES['salesCSV']) && $_FILES['salesCSV']['error'] === UPLOAD_ERR_OK) {
    $fileType = 'sales';
    $fileKey = 'salesCSV';
} elseif (isset($_FILES['pantryCSV']) && $_FILES['pantryCSV']['error'] === UPLOAD_ERR_OK) {
    $fileType = 'pantry';
    $fileKey = 'pantryCSV';
} elseif (isset($_FILES['menuCSV']) && $_FILES['menuCSV']['error'] === UPLOAD_ERR_OK) {
    $fileType = 'menu';
    $fileKey = 'menuCSV';
} else {
    http_response_code(400);
    echo json_encode(['error' => 'No file uploaded or upload error']);
    exit;
}

$uploadDir = __DIR__ . '/../upload/csv/';
$cleanedDir = __DIR__ . '/../upload/cleaned/';

// Create directories if they don't exist
if (!is_dir($uploadDir)) {
    mkdir($uploadDir, 0777, true);
}
if (!is_dir($cleanedDir)) {
    mkdir($cleanedDir, 0777, true);
}

$file = $_FILES[$fileKey];
$fileName = basename($file['name']);
$fileExtension = strtolower(pathinfo($fileName, PATHINFO_EXTENSION));

// Validate file extension
if ($fileExtension !== 'csv') {
    http_response_code(400);
    echo json_encode(['error' => 'Invalid file type. Only CSV files are allowed.']);
    exit;
}

// Generate filename based on file type
$uniqueFileName = $fileType . '.csv';
$uploadPath = $uploadDir . $uniqueFileName;

if(file_exists($uploadPath) && $fileType === 'sales'){
    $uplaodedContent = file_get_contents($file['tmp_name']);
    $lines = explode("\n", $uplaodedContent);

    if(count($lines)>1){
        $dataToAppend = implode("\n", array_slice($lines, 1));
        $dataToAppend = rtrim($dataToAppend);

        if(!empty($dataToAppend)){
            $existingContent = file_get_contents($uploadPath);
            if(substr($existingContent,-1)!== "\n") {
                $dataToAppend = "\n" . $dataToAppend;
            }
            file_put_contents($uploadPath, $dataToAppend, FILE_APPEND);
        }
    }
}else{
    // Move uploaded file
    if (!move_uploaded_file($file['tmp_name'], $uploadPath)) {
        http_response_code(500);
        echo json_encode(['error' => 'Failed to save uploaded file']);
        exit;
    }
}



// Process file with Python script
// Use absolute path and correct subdirectory (this file lives in utils/)
$pythonScript = __DIR__ . '/dataProcessing/readFileSales.py';
$nameWithoutExt = pathinfo($uniqueFileName, PATHINFO_FILENAME);

// Convert Windows paths to forward slashes for Python
$uploadPathForPython = str_replace('\\', '/', $uploadPath);
$pythonScriptForPython = str_replace('\\', '/', $pythonScript);

// Execute Python script using the venv interpreter
// Use escapeshellarg to keep the Windows path intact (escapeshellcmd would strip backslashes)
$pythonCmd = 'C:\Users\Lenovo\Documents\Riccy\uni\AI\aol2\req\Scripts\python.exe';
$command = escapeshellarg($pythonCmd) . ' ' . escapeshellarg($pythonScriptForPython) . ' ' . escapeshellarg($uploadPathForPython) . ' ' . escapeshellarg($nameWithoutExt);
$output = [];
$returnVar = 0;
exec($command . ' 2>&1', $output, $returnVar);

if ($returnVar !== 0) {
    http_response_code(500);
    echo json_encode([
        'error' => 'Failed to process file with Python',
        'details' => implode("\n", $output)
    ]);
    exit;
}

// Read the generated JSON file
$jsonPath = $cleanedDir . $nameWithoutExt . '.json';
if (!file_exists($jsonPath)) {
    http_response_code(500);
    echo json_encode(['error' => 'JSON file was not created']);
    exit;
}

$jsonData = json_decode(file_get_contents($jsonPath), true);

if ($jsonData === null) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to parse JSON file']);
    exit;
}

// Return success with data
echo json_encode([
    'success' => true,
    'message' => 'File uploaded and processed successfully',
    'data' => $jsonData,
    'filename' => $uniqueFileName
]);
?>

