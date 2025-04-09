import tkinter as tk
from tkinter import scrolledtext
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from googletrans import Translator
import time
import threading

class TranslationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Translation App")

        # UI elements for Google Meet code input and buttons
        self.code_label = tk.Label(root, text="Google Meet Code:")
        self.code_label.pack()
        
        self.code_entry = tk.Entry(root, width=30)
        self.code_entry.pack()

        self.start_button = tk.Button(root, text="Start Translation", command=self.start_translation)
        self.start_button.pack()

        self.stop_button = tk.Button(root, text="Stop Translation", command=self.stop_translation, state=tk.DISABLED)
        self.stop_button.pack()

        self.output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20, width=60)
        self.output_text.pack()

        self.translator = Translator()
        self.drivers = {"en_to_jp": None, "jp_to_en": None}
        self.running = {"en_to_jp": False, "jp_to_en": False}

    def start_translation(self):
        self.running["en_to_jp"] = True
        self.running["jp_to_en"] = True
        self.stop_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.DISABLED)

        meet_code = self.code_entry.get().strip()
        if not meet_code:
            self.update_output_text("Please enter a Google Meet code.")
            self.stop_translation()
            return

        meet_url = f'https://meet.google.com/{meet_code}'

        # starting the Selenium tasks in separate threads for both bots
        thread_en_to_jp = threading.Thread(target=self.run_selenium_task, args=(meet_url, "shishir_bot_en2jp", "en_to_jp"))
        thread_jp_to_en = threading.Thread(target=self.run_selenium_task, args=(meet_url, "shishir_bot_jp2en", "jp_to_en"))

        thread_en_to_jp.start()
        thread_jp_to_en.start()

    def stop_translation(self):
        self.running["en_to_jp"] = False
        self.running["jp_to_en"] = False
        for driver in self.drivers.values():
            if driver:
                driver.quit()
        self.drivers = {"en_to_jp": None, "jp_to_en": None}
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def run_selenium_task(self, meet_url, username, mode):
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")

        driver = webdriver.Chrome(options=options)
        self.drivers[mode] = driver

        driver.get(meet_url)
        time.sleep(10)

        try:
            continue_button_xpath = '//span[contains(text(), "Continue without microphone and camera")]'
            continue_button = driver.find_element(By.XPATH, continue_button_xpath)
            continue_button.click()
            time.sleep(5)

            username_input_xpath = '//input[@type="text"]'
            username_input = driver.find_element(By.XPATH, username_input_xpath)
            username_input.send_keys(username)

            time.sleep(5)

            join_button_xpath = '//span[contains(text(), "Ask to join")]'
            join_button = driver.find_element(By.XPATH, join_button_xpath)
            join_button.click()

            time.sleep(10)

            subtitles_xpath = '//*[@class="iTTPOb VbkSUe"]'

            while self.running[mode]:
                subtitles_elements = driver.find_elements(By.XPATH, subtitles_xpath)

                if subtitles_elements:
                    for subtitle_element in subtitles_elements:
                        subtitle_text = subtitle_element.text
                        if mode == "en_to_jp":
                            translation = self.translator.translate(subtitle_text, src='en', dest='ja')
                            output_text = f"Output 1 (JP): {translation.text}\n"
                        else:
                            translation = self.translator.translate(subtitle_text, src='ja', dest='en')
                            output_text = f"Output 2 (EN): {translation.text}\n"

                        self.update_output_text(output_text)

                else:
                    if self.running[mode]:
                        self.update_output_text("...")

                time.sleep(10)

        except Exception as e:
            self.update_output_text(f"An error occurred in {mode} task: {e}")

        finally:
            driver.quit()
            self.drivers[mode] = None

    def update_output_text(self, text):
        # updating the text area in the main thread
        self.root.after(0, lambda: self.output_text.insert(tk.END, text + '\n'))

if __name__ == "__main__":
    root = tk.Tk()
    app = TranslationApp(root)
    root.mainloop()
