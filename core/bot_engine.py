# -*- coding: utf-8 -*-
"""
Zoom Bot Engine
Handles individual Selenium WebDriver instance for Zoom Web Client.
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ZoomBotInstance:
    def __init__(self, index, meeting_id, password, name, headless=False, log_callback=None):
        self.index = index
        self.meeting_id = str(meeting_id).strip().replace(" ", "")
        self.password = str(password).strip()
        self.name = str(name).strip()
        self.headless = headless
        self.log_callback = log_callback or self._default_log
        self.driver = None
        self.status = "initialized"  # initialized, connecting, in_meeting, waiting_room, error, closed
        self.status_text = "Initializing..."
        self.start_time = None
        self.is_running = False

    def _log(self, message, level="info"):
        self.log_callback(f"[{self.index}] {message}", level, self.index)

    def _default_log(self, message, level="info", bot_id=None):
        print(f"[{level.upper()}] {message}")

    def start(self):
        self.is_running = True
        self.status = "connecting"
        self.status_text = "Launching browser..."
        self.start_time = time.time()
        self._log(f"Launching Chrome for participant: '{self.name}'...", "info")

        options = Options()
        # High performance & RAM saving flags
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
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option("useAutomationExtension", False)

        if self.headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1280,800")
            self._log("Running in Headless mode (saves ~70% RAM).", "info")
        else:
            options.add_argument("--window-size=1024,768")

        # Block audio, video, camera, and notifications
        prefs = {
            "profile.default_content_setting_values.media_stream_mic": 2,
            "profile.default_content_setting_values.media_stream_camera": 2,
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_setting_values.geolocation": 2
        }
        options.add_experimental_option("prefs", prefs)

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            wait = WebDriverWait(self.driver, 40)

            # Clean Zoom Web Client join URL
            join_url = f"https://app.zoom.us/wc/{self.meeting_id}/join"
            self._log(f"Navigating to Zoom Web Client ({self.meeting_id})...", "info")
            self.driver.get(join_url)
            time.sleep(5)

            if not self.is_running:
                self.close()
                return False

            # Check if embedded in an iframe
            try:
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                if iframes:
                    self.driver.switch_to.frame(iframes[0])
            except Exception:
                pass

            # Accept cookies / terms dialogs if shown
            try:
                cookie_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Accept') or contains(text(), 'Agree') or contains(text(), 'Got it')]")
                if cookie_buttons:
                    self.driver.execute_script("arguments[0].click();", cookie_buttons[0])
            except Exception:
                pass

            # Wait for join input boxes to appear
            self.status_text = "Filling form..."
            self._log("Waiting for join form inputs...", "info")
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))

            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
            pwd_filled = False
            name_filled = False

            # Fill name and password fields
            for inp in all_inputs:
                try:
                    inp_type = (inp.get_attribute("type") or "").lower()
                    inp_id = (inp.get_attribute("id") or "").lower()
                    inp_placeholder = (inp.get_attribute("placeholder") or "").lower()

                    # Password field
                    if (inp_type == "password" or "pwd" in inp_id or "passcode" in inp_placeholder) and not pwd_filled:
                        if self.password:
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", inp)
                            inp.click()
                            inp.send_keys(Keys.CONTROL + "a")
                            inp.send_keys(Keys.BACKSPACE)
                            inp.send_keys(self.password)
                            pwd_filled = True
                            self._log("Entered passcode.", "info")

                    # Name field
                    elif (inp_type == "text" or "name" in inp_id or "name" in inp_placeholder) and not name_filled:
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", inp)
                        inp.click()
                        inp.send_keys(Keys.CONTROL + "a")
                        inp.send_keys(Keys.BACKSPACE)
                        inp.send_keys(self.name)
                        name_filled = True
                        self._log(f"Entered Name: {self.name}", "info")
                except Exception:
                    continue

            time.sleep(2)

            # Click Join button
            self.status_text = "Submitting..."
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            clicked_join = False
            for btn in buttons:
                txt = (btn.text or "").lower()
                cls = (btn.get_attribute("class") or "").lower()
                if "join" in txt or "preview-join-button" in cls or "join-btn" in cls:
                    self.driver.execute_script("arguments[0].click();", btn)
                    self._log("Clicked Join button.", "info")
                    clicked_join = True
                    break

            if not clicked_join:
                # Try finding button by xpath
                try:
                    join_btn = self.driver.find_element(By.XPATH, "//button[contains(translate(text(), 'JOIN', 'join'), 'join')]")
                    self.driver.execute_script("arguments[0].click();", join_btn)
                    self._log("Clicked Join button via XPath.", "info")
                except Exception:
                    pass

            # Wait to verify connection
            self.status_text = "Verifying..."
            time.sleep(8)

            page_src = (self.driver.page_source or "").lower()
            if "leave" in page_src or "mute" in page_src or "participants" in page_src:
                self.status = "in_meeting"
                self.status_text = "In Meeting"
                self._log(f"SUCCESS: Joined meeting as '{self.name}'!", "success")
            elif "waiting room" in page_src or "host will let you in" in page_src:
                self.status = "waiting_room"
                self.status_text = "Waiting Room"
                self._log(f"Notice: '{self.name}' is in the Host Waiting Room.", "warning")
            elif "incorrect" in page_src or "wrong" in page_src or "invalid" in page_src:
                self.status = "error"
                self.status_text = "Invalid Passcode"
                self._log(f"Error: Incorrect Passcode or Meeting ID for {self.name}", "error")
            else:
                self.status = "in_meeting"
                self.status_text = "Connected"
                self._log(f"Connected: Browser session active for '{self.name}'.", "info")

            # Dismiss optional audio popup
            try:
                ok_buttons = self.driver.find_elements(By.XPATH, "//button[contains(text(), 'OK') or contains(text(), 'Got it')]")
                if ok_buttons:
                    self.driver.execute_script("arguments[0].click();", ok_buttons[0])
            except Exception:
                pass

            # Minimize window if headed mode to save desktop space
            if not self.headless:
                try:
                    self.driver.minimize_window()
                except Exception:
                    pass

            return True

        except Exception as e:
            self.status = "error"
            self.status_text = f"Error: {str(e)[:30]}"
            self._log(f"Error: {e}", "error")
            return False

    def is_alive(self):
        if not self.driver or not self.is_running:
            return False
        try:
            _ = self.driver.window_handles
            return True
        except Exception:
            self.status = "closed"
            self.status_text = "Closed"
            self.is_running = False
            return False

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
