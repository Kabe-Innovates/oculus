import asyncio
import random
import uuid
import httpx
from datetime import datetime, timezone
from config import settings

class TransactionSimulator:
    def __init__(self):
        self.CITIES = {
            "New York": (40.7128, -74.0060),
            "London": (51.5074, -0.1278),
            "Tokyo": (35.6762, 139.6503),
            "Paris": (48.8566, 2.3522),
            "Sydney": (-33.8688, 151.2093),
            "Mumbai": (19.0760, 72.8777),
            "Sao Paulo": (-23.5505, -46.6333),
            "Dubai": (25.2048, 55.2708),
            "Singapore": (1.3521, 103.8198),
            "Toronto": (43.6510, -79.3470)
        }
        self.SENDER_PROFILES = {}
        for i in range(20):
            sender_id = f"user_{i}"
            city_name = random.choice(list(self.CITIES.keys()))
            self.SENDER_PROFILES[sender_id] = {
                "avg_amount": random.uniform(50.0, 500.0),
                "location": f"{self.CITIES[city_name][0]},{self.CITIES[city_name][1]}",
                "name": f"Sender {i}"
            }
        self.running = False
            
    async def stream(self):
        self.running = True
        while self.running:
            scenario_rand = random.random()
            if scenario_rand < 0.05:
                scenario = "rapid_fire"
            elif scenario_rand < 0.13:
                scenario = "whale"
            elif scenario_rand < 0.20:
                scenario = "teleport"
            else:
                scenario = "normal"
                
            if scenario == "rapid_fire":
                sender_id = random.choice(list(self.SENDER_PROFILES.keys()))
                for _ in range(random.randint(5, 10)):
                    if not self.running: break
                    yield self.generate_single("normal", specific_sender=sender_id)
                    await asyncio.sleep(0.1)
            else:
                yield self.generate_single(scenario)
                
            rate = settings.SIMULATOR_RATE
            if rate <= 0: rate = 1.0
            await asyncio.sleep(1.0 / rate)

    def generate_single(self, scenario: str, specific_sender: str = None) -> dict:
        sender_id = specific_sender or random.choice(list(self.SENDER_PROFILES.keys()))
        profile = self.SENDER_PROFILES[sender_id]
        
        amount = profile["avg_amount"] * random.uniform(0.8, 1.2)
        location = profile["location"]
        
        if scenario == "whale":
            amount = profile["avg_amount"] * random.uniform(5, 20)
        elif scenario == "teleport":
            other_cities = [c for c in self.CITIES.keys() if f"{self.CITIES[c][0]},{self.CITIES[c][1]}" != location]
            if other_cities:
                tele_city = random.choice(other_cities)
                location = f"{self.CITIES[tele_city][0]},{self.CITIES[tele_city][1]}"
                
        return {
            "amount": round(amount, 2),
            "currency": "USD",
            "sender_id": sender_id,
            "receiver_id": f"merchant_{random.randint(1, 100)}",
            "sender_location": location,
            "device_fingerprint": f"device_{sender_id}",
            "ip_address": f"192.168.1.{random.randint(1, 255)}"
        }

simulator_instance = TransactionSimulator()
