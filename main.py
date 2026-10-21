# -*- coding: utf-8 -*-
"""
Zoom Bot CLI Runner
Run multiple Zoom Web Client bot attendees directly from the terminal.
"""

import sys
import os
import json
import time
from core.bot_manager import BotManager

def main():
    print(r"""
  ______                         ____        _   
 |___  /                        |  _ \      | |  
    / / ___   ___  _ __ ___     | |_) | ___ | |_ 
   / / / _ \ / _ \| '_ ` _ \    |  _ < / _ \| __|
  / /_| (_) | (_) | | | | | |   | |_) | (_) | |_ 
 /_____\___/ \___/|_| |_| |_|   |____/ \___/ \__|
==================================================
       ZOOM AUTO ATTENDEE & MULTI-BOT
==================================================
    """)
    manager = BotManager()
    cfg = manager.load_config()

    print("[1] Launch with current config.json")
    print("[2] Enter new Meeting ID and Passcode")
    print("[3] Launch Web Dashboard instead (Recommended)")
    print("[4] Exit")

    choice = input("\nSelect Option [1-4] (Default: 1): ").strip()

    if choice == "3":
        print("\nStarting Web Dashboard on http://127.0.0.1:5000 ...")
        from app import app, open_browser
        open_browser()
        app.run(port=5000)
        return
    elif choice == "4":
        sys.exit(0)

    if choice == "2":
        meeting_id = input("Enter Zoom Meeting ID: ").strip().replace(" ", "")
        passcode = input("Enter Passcode (leave blank if none): ").strip()
        count = input(f"Enter Bot Count [Default: {cfg.get('account_count', 5)}]: ").strip()
        count = int(count) if count.isdigit() else cfg.get("account_count", 5)
        delay = input(f"Enter Join Interval seconds [Default: {cfg.get('delay_seconds', 15)}]: ").strip()
        delay = int(delay) if delay.isdigit() else cfg.get("delay_seconds", 15)
    else:
        meeting_id = cfg.get("meeting_id", "")
        passcode = cfg.get("password", "")
        count = cfg.get("account_count", 5)
        delay = cfg.get("delay_seconds", 15)

    name_list = cfg.get("name_list", ["Attendee"])

    print(f"\nTarget Meeting ID: {meeting_id}")
    print(f"Passcode:          " + ("*" * len(passcode) if passcode else "(None)"))
    print(f"Number of Bots:    {count}")
    print(f"Join Interval:     {delay}s")
    print(f"Stealth Mode:      Auto-Minimized (Bypasses Zoom bot block)")
    print("-" * 50)

    success, msg = manager.start_session(
        meeting_id=meeting_id,
        password=passcode,
        count=count,
        name_list=name_list,
        delay=delay
    )

    if not success:
        print(f"Error: {msg}")
        return

    print("\nBots are now connecting... Press Ctrl+C or Enter to stop all bots.\n")
    try:
        while manager.is_running:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    print("\nTerminating all bots gracefully...")
    manager.stop_session()
    time.sleep(3)
    print("All bots terminated. Bye!")

if __name__ == "__main__":
    main()
