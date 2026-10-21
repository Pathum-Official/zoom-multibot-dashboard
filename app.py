# -*- coding: utf-8 -*-
"""
Zoom Bot Modern Web Dashboard
Flask Server providing REST APIs and visual management UI.
"""

import os
import sys
import webbrowser
import threading
from flask import Flask, render_template, request, jsonify
from core.bot_manager import BotManager

app = Flask(__name__)
manager = BotManager()

PRESET_NAMES = {
    "sinhala": [
        "Kavindu Gunarathne", "Nethmi Gimansa", "Pasindu Gimhan", "Sanduni Gethmini",
        "Tharindu Gunawardhane", "Rashmi Gothami", "Shehan Garusinhe", "Amaya Gisanka",
        "Avishka Grishma", "Kavindi Gimhani", "Nipun Gayashan", "Hansini Gunarathna",
        "Ravindu Rathnayake", "Ishani Lakshika", "Sithum Wickramasinghe", "Hiruni Himasha",
        "Hirusha Gamage", "Piyumi Hansika", "Isuru Ekanayake", "Shashini Perera",
        "Dasun Herath", "Dilini Maheshika", "Malith Gunawardena", "Chamari Atapattu",
        "Chathura Karunaratne", "Ruwini Nethmini", "Janith Dissanayake", "Sajani Weerasinghe"
    ],
    "global": [
        "Alex Walker", "Emma Johnson", "Liam Smith", "Olivia Brown",
        "Noah Williams", "Sophia Miller", "James Davis", "Isabella Wilson",
        "Lucas Taylor", "Mia Anderson", "Ethan Thomas", "Harper Jackson"
    ],
    "tech": [
        "DevOps Lead", "Frontend Specialist", "Data Architect", "Cloud Engineer",
        "QA Automation Bot", "Security Auditor", "Backend Core Dev", "System Observer"
    ]
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status", methods=["GET"])
def get_status():
    return jsonify(manager.get_status())

@app.route("/api/logs", methods=["GET"])
def get_logs():
    since_id = request.args.get("since", default=0, type=int)
    return jsonify({
        "logs": manager.get_logs(since_id)
    })

@app.route("/api/logs/clear", methods=["POST"])
def clear_logs():
    manager.clear_logs()
    return jsonify({"success": True})

@app.route("/api/config", methods=["GET", "POST"])
def handle_config():
    if request.method == "POST":
        data = request.json or {}
        success = manager.save_config(data)
        return jsonify({"success": success})
    return jsonify(manager.load_config())

@app.route("/api/presets", methods=["GET"])
def get_presets():
    return jsonify(PRESET_NAMES)

@app.route("/api/start", methods=["POST"])
def start_bots():
    data = request.json or {}
    meeting_id = data.get("meeting_id")
    password = data.get("password", "")
    count = data.get("account_count", 5)
    delay = data.get("delay_seconds", 15)
    name_list = data.get("name_list", [])

    if not meeting_id:
        return jsonify({"success": False, "message": "Meeting ID is required!"}), 400

    success, message = manager.start_session(
        meeting_id=meeting_id,
        password=password,
        count=count,
        name_list=name_list,
        delay=delay
    )
    return jsonify({"success": success, "message": message})

@app.route("/api/stop", methods=["POST"])
def stop_bots():
    success, message = manager.stop_session()
    return jsonify({"success": success, "message": message})

@app.route("/api/stop/<int:bot_id>", methods=["POST"])
def stop_bot(bot_id):
    success, message = manager.stop_single_bot(bot_id)
    return jsonify({"success": success, "message": message})

def open_browser():
    time_delay = 1.2
    threading.Timer(time_delay, lambda: webbrowser.open("http://127.0.0.1:5000")).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(r"""
  ______                         ____        _   
 |___  /                        |  _ \      | |  
    / / ___   ___  _ __ ___     | |_) | ___ | |_ 
   / / / _ \ / _ \| '_ ` _ \    |  _ < / _ \| __|
  / /_| (_) | (_) | | | | | |   | |_) | (_) | |_ 
 /_____\___/ \___/|_| |_| |_|   |____/ \___/ \__|
==================================================
  Web Dashboard Started!
  URL: http://127.0.0.1:5000
  Press CTRL+C to stop the web server.
==================================================
    """)
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        open_browser()
    app.run(host="0.0.0.0", port=port, threaded=True, debug=False)
