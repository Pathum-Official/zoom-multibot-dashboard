# 🚀 Zoom Bot Pro & Multi-Attendee Dashboard

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Selenium-4.20+-43B02A?style=for-the-badge&logo=selenium&logoColor=white" />
  <img src="https://img.shields.io/badge/Flask-Web_UI-000000?style=for-the-badge&logo=flask&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-informational?style=for-the-badge" />
</p>

A powerful, high-performance automated Zoom Web Client attendee bot and management suite. Designed for load-testing, attendance automation, and multi-user simulations with an ultra-sleek, modern **Glassmorphism Web Dashboard**, a **1-Click Windows Launcher (`.bat`)**, and an advanced **Chrome DevTools Protocol (CDP) Anti-Detection Stealth Engine**.

---

## 🇱🇰 සිංහලෙන් හැඳින්වීම (Sinhala Overview)
ඕනෑම පරිශීලකයෙකුට පහසුවෙන් Zoom meetings වලට ගිණුම්/සහභාගිවන්නන් එකවර හෝ අනුපිළිවෙලින් ස්වයංක්‍රීයව සම්බන්ධ කළ හැකි ප්‍රබල මෘදුකාංගයකි. 
- **1-Click Setup**: `start.bat` මත double click කිරීමෙන් පමණක් අවශ්‍ය සියලුම setup ස්වයංක්‍රීයව සිදුවී Dashboard එක Browser එකෙන් විවෘත වේ.
- **🛡️ Stealth Engine (Bypasses Zoom Anti-Bot)**: Zoom එකේ Google reCAPTCHA Enterprise පද්ධතියට හසුනොවන පරිදි සැබෑ පරිශීලකයෙකුගේ ආකාරයට සම්බන්ධ වේ.
- **Auto-Minimized Mode**: බ්‍රව්සර් විවෘත වූ සැණින් ස්වයංක්‍රීයව Taskbar එකට Minimize වන බැවින් පරිගණකයේ ඔබේ වැඩවලට කිසිදු බාධාවක් නොවේ.
- **Modern Dashboard**: Meeting ID, Password, Bot ගණන, Delay පහසුවෙන් පාලනය කළ හැක.
- **Preset Names**: ශ්‍රී ලාංකික නම් 100+ ක් ඇතුලත් කර ඇති අතර ඔබේම නම් ලැයිස්තුවක්ද එක් කළ හැක.

---

## ✨ Features (ප්‍රධාන විශේෂාංග)

- 🎨 **Modern Glassmorphic Web Dashboard**: Control and monitor all bots in real-time from a sleek web UI (`http://localhost:5000`).
- ⚡ **1-Click Launcher (`start.bat`)**: Zero technical knowledge needed. Auto-creates Python venv, auto-installs requirements, and opens the dashboard in your default browser.
- 🛡️ **CDP Stealth Anti-Detection**: Injects custom Chrome DevTools Protocol overrides to remove `navigator.webdriver`, spoof Chrome runtime, and bypass Zoom Web Client bot restrictions.
- 🗕 **Auto-Minimized Windows**: Browser windows automatically minimize to the taskbar immediately after launching, keeping your desktop completely clean.
- 📋 **Preset Name Generator**: Includes 100+ authentic Sri Lankan names, international names, and custom lists with instant shuffle & randomization.
- 📊 **Real-Time Live Console & Telemetry**: Monitor join states (Connecting, In Meeting, Waiting Room, Closed), uptime, and live logs directly from the dashboard.
- 🎛️ **Granular Bot Control**: Stop all bots together or terminate single bot instances individually.
- 💻 **Flexible Modes**: Run via the **Web Dashboard** or the high-speed **CLI Terminal Mode (`run_cli.bat`)**.

---

## 🏁 Quick Start for Windows (පහසුම ක්‍රමය)

1. **Clone or Download** this repository:
   ```bash
   git clone https://github.com/Pathum-Official/zoom-multibot-dashboard.git
   cd zoom-multibot-dashboard
   ```
2. Double-click **`start.bat`**.
3. That's it! The launcher will automatically:
   - Configure Python Virtual Environment.
   - Install required packages (`selenium`, `flask`, `webdriver-manager`).
   - Launch the Web Dashboard and open it in your browser (`http://127.0.0.1:5000`).
4. Enter your Meeting ID and Passcode, and click **"Launch Bots"**!

---

## 🛠️ Manual Installation (Cross-Platform)

Works on **Windows, macOS, and Linux**:

```bash
# 1. Clone repo
git clone https://github.com/Pathum-Official/zoom-multibot-dashboard.git
cd zoom-multibot-dashboard

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run Web Dashboard
python app.py

# OR run CLI Mode:
python main.py
```

---

## ⚙️ Configuration (`config.json`)

Settings are automatically saved and updated from the Web Dashboard, or you can edit `config.json` directly:

```json
{
    "meeting_id": "7018786250",
    "password": "123",
    "account_count": 5,
    "delay_seconds": 15,
    "name_list": [
        "Kavindu Gunarathne",
        "Nethmi Gimansa",
        "Pasindu Gimhan"
    ]
}
```

| Field | Description |
|---|---|
| `meeting_id` | Zoom Meeting ID (spaces are automatically stripped) |
| `password` | Meeting Passcode / Password |
| `account_count` | Number of bot attendees to launch |
| `delay_seconds` | Wait duration between launching consecutive bots (default: 15s to prevent IP rate limits) |
| `name_list` | Array of participant display names |

---

## 📁 Project Structure

```
zoom-bot/
│
├── core/
│   ├── __init__.py
│   ├── bot_engine.py       # Selenium Zoom Web client driver & stealth logic
│   └── bot_manager.py      # Multi-instance coordinator, thread pool & state
│
├── static/
│   ├── css/
│   │   └── dashboard.css   # Modern Glassmorphic dark styling & animations
│   └── js/
│       └── dashboard.js    # Real-time state polling, controls & logs
│
├── templates/
│   └── index.html          # Web Dashboard UI template
│
├── app.py                  # Flask Web Server
├── main.py                 # Standalone Terminal CLI runner
├── requirements.txt        # Python dependencies
├── config.json             # Active user settings
├── config.example.json     # Safe template for GitHub
├── start.bat               # 1-Click Windows Launcher (Web UI)
├── run_cli.bat             # 1-Click Windows Launcher (CLI)
├── .gitignore              # Ignores venv, cache, sensitive files
├── LICENSE                 # MIT Open Source License
└── README.md               # Documentation
```

---

## 💡 Performance & Reliability Tips

- **Join Interval**: Keep join interval at **12–15 seconds**. Rapid consecutive connections from the same IP can trigger Zoom's reCAPTCHA rate limits.
- **Auto-Minimize**: Browser windows automatically minimize to the taskbar, allowing your PC to run smoothly without window clutter.
- **Google Chrome**: Ensure Google Chrome is installed on your computer. `webdriver-manager` will automatically manage driver versions.

---

## ⚠️ Disclaimer & Ethical Use

This software is developed strictly for **educational, testing, meeting load analysis, and automated attendance demonstration purposes**. The authors are not responsible for any misuse, violations of Zoom's Terms of Service, or disruptive behavior. Please ensure you have explicit permission from the meeting host before running bots in any meeting.

---

## 📜 License

Distributed under the **MIT License**. Feel free to use, modify, and distribute.
