from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
import datetime
import time

# Параметры подключения
IP_ADDRESS = '109.167.241.225'
PORT = 601
DEVICE_ADDRESS = 1
START_REGISTER = 3 * 100 
REGISTER_COUNT = 12 

def main():
    # Фиксируем время начала запроса
    request_time = datetime.datetime.now()
    print(f"Время запроса: {request_time}")
    
    try:
        # Создаем клиента Modbus TCP
        client = ModbusTcpClient(IP_ADDRESS, port=PORT)
        
        # Подключаемся к устройству
        connection = client.connect()
        if not connection:
            print("Не удалось подключиться к устройству")
            return
        
        # Читаем регистры (функциональный код 0x03 - Read Holding Registers)
        response = client.read_holding_registers(
            address=START_REGISTER,
            count=REGISTER_COUNT,
            slave=DEVICE_ADDRESS
        )
        
        # Проверяем ответ
        if response.isError():
            print(f"Ошибка при чтении регистров: {response}")
            return
        
        # Декодируем данные
        decoder = BinaryPayloadDecoder.fromRegisters(
            response.registers,
            byteorder=Endian.BIG,
            wordorder=Endian.BIG
        )
        
        # Читаем 2 числа U16
        number1 = decoder.decode_16bit_uint()
        number2 = decoder.decode_16bit_uint()

        ascii_string = decoder.decode_string(10).decode('ascii')
        
        # Выводим результаты
        print(f"Прочитанные данные:")
        print(f"Первое число (U16): {number1}")
        print(f"Второе число (U16): {number2}")
        print(f"Строка ASCII: '{ascii_string}'")
        
        # Проверяем корректность ASCII символов
        if all(32 <= ord(c) <= 126 for c in ascii_string):
            print("Строка содержит только корректные ASCII символы")
        else:
            print("В строке обнаружены некорректные ASCII символы")
            
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        # Закрываем соединение
        client.close()

if __name__ == "__main__":
    main()