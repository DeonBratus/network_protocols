import socket

def send_raw_http_request():
    host = "109.167.241.225"
    port = 8001
    path = "/http_example/give_me_five/?wday=1&student=3"

    request = (
        f"GET {path} HTTP/1.0\r\n"
        f"REQUEST_AGENT: ITMO student\r\n"
        f"COURSE: Net Protocols\r\n"
        f"Host: \r\n"
        f"\r\n"
    )

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(request.encode())
        
        # Получаем данные частями
        response = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk

    # Пробуем декодировать с учетом возможных кодировок
    try:
        decoded_response = response.decode('utf-8')
    except UnicodeDecodeError:
        try:
            # Попытка декодирования как Windows-1251 (для кириллических символов)
            decoded_response = response.decode('cp1251')
        except UnicodeDecodeError:
            # Экстренный вариант: пропуск недопустимых символов
            decoded_response = response.decode('utf-8', errors='ignore')
    
    print(decoded_response)

send_raw_http_request()