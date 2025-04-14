from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import paho.mqtt.client as mqtt
from datetime import datetime
import threading
import time
import logging
import json
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Глобальное хранилище
class MQTTManager:
    def __init__(self):
        self.client = None
        self.connections = set()
        self.topics = {}
        self.is_connected = False

    async def connect(self, broker, port, username, password, client_id):
        if self.client:
            self.client.disconnect()
        
        self.client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION1)
        self.client.username_pw_set(username, password)
        
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        try:
            self.client.connect(broker, port)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self.is_connected = True
            logger.info("MQTT Connected!")
            # Ресубскрайбимся на топики при переподключении
            for topic in self.topics.values():
                client.subscribe(topic['name'])
        else:
            logger.error(f"Connection failed with code {rc}")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()
        timestamp = datetime.now().isoformat()
        
        # Сохраняем данные
        if topic not in self.topics:
            self.topics[topic] = {
                'name': topic,
                'value': payload,
                'timestamp': timestamp,
                'subscribed': True
            }
        else:
            self.topics[topic].update({
                'value': payload,
                'timestamp': timestamp
            })
        
        # Рассылаем обновление
        asyncio.run(self.broadcast({
            'event': 'update',
            'topic': topic,
            'data': self.topics[topic]
        }))

    def on_disconnect(self, client, userdata, rc, properties=None):
        self.is_connected = False
        logger.warning(f"Disconnected with code {rc}")

    def subscribe(self, topic):
        if self.client and topic not in self.topics:
            self.client.subscribe(topic)
            self.topics[topic] = {
                'name': topic,
                'value': 'No data',
                'timestamp': 'Never',
                'subscribed': True
            }
            return True
        return False

    def publish(self, topic, message):
        if self.client:
            self.client.publish(topic, message)
            return True
        return False

    async def broadcast(self, message):
        for connection in self.connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending WS message: {e}")

mqtt_manager = MQTTManager()

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    mqtt_manager.connections.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("action") == "connect":
                    result = await mqtt_manager.connect(
                        message["broker"],
                        int(message["port"]),
                        message["username"],
                        message["password"],
                        message["client_id"]
                    )
                    await websocket.send_text(json.dumps({
                        'event': 'connection',
                        'status': 'connected' if result else 'failed'
                    }))
                elif message.get("action") == "subscribe":
                    mqtt_manager.subscribe(message["topic"])
                elif message.get("action") == "publish":
                    mqtt_manager.publish(message["topic"], message["message"])
            except Exception as e:
                logger.error(f"WS message error: {e}")
    except WebSocketDisconnect:
        mqtt_manager.connections.remove(websocket)
        logger.info("WebSocket disconnected")

# HTML Page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)