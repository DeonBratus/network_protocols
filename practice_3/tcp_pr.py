import socket
import datetime
import json
import re

IP_ADDR = "109.167.241.225"
PORT = 6340
MAX_PACKETS = 10
STUDENT_NUMBER = 3


def collect_student_packets(student_number, host, port, max_packets):
    """Собирает TCP пакеты для указанного номера студента."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)

    try:
        print(f"[INFO] Подключение к {host}:{port}...")
        sock.connect((host, port))
        print(f"[INFO] Подключено к серверу")

        collected_packets = []
        buffer = ""
        # regular for find packets of student
        pattern = re.compile(rf"Student\s*{student_number}[^\d](.*?)(?=Student\s*\d|$)")

        while len(collected_packets) < max_packets:
            # get raw data of packet
            data = sock.recv(4096)
            if not data:
                print("[WARN] Сервер закрыл соединение")
                break
            
            # Add data to buffer
            buffer += data.decode('utf-8', errors='replace')
            matches = list(pattern.finditer(buffer)) # get my all my packets

            #  collect packet with student's id
            for match in matches:
                packet_data = match.group(1).strip()
                print(packet_data)
                collected_packets.append({
                    "timestamp": datetime.datetime.now().isoformat(),
                    "student": student_number,
                    "data": packet_data
                })
                print(f"[INFO] Пакет #{len(collected_packets)} собран")

                if len(collected_packets) >= max_packets:
                    break
            if matches:
                buffer = buffer[matches[-1].end():]

        return collected_packets

    except Exception as e:
        print(f"[ERROR] {e}")
        return []
    finally:
        sock.close()
        print("[INFO] Соединение закрыто")


def save_to_jsonl(data, filename='report.jsonl'):
    """Сохраняет данные в формате JSONL."""
    with open(filename, 'w', encoding='utf-8') as f:
        for entry in data:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')
    print(f"[INFO] Данные сохранены в {filename}")

if __name__ == "__main__":

    print(f"Сбор пакетов для студента {STUDENT_NUMBER}...\n")
    packets = collect_student_packets(STUDENT_NUMBER, IP_ADDR, PORT, MAX_PACKETS)

    if len(packets) == 10:
        save_to_jsonl(packets)
        print("\nСобрано 10 пакетов:")
        for pkt in packets:
            print(f"[{pkt['timestamp']}] {pkt['data']}")
    else:
        print("\nНе удалось собрать 10 пакетов. Собрано:", len(packets))
