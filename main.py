import sys
import random
import time
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QPushButton, 
                            QTextEdit, QFileDialog, QLabel, QWidget, QHBoxLayout)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (TimeoutException, NoSuchElementException, 
                                       WebDriverException)

class WhatsAppBotGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setupState()

    def initUI(self):
        self.setWindowTitle("WhatsApp Bot by @sudo1996")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("""
            background-color: #f5f5f5;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        """)

        main_layout = QVBoxLayout()
        self.createHeader(main_layout)
        self.createUploadSection(main_layout)
        self.createMediaUploadSection(main_layout)
        self.createControlButtons(main_layout)
        self.createLogDisplay(main_layout)
        self.createFooter(main_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def setupState(self):
        self.phone_numbers = []
        self.messages = []
        self.image_path = None
        self.video_path = None
        self.audio_path = None
        self.bot_running = False
        self.driver = None

    def createHeader(self, layout):
        header = QHBoxLayout()
        logo = QLabel(self)
        pixmap = QPixmap("logo.png").scaled(80, 80, Qt.KeepAspectRatio)
        logo.setPixmap(pixmap)
        header.addWidget(logo)

        title = QLabel("WA Auto Sender by @sudo1996")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

    def createUploadSection(self, layout):
        self.upload_numbers_btn = self.createButton(
            "Upload Contacts", "#2ecc71", self.upload_numbers)
        self.upload_messages_btn = self.createButton(
            "Upload Messages", "#3498db", self.upload_messages)
        layout.addWidget(self.upload_numbers_btn)
        layout.addWidget(self.upload_messages_btn)

    def createMediaUploadSection(self, layout):
        media_layout = QHBoxLayout()
        self.upload_image_btn = self.createButton(
            "Image", "#f1c40f", self.upload_image)
        self.upload_video_btn = self.createButton(
            "Video", "#9b59b6", self.upload_video)
        self.upload_audio_btn = self.createButton(
            "Audio", "#1abc9c", self.upload_audio)
        media_layout.addWidget(self.upload_image_btn)
        media_layout.addWidget(self.upload_video_btn)
        media_layout.addWidget(self.upload_audio_btn)
        layout.addLayout(media_layout)

    def createControlButtons(self, layout):
        control_layout = QHBoxLayout()
        self.start_btn = self.createButton(
            "▶ Start", "#27ae60", self.start_automation)
        self.stop_btn = self.createButton(
            "⏹ Stop", "#e74c3c", self.stop_automation)
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        layout.addLayout(control_layout)

    def createLogDisplay(self, layout):
        self.log_display = QTextEdit()
        self.log_display.setStyleSheet("""
            background-color: white;
            color: #34495e;
            border-radius: 8px;
            padding: 12px;
            font-size: 14px;
        """)
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)

    def createFooter(self, layout):
        footer = QLabel("© 2025 WhatsApp Marketing Bot by @sudo1996 | v1.0")
        footer.setStyleSheet("""
            color: #7f8c8d;
            font-size: 12px;
            padding-top: 15px;
        """)
        footer.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer)

    def createButton(self, text, color, callback):
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darkenColor(color)};
            }}
        """)
        btn.clicked.connect(callback)
        return btn

    def darkenColor(self, hex_color, factor=0.8):
        rgb = [int(hex_color[i:i+2], 16) for i in (1, 3, 5)]
        darker = [int(c * factor) for c in rgb]
        return "#" + "".join(f"{c:02x}" for c in darker)

    def upload_numbers(self):
        file = QFileDialog.getOpenFileName(self, "Select Contacts File", "", 
                                         "Text Files (*.txt);;CSV Files (*.csv)")[0]
        if file:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    self.phone_numbers = [line.strip() for line in f if line.strip()]
                self.log(f"Loaded {len(self.phone_numbers)} contacts")
            except Exception as e:
                self.log(f"Error loading contacts: {str(e)}")

    def upload_messages(self):
        file = QFileDialog.getOpenFileName(self, "Select Messages File", "", 
                                         "Text Files (*.txt);;CSV Files (*.csv)")[0]
        if file:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.messages = self.parseMessages(content)
                self.log(f"Loaded {len(self.messages)} messages")
            except Exception as e:
                self.log(f"Error loading messages: {str(e)}")

    def parseMessages(self, content):
        """Improved message parser using regex"""
        pattern = re.compile(r'"((?:[^"\\]|\\.)*)"', re.DOTALL)
        matches = pattern.findall(content)
        return [match.replace('\\"', '"').strip() for match in matches if match.strip()]

    def upload_image(self):
        self.image_path = self.getMediaPath("Image", "Images (*.png *.jpg *.jpeg)")
        if self.image_path:
            self.log(f"Image ready: {self.image_path.split('/')[-1]}")

    def upload_video(self):
        self.video_path = self.getMediaPath("Video", "Videos (*.mp4 *.avi *.mkv)")
        if self.video_path:
            self.log(f"Video ready: {self.video_path.split('/')[-1]}")

    def upload_audio(self):
        self.audio_path = self.getMediaPath("Audio", "Audio (*.mp3 *.wav)")
        if self.audio_path:
            self.log(f"Audio ready: {self.audio_path.split('/')[-1]}")

    def getMediaPath(self, media_type, filter):
        path = QFileDialog.getOpenFileName(self, f"Select {media_type} File", "", filter)[0]
        return path if path else None

    def start_automation(self):
        if not self.validateSetup():
            return
        
        self.bot_running = True
        self.driver = webdriver.Chrome()
        
        try:
            self.log("Initializing WhatsApp Web...")
            self.driver.get("https://web.whatsapp.com")
            self.waitForLogin()
            self.processContacts()
        except Exception as e:
            self.log(f"Automation failed: {str(e)}")
        finally:
            self.cleanup()

    def validateSetup(self):
        if not self.phone_numbers:
            self.log("Error: No contacts loaded!")
            return False
        if not self.messages and not any([self.image_path, self.video_path, self.audio_path]):
            self.log("Error: No content to send!")
            return False
        return True

    def waitForLogin(self):
        try:
            WebDriverWait(self.driver, 120).until(
                EC.invisibility_of_element_located(
                    (By.CSS_SELECTOR, "canvas[aria-label='Scan this QR code to link a device!']")
                )
            )
            self.log("Login successful!")
        except TimeoutException:
            self.log("Login timed out. Please try again.")
            raise

    def processContacts(self):
        total = len(self.phone_numbers)
        for idx, number in enumerate(self.phone_numbers, 1):
            if not self.bot_running:
                break
            
            self.log(f"Processing {number} ({idx}/{total})")
            try:
                self.sendToNumber(number)
                self.randomDelay()
            except Exception as e:
                self.log(f"Failed to send to {number}: {str(e)}")

    def sendToNumber(self, number):
        self.driver.get(f"https://web.whatsapp.com/send?phone={number}")
        
        if self.messages:
            self.sendTextMessage()
        
        media_sent = False
        if self.image_path:
            self.sendMedia(self.image_path, "image")
            media_sent = True
        if self.video_path:
            self.sendMedia(self.video_path, "video")
            media_sent = True
        if self.audio_path:
            self.sendMedia(self.audio_path, "audio") 
            media_sent = True
        
        if media_sent:
            self.randomDelay(media=True)

    def sendTextMessage(self):
        try:
            input_box = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']")
                )
            )
            
            message = random.choice(self.messages)
            
            # Properly handle Arabic text and formatting
            self.driver.execute_script(f"""
                const input = arguments[0];
                const text = arguments[1];
                
                input.focus();
                document.execCommand('insertText', false, text);
                
                // Trigger necessary events
                const inputEvent = new Event('input', {{ bubbles: true }});
                input.dispatchEvent(inputEvent);
                
                const changeEvent = new Event('change', {{ bubbles: true }});
                input.dispatchEvent(changeEvent);
            """, input_box, message)
            
            # Send with natural delay
            time.sleep(0.5)
            input_box.send_keys(Keys.ENTER)
            self.log("تم إرسال الرسالة بنجاح")
            
        except Exception as e:
            self.log(f"فشل الإرسال: {str(e)}")
            raise

    def sendMedia(self, path, media_type):
        try:
            self.openAttachmentMenu()
            self.selectMediaOption()
            self.uploadFile(path)
            self.confirmSend()
            self.log(f"{media_type.capitalize()} sent successfully")
        except Exception as e:
            self.log(f"Failed to send {media_type}: {str(e)}")
            raise

    def openAttachmentMenu(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span[data-icon='attach-menu-plus']"))
        ).click()

    def selectMediaOption(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Photos & Videos')]"))
        ).click()

    def uploadFile(self, path):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
        ).send_keys(path)

    def confirmSend(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span[data-icon='send']"))
        ).click()
        time.sleep(2)

    def randomDelay(self, media=False):
        base = 10 if media else 5
        delay = random.randint(base, base + 15)
        self.log(f"Waiting {delay} seconds...")
        time.sleep(delay)

    def stop_automation(self):
        self.bot_running = False
        self.log("Stopping automation...")

    def cleanup(self):
        if self.driver:
            self.driver.quit()
        self.bot_running = False
        self.log("Automation completed")

    def log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log_display.append(f"[{timestamp}] {message}")
        QApplication.processEvents()

    def closeEvent(self, event):
        self.stop_automation()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WhatsAppBotGUI()
    window.show()
    sys.exit(app.exec_())
