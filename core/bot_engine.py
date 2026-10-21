# -*- coding: utf-8 -*-
"""
Zoom Bot Engine
Handles individual Selenium WebDriver instance for Zoom Web Client with Anti-Detection CDP.
Operates in Auto-Minimized Stealth Mode (bypasses Zoom reCAPTCHA Enterprise bot detection).
"""

import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

_CACHED_DRIVER_PATH = None
_DRIVER_LOCK = threading.Lock()

def get_chromedriver_path():
    global _CACHED_DRIVER_PATH
    with _DRIVER_LOCK:
        if _CACHED_DRIVER_PATH is None:
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                _CACHED_DRIVER_PATH = ChromeDriverManager().install()
            except Exception as e:
                print(f"[Driver] Using default Selenium PATH: {e}")
                _CACHED_DRIVER_PATH = ""
        return _CACHED_DRIVER_PATH

class ZoomBotInstance:
    def __init__(self, index, meeting_id, password, name, log_callback=None):
        self.index = index
        self.meeting_id = str(meeting_id).strip().replace(" ", "")
        self.password = str(password).strip()
        self.name = str(name).strip()
        self.log_callback = log_callback or self._default_log
        self.driver = None
        self.status = "initialized"  # initialized, connecting, in_meeting, waiting_room, error, closed
        self.status_text = "Initializing..."
        self.start_time = None
        self.is_running = False
        self.worker_thread = None

    def _log(self, message, level="info"):
        self.log_callback(f"[{self.index}] {message}", level, self.index)

    def _default_log(self, message, level="info", bot_id=None):
        print(f"[{level.upper()}] {message}")

    def start(self):
        """Starts the bot in an independent daemon thread."""
        self.is_running = True
        self.status = "connecting"
        self.status_text = "Launching..."
        self.start_time = time.time()
        self.worker_thread = threading.Thread(target=self._run_browser, daemon=True)
        self.worker_thread.start()

    def _run_browser(self):
        self._log(f"Launching Chrome for '{self.name}'...", "info")

        options = Options()
        # High performance flags
        options.add_argument("--window-size=1024,768")
        options.add_argument("--disable-gpu")
        options.add_argument("--mute-audio")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--log-level=3")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-default-apps")
        options.add_argument("--disable-sync")

        # Anti-detection flags
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")

        # Block media stream prompts
        prefs = {
            "profile.default_content_setting_values.media_stream_mic": 2,
            "profile.default_content_setting_values.media_stream_camera": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_setting_values.geolocation": 2
        }
        options.add_experimental_option("prefs", prefs)

        try:
            driver_path = get_chromedriver_path()
            if driver_path:
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                self.driver = webdriver.Chrome(options=options)

            # Apply Chrome DevTools Protocol Anti-Detection injection
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    window.navigator.chrome = {
                        runtime: {},
                        loadTimes: function() {},
                        csi: function() {},
                        app: {}
                    };
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en']
                    });
                """
            })

            wait = WebDriverWait(self.driver, 25)

            # Clean Zoom Web Client join URL
            join_url = f"https://app.zoom.us/wc/{self.meeting_id}/join"
            self._log(f"Navigating to Zoom Web Client ({self.meeting_id})...", "info")
            self.driver.get(join_url)

            if not self.is_running:
                self.close()
                return

            # Allow page DOM to render initial components
            time.sleep(3)

            # Dismiss microphone/camera dialog if present
            try:
                modal_btns = self.driver.find_elements(By.XPATH, "//button[contains(., 'Continue without') or contains(., 'microphone')] | //a[contains(., 'Continue without')]")
                if modal_btns:
                    self.driver.execute_script("arguments[0].click();", modal_btns[0])
            except Exception:
                pass

            # Accept cookies / terms dialogs if shown
            try:
                cookie_btns = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Agree') or contains(text(), 'Got it')]")
                if cookie_btns:
                    self.driver.execute_script("arguments[0].click();", cookie_btns[0])
            except Exception:
                pass

            self.status_text = "Filling form..."
            self._log("Locating join fields...", "info")

            # 1. Fill Passcode (if required)
            if self.password:
                try:
                    pwd_inp = wait.until(EC.element_to_be_clickable((By.ID, "input-for-pwd")))
                    pwd_inp.click()
                    pwd_inp.send_keys(Keys.CONTROL + "a")
                    pwd_inp.send_keys(Keys.BACKSPACE)
                    pwd_inp.send_keys(self.password)
                    self._log("Entered passcode.", "info")
                except Exception:
                    for inp in self.driver.find_elements(By.TAG_NAME, "input"):
                        if "pwd" in (inp.get_attribute("id") or "").lower() or inp.get_attribute("type") == "password":
                            inp.send_keys(self.password)
                            break

            # 2. Fill Name
            try:
                name_inp = wait.until(EC.element_to_be_clickable((By.ID, "input-for-name")))
                name_inp.click()
                name_inp.send_keys(Keys.CONTROL + "a")
                name_inp.send_keys(Keys.BACKSPACE)
                name_inp.send_keys(self.name)
                self._log(f"Entered Name: {self.name}", "info")
            except Exception as e:
                self._log(f"Finding name input: {e}", "warning")

            time.sleep(1)

            # 3. Click Join Button
            self.status_text = "Submitting..."
            clicked = False
            try:
                join_btn = self.driver.find_element(By.CSS_SELECTOR, "button.preview-join-button")
                self.driver.execute_script("arguments[0].click();", join_btn)
                self._log("Clicked Join button.", "info")
                clicked = True
            except Exception:
                pass

            if not clicked:
                try:
                    join_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Join')]")
                    self.driver.execute_script("arguments[0].click();", join_btn)
                    self._log("Clicked Join button via text.", "info")
                except Exception:
                    pass

            # Minimize window immediately to taskbar so desktop stays clean
            try:
                self.driver.minimize_window()
            except Exception:
                pass

            # Wait to verify connection
            self.status_text = "Verifying..."
            time.sleep(10)

            page_src = (self.driver.page_source or "").lower()
            if "automated bots" in page_src:
                self.status = "error"
                self.status_text = "Blocked by Zoom"
                self._log("Zoom anti-bot triggered: Automated bots aren't allowed.", "error")
            elif "leave" in page_src:
                self.status = "in_meeting"
                self.status_text = "In Meeting"
                self._log(f"SUCCESS: Joined meeting room as '{self.name}'!", "success")
            elif "waiting room" in page_src or "host will let you in" in page_src or "waiting for the host" in page_src:
                self.status = "waiting_room"
                self.status_text = "Waiting Room"
                self._log(f"Participant '{self.name}' is in Host Waiting Room.", "warning")
            elif "incorrect" in page_src or "wrong" in page_src or "invalid" in page_src:
                self.status = "error"
                self.status_text = "Invalid Passcode"
                self._log(f"Error: Incorrect Passcode or Meeting ID for {self.name}", "error")
            else:
                self.status = "in_meeting"
                self.status_text = "Connected"
                self._log(f"Connected: Active session for '{self.name}'.", "info")

            # Dismiss optional audio popup
            try:
                ok_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'OK') or contains(text(), 'Got it')]")
                if ok_buttons:
                    self.driver.execute_script("arguments[0].click();", ok_buttons[0])
            except Exception:
                pass

            # Re-ensure window is minimized
            try:
                self.driver.minimize_window()
            except Exception:
                pass

            # Heartbeat loop in THIS thread
            while self.is_running:
                time.sleep(5)
                try:
                    _ = self.driver.title
                except Exception:
                    self.status = "closed"
                    self.status_text = "Closed"
                    self.is_running = False
                    self._log(f"Browser window for Bot #{self.index} closed.", "info")
                    break

        except Exception as e:
            self.status = "error"
            self.status_text = "Error"
            self._log(f"Error launching bot: {e}", "error")
            self.is_running = False

    def is_alive(self):
        """Pure in-memory status check."""
        return self.is_running and self.status in ["connecting", "in_meeting", "waiting_room"]

    def close(self):
        self.is_running = False
        self.status = "closed"
        self.status_text = "Closed"
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
        self._log(f"Bot {self.index} ({self.name}) disconnected.", "info")
