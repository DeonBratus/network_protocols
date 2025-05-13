from datetime import datetime
import socket
from ftplib import FTP
import time
import os
from tqdm import tqdm


def generate_data():
    """Generate test data as list of tuples (i, y)"""
    data = []
    y = 0
    for i in range(1000):
        data.append((i, y))
        y += i + 1
    return data


def send_udp_packets():
    """Send generated data via UDP packets"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('109.167.241.225', 61557)
    data = generate_data()
    
    for i, y in tqdm(data, desc="Sending UDP packets"):
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        millis = int(time.time() * 1000) % 1000
        message = f"{timestamp},{millis}\tBratus;{i};{y}"
        
        try:
            sock.sendto(message.encode(), server_address)
        except Exception as e:
            print(f"Error sending packet {i}: {e}")
        time.sleep(0.01)
    
    sock.close()


def download_log():
    """Download log file from FTP server"""
    try:
        with FTP() as ftp:
            ftp.connect('109.167.241.225', 21, timeout=10)
            ftp.login(user='Student', passwd='FksG5$%^rgtdSDFH')
            
            files = ftp.nlst()
            log_file = "UDP log.txt"
            
            if log_file in files:
                with open('downloaded_log.log', 'wb') as f:
                    ftp.retrbinary(f'RETR {log_file}', f.write)
            else:
                print(f"Log file '{log_file}' not found on server")
    except Exception as e:
        print(f"FTP error: {e}")


def parse_log():
    """Parse log file and analyze data delivery"""
    original = {i: y for i, y in generate_data()}
    received = {}

    if not os.path.exists('downloaded_log.log'):
        print("Log file not found")
        return

    try:
        with open('downloaded_log.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open('downloaded_log.log', 'r', encoding='latin-1') as f:
            lines = f.readlines()

    for line in tqdm(lines, desc="Parsing log file"):
        if '\tBratus;' in line:
            try:
                parts = line.strip().split('\t')[1].split(';')
                if len(parts) == 3:
                    i = int(parts[1])
                    y = float(parts[2])
                    received[i] = y
            except Exception as e:
                print(f"Error parsing line: {line.strip()}. Error: {e}")

    total = len(original)
    delivered = len(received)
    percent = (delivered / total) * 100
    print(f"Delivered: {delivered}/{total} ({percent:.2f}%)")

    if delivered > 0:
        correct = sum(1 for i, y in received.items() if original[i] == y)
        accuracy = (correct / delivered) * 100
        print(f"Accuracy: {correct}/{delivered} ({accuracy:.2f}%)")


if __name__ == "__main__":
    print("Starting UDP packet transmission...")
    send_udp_packets()

    print("Waiting for server processing...")
    time.sleep(10)

    print("Downloading log file...")
    download_log()

    print("Analyzing data...")
    parse_log()