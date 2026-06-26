<?php
declare(strict_types=1);

require __DIR__ . '/api/config.php';

$sqlFile = __DIR__ . ' /../database/inspection_scolaire.sql';
if (!file_exists($sqlFile)) {
    echo json_encode(['error' => 'SQL file not found: ' . $sqlFile]);
    exit(1);
}

$sql = file_get_contents($sqlFile);
if ($sql === false) {
    echo json_encode(['error' => 'Failed to read SQL file']);
    exit(1);
}

$mysqli = new mysqli(DB_HOST, DB_USER, DB_PASS);
if ($mysqli->connect_errno) {
    echo json_encode(['error' => 'Connect error: ' . $mysqli->connect_error]);
    exit(1);
}

// Enable multi statements if disabled (default OK).
$mysqli->multi_query("SET NAMES utf8mb4;");

if ($mysqli->multi_query($sql)) {
    // Consume all results to finish multi_query
    do {
        if ($result = $mysqli->store_result()) {
            $result->free();
        }
    } while ($mysqli->more_results() && $mysqli->next_result());

    echo json_encode(['status' => 'ok', 'message' => 'Import terminé']);
    $mysqli->close();
    exit(0);
} else {
    echo json_encode(['error' => 'Import failed: ' . $mysqli->error]);
    $mysqli->close();
    exit(1);
}

?>
