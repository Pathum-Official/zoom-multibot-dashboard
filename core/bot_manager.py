# -*- coding: utf-8 -*-
"""
Zoom Bot Manager
Thread-safe session controller, coordinator, and status manager for all bots.
Uses RLock to prevent any re-entrant deadlocks.
"""

import os
import json
import time
import threading
from datetime import datetime
from core.bot_engine import ZoomBotInstance

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

class BotManager:
    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(BotManager, cls).__new__(cls)
                cls._instance._init_manager()
            return cls._instance

    def _init_manager(self):
        self.lock = threading.RLock()
        self.bots = {}          # index -> ZoomBotInstance
        self.logs = []          # list of log dicts
        self.log_counter = 0
        self.is_running = False
        self.worker_thread = None
        self.start_time = None
        self.meeting_id = ""
        self.password = ""
        self.total_target = 0
        self.config = self.load_config()

    def add_log(self, message, level="info", bot_id=None):
        with self.lock:
            self.log_counter += 1
            log_entry = {
                "id": self.log_counter,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "level": level,
                "message": message,
                "bot_id": bot_id
            }
            self.logs.append(log_entry)
            if len(self.logs) > 500:
                self.logs.pop(0)
            return log_entry

    def get_logs(self, since_id=0):
        with self.lock:
            if since_id <= 0:
                return self.logs[-100:]
            return [l for l in self.logs if l["id"] > since_id]

    def clear_logs(self):
        with self.lock:
            self.logs = []
            self.log_counter = 0

    def load_config(self):
        default_config = {
            "meeting_id": "7018786250",
            "password": "123",
            "account_count": 5,
            "delay_seconds": 15,
            "name_list": [
                "Kavindu Gunarathne", "Nethmi Gimansa", "Pasindu Gimhan", "Sanduni Gethmini",
                "Tharindu Gunawardhane", "Rashmi Gothami", "Shehan Garusinhe", "Amaya Gisanka"
            ]
        }
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    default_config.update(data)
            except Exception as e:
                self.add_log(f"Error reading config: {e}", "warning")
        return default_config

    def save_config(self, new_config):
        with self.lock:
            self.config.update(new_config)
            try:
                with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, indent=4, ensure_ascii=False)
                self.add_log("Configuration saved successfully.", "success")
                return True
            except Exception as e:
                self.add_log(f"Failed to save config: {e}", "error")
                return False

    def start_session(self, meeting_id, password, count, name_list, delay=15):
        with self.lock:
            if self.is_running:
                return False, "A bot session is already running!"
            
            # Clean old instances
            self.bots.clear()
            self.is_running = True
            self.meeting_id = str(meeting_id).strip().replace(" ", "")
            self.password = str(password).strip()
            self.total_target = int(count)
            self.start_time = time.time()
            
            # Save recent params in config
            self.config["meeting_id"] = self.meeting_id
            self.config["password"] = self.password
            self.config["account_count"] = self.total_target
            self.config["delay_seconds"] = int(delay)
            if name_list:
                self.config["name_list"] = name_list
            self.save_config(self.config)

        self.add_log(f"=== Starting Session: {self.total_target} bots targeting Meeting ID {self.meeting_id} ===", "info")

        def _runner():
            names = name_list if name_list else ["Guest Participant"]
            for i in range(1, self.total_target + 1):
                if not self.is_running:
                    self.add_log("Session stopped by user.", "warning")
                    break

                assigned_name = names[(i - 1) % len(names)]
                bot = ZoomBotInstance(
                    index=i,
                    meeting_id=self.meeting_id,
                    password=self.password,
                    name=assigned_name,
                    log_callback=self.add_log
                )
                
                with self.lock:
                    self.bots[i] = bot

                # Launch bot in its own background thread
                bot.start()

                # Delay before next bot
                if i < self.total_target and self.is_running:
                    self.add_log(f"Waiting {delay}s before launching next bot...", "info")
                    for _ in range(int(delay * 2)):
                        if not self.is_running:
                            break
                        time.sleep(0.5)

            self.add_log("All scheduled bot launches initiated.", "info")

        self.worker_thread = threading.Thread(target=_runner, daemon=True)
        self.worker_thread.start()
        return True, "Session launched successfully."

    def stop_session(self):
        with self.lock:
            if not self.is_running and not self.bots:
                return False, "No active session to stop."
            self.is_running = False

        self.add_log("=== Stopping all active bot instances... ===", "warning")

        def _cleanup():
            with self.lock:
                instances = list(self.bots.values())
            for bot in instances:
                try:
                    bot.close()
                except Exception:
                    pass
            self.add_log("All bot instances successfully closed.", "success")

        threading.Thread(target=_cleanup, daemon=True).start()
        return True, "Stopping all bots..."

    def stop_single_bot(self, bot_index):
        with self.lock:
            bot = self.bots.get(int(bot_index))
        if not bot:
            return False, f"Bot #{bot_index} not found."

        self.add_log(f"Terminating individual bot #{bot_index}...", "info")
        threading.Thread(target=bot.close, daemon=True).start()
        return True, f"Bot #{bot_index} closed."

    def get_status(self):
        with self.lock:
            bots_data = []
            active_count = 0
            now = time.time()

            # Fast in-memory check - zero cross-thread driver deadlock!
            for idx, bot in self.bots.items():
                duration_str = "00:00"
                if bot.start_time:
                    dur = int(now - bot.start_time)
                    m, s = divmod(dur, 60)
                    h, m = divmod(m, 60)
                    duration_str = f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

                if bot.status in ["in_meeting", "waiting_room", "connecting"]:
                    active_count += 1

                bots_data.append({
                    "id": bot.index,
                    "name": bot.name,
                    "status": bot.status,
                    "status_text": bot.status_text,
                    "duration": duration_str
                })

            uptime_str = "00:00:00"
            if self.is_running and self.start_time:
                dur = int(now - self.start_time)
                m, s = divmod(dur, 60)
                h, m = divmod(m, 60)
                uptime_str = f"{h:02d}:{m:02d}:{s:02d}"

            return {
                "is_running": self.is_running,
                "meeting_id": self.meeting_id,
                "total_target": self.total_target,
                "active_count": active_count,
                "uptime": uptime_str,
                "bots": bots_data,
                "config": self.config
            }
