import paho.mqtt.client as mqtt
import time
from datetime import datetime
from collections import defaultdict

# MQTT Configuration
BROKER = "srv2.clusterfly.ru"
PORT = 9991  # Using TCP port without SSL
USERNAME = "user_0d181660"
PASSWORD = "qaf0imzefxXVQ"
STUDENT_N = "3"  # student number
CLIENT_ID = "user_0d181660_student3_reader"  # Unique client ID

# Topics
PERSONAL_TOPIC1 = f"user_0d181660/Student{STUDENT_N}/Value1"
PERSONAL_TOPIC2 = f"user_0d181660/Student{STUDENT_N}/Value2"
COMMON_TOPIC = "Value3"

# Store last values for each topic
topic_values = defaultdict(lambda: "No data yet")
last_update_times = defaultdict(lambda: "Never")

def print_topic_states():
    """Print current state of all topics"""
    print("\n=== Topic States ===")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"1. {PERSONAL_TOPIC1}")
    print(f"   Value: {topic_values[PERSONAL_TOPIC1]}")
    print(f"   Last update: {last_update_times[PERSONAL_TOPIC1]}")
    print(f"2. {PERSONAL_TOPIC2}")
    print(f"   Value: {topic_values[PERSONAL_TOPIC2]}")
    print(f"   Last update: {last_update_times[PERSONAL_TOPIC2]}")
    print(f"3. {COMMON_TOPIC}")
    print(f"   Value: {topic_values[COMMON_TOPIC]}")
    print(f"   Last update: {last_update_times[COMMON_TOPIC]}")
    print("===================\n")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        print(f"Subscribing to topics:")
        print(f"1. {PERSONAL_TOPIC1}")
        print(f"2. {PERSONAL_TOPIC2}")
        print(f"3. {COMMON_TOPIC}")
        # Subscribe to personal topics
        client.subscribe(PERSONAL_TOPIC1)
        client.subscribe(PERSONAL_TOPIC2)
        # Subscribe to common topic
        client.subscribe(COMMON_TOPIC)
        print("\nCommands:")
        print("1 <value> - Send message to Value1")
        print("2 <value> - Send message to Value2")
        print("s - Show current topic states")
        print("q - Quit")
    else:
        error_messages = {
            1: "Connection refused - incorrect protocol version",
            2: "Connection refused - invalid client identifier",
            3: "Connection refused - server unavailable",
            4: "Connection refused - bad username or password",
            5: "Connection refused - not authorized"
        }
        error_msg = error_messages.get(rc, f"Unknown error code: {rc}")
        print(f"Failed to connect: {error_msg}")

def on_message(client, userdata, msg):
    """Handle incoming messages"""
    topic = msg.topic
    value = msg.payload.decode()
    current_time = datetime.now().strftime('%H:%M:%S')
    
    # Update stored values
    topic_values[topic] = value
    last_update_times[topic] = current_time
    
    print(f"\nNew message received at {current_time}")
    print(f"Topic: {topic}")
    print(f"Value: {value}")

def publish_message(client, topic_num, value):
    """Publish message to specified topic"""
    try:
        if topic_num == 1:
            topic = PERSONAL_TOPIC1
        elif topic_num == 2:
            topic = PERSONAL_TOPIC2
        else:
            print("Invalid topic number. Use 1 or 2.")
            return
        
        client.publish(topic, value)
        print(f"Message sent to {topic}: {value}")
    except Exception as e:
        print(f"Error publishing message: {e}")

def main():
    # Create MQTT client instance with specific client ID and callback API version
    client = mqtt.Client(client_id=CLIENT_ID, callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
    
    # Set username and password
    client.username_pw_set(USERNAME, PASSWORD)
    
    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        # Connect to broker
        print(f"Connecting to {BROKER}:{PORT} as {USERNAME}...")
        client.connect(BROKER, PORT)
        
        # Start the loop in background thread
        client.loop_start()
        
        # Interactive loop for commands
        while True:
            try:
                command = input("> ").strip()
                
                if command.lower() == 'q':
                    break
                elif command.lower() == 's':
                    print_topic_states()
                elif command:
                    parts = command.split()
                    if len(parts) >= 2:
                        try:
                            topic_num = int(parts[0])
                            value = " ".join(parts[1:])
                            publish_message(client, topic_num, value)
                        except ValueError:
                            print("Invalid command format. Use: <topic_number> <value>")
                    else:
                        print("Invalid command format. Use: <topic_number> <value>")
                
                time.sleep(2)  # Small delay to prevent CPU overuse
                
            except Exception as e:
                print(f"Error processing command: {e}")
            
    except KeyboardInterrupt:
        print("\nDisconnecting from broker")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        client.disconnect()
        client.loop_stop()

if __name__ == "__main__":
    main()
