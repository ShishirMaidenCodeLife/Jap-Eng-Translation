import tkinter as tk
from tkinter import scrolledtext
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from googletrans import Translator
import time
import threading

class TranslationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Google Meet Translation App")

        # UI elements for Google Meet code input and buttons
        self.code_label = tk.Label(root, text="Google Meet Code:")
        self.code_label.pack()
        
        self.code_entry = tk.Entry(root, width=30)
        self.code_entry.pack()

        self.mode_var = tk.StringVar(value="en_to_jp")
        self.en_to_jp_button = tk.Radiobutton(root, text="English to Japanese", variable=self.mode_var, value="en_to_jp")
        self.en_to_jp_button.pack()

        self.jp_to_en_button = tk.Radiobutton(root, text="Japanese to English", variable=self.mode_var, value="jp_to_en")
        self.jp_to_en_button.pack()

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
        self.running[self.mode_var.get()] = True
        self.stop_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.DISABLED)

        meet_code = self.code_entry.get().strip()
        if not meet_code:
            self.update_output_text("Please enter a Google Meet code.")
            self.stop_translation()
            return

        meet_url = f'https://meet.google.com/{meet_code}'

        # starting the Selenium tasks in separate threads based on selected mode
        thread = threading.Thread(target=self.run_selenium_task, args=(meet_url, "shishir_bot", self.mode_var.get()))
        thread.start()

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

            if mode == "jp_to_en":
                self.setup_japanese_mode(driver)

            subtitles_xpath = '//*[@class="iTTPOb VbkSUe"]'
            speaker_info_xpath = '//*[@class="zs7s8d jxFHg"]'

            while self.running[mode]:
                subtitles_elements = driver.find_elements(By.XPATH, subtitles_xpath)

                if subtitles_elements:
                    current_speaker = driver.find_elements(By.XPATH, speaker_info_xpath)
                    for speaker_iden, subtitle_element in zip(current_speaker, subtitles_elements):
                        speaker_name = speaker_iden.text
                        subtitle_text = subtitle_element.text

                        if mode == "en_to_jp":
                            translation = self.translator.translate(subtitle_text, src='en', dest='ja')
                            output_text = f"{speaker_name}: {subtitle_text} -> {translation.text}\n"
                        else:
                            translation = self.translator.translate(subtitle_text, src='ja', dest='en')
                            output_text = f"{speaker_name}: {subtitle_text} -> {translation.text}\n"

                        self.update_output_text(output_text)

                else:
                    if self.running[mode]:
                        self.update_output_text("Waiting for subtitles...")

                time.sleep(10)

        except Exception as e:
            self.update_output_text(f"An error occurred in {mode} task: {e}")

        finally:
            driver.quit()
            self.drivers[mode] = None

    def setup_japanese_mode(self, driver):
        # click on the caption button to turn on captions
        action = ActionChains(driver)
        try:
            action.send_keys("c").perform()
            time.sleep(5)
            self.update_output_text("Turned on captions.")
        except Exception:
            self.update_output_text("Failed to turn on captions with 'c'.")

        # click on the caption settings
        caption_settings_xpath = '/html/body/div[1]/c-wiz/div/div/div[28]/div[3]/div[3]/div[2]/div/span/div[1]/button'
        caption_settings = driver.find_element(By.XPATH, caption_settings_xpath)
        caption_settings.click()
        self.update_output_text("Opened settings.")

        time.sleep(3)

        # simulate TAB key presses to select Japanese language
        for _ in range(8): # Based on the number of TAB presses required ( I checked manually)
            action.send_keys(Keys.TAB).perform()
            time.sleep(0.5)

        action.send_keys(Keys.ENTER).perform()  # opening language dropdown first
        time.sleep(2)
        action.send_keys("j").perform()  # select Japanese since "j" navigates to language options.
        time.sleep(1)
        action.send_keys(Keys.ENTER).perform()  # confirming selection
        time.sleep(1)
        action.send_keys(Keys.ESCAPE).perform()  # close the settings
        self.update_output_text("Selected Japanese language for captions.")

    def update_output_text(self, text):
        self.root.after(0, lambda: self.output_text.insert(tk.END, text + '\n'))

if __name__ == "__main__":
    root = tk.Tk()
    app = TranslationApp(root)
    root.mainloop()
