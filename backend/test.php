<?php
try {
    $pdo = new PDO('mysql:host=127.0.0.1;dbname=inspection_scolaire;charset=utf8mb4', 'root', '1234', [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    ]);
    echo json_encode(['status' => 'ok', 'databases' => $pdo->query('SHOW DATABASES')->fetchAll()]);
} catch (Exception $e) {
    echo json_encode(['error' => $e->getMessage()]);
}
?>