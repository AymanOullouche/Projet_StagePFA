<?php

declare(strict_types=1);

require __DIR__ . '/config.php';

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

$method = $_SERVER['REQUEST_METHOD'];
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH) ?? '/';
$script = $_SERVER['SCRIPT_NAME'] ?? '';
$route = trim(substr($path, strlen($script)), '/');

if ($route === '' || str_starts_with($route, '..')) {
    $base = rtrim(str_replace('\\', '/', dirname($script)), '/');
    $route = str_starts_with($path, $base) ? trim(substr($path, strlen($base)), '/') : '';
    $route = preg_replace('#^index\.php/?#', '', $route) ?? '';
    $route = trim($route, '/');
}

if ($route === '') {
    $route = trim($_GET['route'] ?? '', '/');
}

$parts = $route === '' ? [] : explode('/', $route);

try {
    if ($parts === ['health']) {
        json_response(['status' => 'ok']);
    }

        if ($parts === ['auth', 'login'] && $method === 'POST') {
        login();
    }

    if ($parts === ['auth', 'logout'] && $method === 'POST') {
        logout();
    }

    if ($parts === ['auth', 'me'] && $method === 'GET') {
        who_am_i();
    }

    if ($parts === ['users'] && $method === 'GET') {
        list_users();
    }

    if (($parts[0] ?? '') === 'etablissements') {
        handle_etablissements($method, $parts);
    }

    if (($parts[0] ?? '') === 'inspections') {
        handle_inspections($method, $parts);
    }

    if (($parts[0] ?? '') === 'rapports') {
        handle_rapports($method, $parts);
    }

    json_response(['error' => 'Route introuvable'], 404);
} catch (Throwable $error) {
    json_response(['error' => $error->getMessage()], 500);
}

function input(): array
{
    $raw = file_get_contents('php://input') ?: '';
    $data = json_decode($raw, true);
    return is_array($data) ? $data : [];
}

function json_response(array $data, int $status = 200): void
{
    http_response_code($status);
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

function get_authorization_token(): string
{
    $header = $_SERVER['HTTP_AUTHORIZATION'] ?? $_SERVER['REDIRECT_HTTP_AUTHORIZATION'] ?? '';
    if (!$header) {
        http_response_code(401);
        json_response(['error' => 'Authorization header missing']);
    }

    if (!preg_match('/^Bearer\s+(.+)$/i', trim($header), $matches)) {
        http_response_code(401);
        json_response(['error' => 'Invalid authorization header']);
    }

    return $matches[1];
}

function get_current_session(): array
{
    $token = get_authorization_token();
    $stmt = db()->prepare(
        'SELECT s.token, u.id AS user_id, u.nom, u.email, u.role
         FROM session_tokens s
         INNER JOIN users u ON u.id = s.user_id
         WHERE s.token = :token
         LIMIT 1'
    );
    $stmt->execute(['token' => $token]);
    $session = $stmt->fetch();
    if (!$session) {
        http_response_code(401);
        json_response(['error' => 'Session invalide ou expirée']);
    }

    return $session;
}

function get_current_user(): array
{
    $session = get_current_session();
    return [
        'id' => (int)$session['user_id'],
        'nom' => $session['nom'],
        'email' => $session['email'],
        'role' => $session['role'],
    ];
}

function require_admin(): array
{
    $user = get_current_user();
    if ($user['role'] !== 'ADMIN') {
        http_response_code(403);
        json_response(['error' => 'Accès admin requis']);
    }
    return $user;
}

function login(): void
{
    $data = input();
    $email = trim((string)($data['email'] ?? ''));
    $role = strtoupper(trim((string)($data['role'] ?? 'INSPECTEUR')));

    if ($email === '') {
        json_response(['error' => 'Email obligatoire'], 422);
    }

    $stmt = db()->prepare('SELECT id, nom, email, role FROM users WHERE email = :email LIMIT 1');
    $stmt->execute(['email' => $email]);
    $user = $stmt->fetch();

    if (!$user) {
        $name = $role === 'ADMIN' ? 'Admin Systeme' : 'Inspecteur Principal';
        $role = $role === 'ADMIN' ? 'ADMIN' : 'INSPECTEUR';
        $stmt = db()->prepare('INSERT INTO users (nom, email, role) VALUES (:nom, :email, :role)');
        $stmt->execute(['nom' => $name, 'email' => $email, 'role' => $role]);
        $user = ['id' => (int)db()->lastInsertId(), 'nom' => $name, 'email' => $email, 'role' => $role];
    }

    $token = bin2hex(random_bytes(32));
    $stmt = db()->prepare('INSERT INTO session_tokens (user_id, token) VALUES (:user_id, :token)');
    $stmt->execute(['user_id' => $user['id'], 'token' => $token]);

    json_response([
        'token' => $token,
        'user' => normalize_user($user),
    ]);
}

function logout(): void
{
    $token = get_authorization_token();
    $stmt = db()->prepare('DELETE FROM session_tokens WHERE token = :token');
    $stmt->execute(['token' => $token]);
    json_response(['status' => 'logged_out']);
}

function who_am_i(): void
{
    $user = get_current_user();
    json_response(['data' => normalize_user($user)]);
}

function list_users(): void
{
    require_admin();
    $rows = db()->query('SELECT id, nom, email, role FROM users ORDER BY id ASC')->fetchAll();
    json_response(['data' => array_map('normalize_user', $rows)]);
}

function handle_etablissements(string $method, array $parts): void
{
    get_current_user();
    $id = isset($parts[1]) ? (int)$parts[1] : null;

    if ($method === 'GET' && !$id) {
        $rows = db()->query('SELECT * FROM etablissements ORDER BY id DESC')->fetchAll();
        json_response(['data' => array_map('normalize_etablissement', $rows)]);
    }

    if ($method === 'POST' && !$id) {
        require_admin();
        $data = input();
        $stmt = db()->prepare(
            'INSERT INTO etablissements (nom, type, adresse, ville, region, score)
             VALUES (:nom, :type, :adresse, :ville, :region, :score)'
        );
        $stmt->execute([
            'nom' => trim((string)$data['nom']),
            'type' => (string)$data['type'],
            'adresse' => trim((string)$data['adresse']),
            'ville' => trim((string)$data['ville']),
            'region' => trim((string)$data['region']),
            'score' => (int)($data['score'] ?? 70),
        ]);
        json_response(['data' => find_etablissement((int)db()->lastInsertId())], 201);
    }

    if ($method === 'PUT' && $id) {
        require_admin();
        $data = input();
        $stmt = db()->prepare(
            'UPDATE etablissements
             SET nom = :nom, type = :type, adresse = :adresse, ville = :ville, region = :region
             WHERE id = :id'
        );
        $stmt->execute([
            'id' => $id,
            'nom' => trim((string)$data['nom']),
            'type' => (string)$data['type'],
            'adresse' => trim((string)$data['adresse']),
            'ville' => trim((string)$data['ville']),
            'region' => trim((string)$data['region']),
        ]);
        json_response(['data' => find_etablissement($id)]);
    }

    if ($method === 'DELETE' && $id) {
        require_admin();
        $stmt = db()->prepare('DELETE FROM etablissements WHERE id = :id');
        $stmt->execute(['id' => $id]);
        json_response(['deleted' => true]);
    }

    json_response(['error' => 'Action etablissement invalide'], 405);
}

function handle_inspections(string $method, array $parts): void
{
    if ($method === 'GET' && count($parts) === 1) {
        get_current_user();
        $rows = db()->query(
            'SELECT i.*, e.nom AS etablissement
             FROM inspections i
             INNER JOIN etablissements e ON e.id = i.etablissement_id
             ORDER BY i.date_inspection DESC, i.id DESC'
        )->fetchAll();
        json_response(['data' => array_map('normalize_inspection', $rows)]);
    }

    if ($method === 'POST' && count($parts) === 1) {
        get_current_user();
        $data = input();
        $stmt = db()->prepare(
            'INSERT INTO inspections (etablissement_id, salle, statut, date_inspection, score_global, anomalies)
             VALUES (:etablissement_id, :salle, :statut, :date_inspection, :score_global, :anomalies)'
        );
        $stmt->execute([
            'etablissement_id' => (int)$data['etablissementId'],
            'salle' => trim((string)$data['salle']),
            'statut' => (string)($data['statut'] ?? 'TERMINEE'),
            'date_inspection' => (string)($data['dateInspection'] ?? date('Y-m-d')),
            'score_global' => (int)($data['scoreGlobal'] ?? 0),
            'anomalies' => (int)($data['anomalies'] ?? 0),
        ]);
        json_response(['data' => find_inspection((int)db()->lastInsertId())], 201);
    }

    json_response(['error' => 'Action inspection invalide'], 405);
}

function handle_rapports(string $method, array $parts): void
{
    if ($method === 'GET' && count($parts) === 1) {
        get_current_user();
        $rows = db()->query('SELECT * FROM rapports ORDER BY date_generation DESC, id DESC')->fetchAll();
        json_response(['data' => array_map('normalize_rapport', $rows)]);
    }

    if ($method === 'POST' && count($parts) === 1) {
        get_current_user();
        $data = input();
        $stmt = db()->prepare(
            'INSERT INTO rapports (inspection_id, titre, etablissement, date_generation, statut, anomalies)
             VALUES (:inspection_id, :titre, :etablissement, :date_generation, :statut, :anomalies)'
        );
        $stmt->execute([
            'inspection_id' => $data['inspectionId'] ?? null,
            'titre' => trim((string)$data['titre']),
            'etablissement' => trim((string)$data['etablissement']),
            'date_generation' => (string)($data['dateGeneration'] ?? date('Y-m-d')),
            'statut' => (string)($data['statut'] ?? 'Pret'),
            'anomalies' => (int)($data['anomalies'] ?? 0),
        ]);
        json_response(['data' => find_rapport((int)db()->lastInsertId())], 201);
    }

    json_response(['error' => 'Action rapport invalide'], 405);
}

function find_etablissement(int $id): array
{
    $stmt = db()->prepare('SELECT * FROM etablissements WHERE id = :id');
    $stmt->execute(['id' => $id]);
    $row = $stmt->fetch();
    if (!$row) {
        json_response(['error' => 'Etablissement introuvable'], 404);
    }
    return normalize_etablissement($row);
}

function find_inspection(int $id): array
{
    $stmt = db()->prepare(
        'SELECT i.*, e.nom AS etablissement
         FROM inspections i
         INNER JOIN etablissements e ON e.id = i.etablissement_id
         WHERE i.id = :id'
    );
    $stmt->execute(['id' => $id]);
    $row = $stmt->fetch();
    if (!$row) {
        json_response(['error' => 'Inspection introuvable'], 404);
    }
    return normalize_inspection($row);
}

function find_rapport(int $id): array
{
    $stmt = db()->prepare('SELECT * FROM rapports WHERE id = :id');
    $stmt->execute(['id' => $id]);
    $row = $stmt->fetch();
    if (!$row) {
        json_response(['error' => 'Rapport introuvable'], 404);
    }
    return normalize_rapport($row);
}

function normalize_user(array $row): array
{
    return [
        'id' => (int)$row['id'],
        'nom' => $row['nom'],
        'email' => $row['email'],
        'role' => $row['role'],
    ];
}

function normalize_etablissement(array $row): array
{
    return [
        'id' => (int)$row['id'],
        'nom' => $row['nom'],
        'type' => $row['type'],
        'adresse' => $row['adresse'],
        'ville' => $row['ville'],
        'region' => $row['region'],
        'score' => (int)$row['score'],
    ];
}

function normalize_inspection(array $row): array
{
    return [
        'id' => (int)$row['id'],
        'etablissementId' => (int)$row['etablissement_id'],
        'etablissement' => $row['etablissement'],
        'salle' => $row['salle'],
        'statut' => $row['statut'],
        'dateInspection' => $row['date_inspection'],
        'scoreGlobal' => (int)$row['score_global'],
        'anomalies' => (int)$row['anomalies'],
    ];
}

function normalize_rapport(array $row): array
{
    return [
        'id' => (int)$row['id'],
        'inspectionId' => isset($row['inspection_id']) ? (int)$row['inspection_id'] : null,
        'titre' => $row['titre'],
        'etablissement' => $row['etablissement'],
        'dateGeneration' => $row['date_generation'],
        'statut' => $row['statut'],
        'anomalies' => (int)$row['anomalies'],
    ];
}
