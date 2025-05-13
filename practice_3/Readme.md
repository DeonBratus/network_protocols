```python
IP_ADDR = "109.167.241.225"
PORT = 6340
MAX_PACKETS = 10
STUDENT_NUMBER = 3
```
Определение констант:
- IP-адрес и порт сервера
- Максимальное количество собираемых пакетов
- Номер студента, чьи пакеты нужно собрать

```python
def collect_student_packets(student_number, host, port, max_packets):
```
Объявление функции для сбора пакетов, принимающей параметры:
- `student_number` - номер студента
- `host` - адрес сервера
- `port` - порт сервера
- `max_packets` - максимальное количество пакетов

```python
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
```
Создание TCP-сокета:
- `AF_INET` - использование IPv4
- `SOCK_STREAM` - указание на TCP протокол
- Установка таймаута 10 секунд на операции с сокетом

```python
    try:
        print(f"[INFO] Подключение к {host}:{port}...")
        sock.connect((host, port))
        print(f"[INFO] Подключено к серверу")
```
Попытка подключения к серверу с выводом информационных сообщений

```python
        collected_packets = []
        buffer = ""
        pattern = re.compile(rf"Student\s*{student_number}[^\d](.*?)(?=Student\s*\d|$)")
```
Инициализация:
- Пустого списка для собранных пакетов
- Пустого буфера для накопления данных
- Регулярного выражения для поиска пакетов студента

```python
        while len(collected_packets) < max_packets:
```
Цикл сбора пакетов, пока не наберется нужное количество

```python
            data = sock.recv(4096)
            if not data:
                print("[WARN] Сервер закрыл соединение")
                break
```
Получение данных от сервера (максимум 4096 байт за раз)
Проверка на закрытие соединения сервером

```python
            buffer += data.decode('utf-8', errors='replace')
```
Декодирование полученных данных (с заменой некорректных символов) и добавление в буфер

```python
            matches = list(pattern.finditer(buffer))
```
Поиск всех совпадений с регулярным выражением в буфере

```python
            for match in matches:
                packet_data = match.group(1).strip()
                print(packet_data)
```
Обработка каждого найденного совпадения:
- Извлечение данных пакета (группа 1 в регулярном выражении)
- Удаление пробельных символов по краям
- Вывод содержимого пакета

```python
                collected_packets.append({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "student": student_number,
                    "data": packet_data
                })
```
Добавление пакета в список с метаданными:
- Текущая временная метка
- Номер студента
- Данные пакета

```python
                print(f"[INFO] Пакет #{len(collected_packets)} собран")
                if len(collected_packets) >= max_packets:
                    break
```
Вывод информации о собранном пакете и проверка достижения лимита

```python
            if matches:
                buffer = buffer[matches[-1].end():]
```
Если были совпадения, буфер обрезается до конца последнего совпадения

```python
        return collected_packets
```
Возврат собранных пакетов при успешном завершении

```python
    except Exception as e:
        print(f"[ERROR] {e}")
        return []
```
Обработка исключений с выводом ошибки и возвратом пустого списка

```python
    finally:
        sock.close()
        print("[INFO] Соединение закрыто")
```
Гарантированное закрытие сокета в любом случае

```python
def save_to_jsonl(data, filename='report.jsonl'):
    with open(filename, 'w', encoding='utf-8') as f:
        for entry in data:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')
    print(f"[INFO] Данные сохранены в {filename}")
```
Функция сохранения данных:
- Открытие файла на запись
- Последовательная запись каждого пакета как отдельной JSON строки
- Закрытие файла (происходит автоматически при выходе из with)

```python
if __name__ == "__main__":
    print(f"Сбор пакетов для студента {STUDENT_NUMBER}...\n")
    packets = collect_student_packets(STUDENT_NUMBER, IP_ADDR, PORT, MAX_PACKETS)
```
Основной блок:
- Вывод информации о начале сбора
- Вызов функции сбора пакетов с параметрами из констант

```python
    if len(packets) == 10:
        save_to_jsonl(packets)
        print("\nСобрано 10 пакетов:")
        for pkt in packets:
            print(f"[{pkt['timestamp']}] {pkt['data']}")
    else:
        print("\nНе удалось собрать 10 пакетов. Собрано:", len(packets))
```
