# producer.py
from kafka import KafkaProducer
import json, time, random
from datetime import datetime

producer = KafkaProducer(bootstrap_servers='localhost:9092')

def generate_log():
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": f"user_{random.randint(1,500)}",
        "device_id": f"device_{random.randint(1,1000)}",
        "ip_address": f"192.168.{random.randint(0,255)}.{random.randint(0,255)}",
        "location": random.choice(["New York, USA", "Cape Town, South Africa", "Tokyo, Japan"]),
        "login_success": random.choice([0,1]),
        "access_time": datetime.utcnow().strftime("%H:%M:%S"),
        "resource_accessed": random.choice(["sales","finance","hr","prod"]),
        "bytes_transferred": random.uniform(1e5, 1e7)
    }

while True:
    msg = generate_log()
    producer.send("auth_events", json.dumps(msg).encode("utf-8"))
    print("Produced:", msg)
    time.sleep(1)
