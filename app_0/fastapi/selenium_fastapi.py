from fastapi import FastAPI, BackgroundTasks
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from googletrans import Translator
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# global variable to store the Google Meet URL
g_meet_url = ""

# basic CORS to allow all for experimentation purposes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MeetURL(BaseModel):
    meet_url: str

def run_translation_script(direction: str):
    global g_meet_url
    
    # setting up the Chrome options for selenium
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(options=options)
    action = ActionChains(driver)

    driver.get(g_meet_url)
    time.sleep(10)

    try:
        # Simulate the click on "Continue without microphone and camera"
        continue_button_xpath = '//span[contains(text(), "Continue without microphone and camera")]'
        continue_button = driver.find_element(By.XPATH, continue_button_xpath)
        continue_button.click()
        print("Clicked 'Continue without microphone and camera'.")
        time.sleep(5)

        # Entering the username based on direction
        username_input_xpath = '//input[@type="text"]' # I keept this xpath based on the time I implemented this. May need update with the correct XPath for the username input field if the google meet changes the xpath.
        username_input = driver.find_element(By.XPATH, username_input_xpath)

        if direction == "en_to_jp":
            username_input.send_keys("shishir_bot_en2jp")
            print("Entered username for English-to-Japanese.")
        else:
            username_input.send_keys("shishir_bot_jp_2_en")
            print("Entered username for Japanese-to-English.")

        time.sleep(5)

        # Autoclicking "Join now" element
        join_button_xpath = '//span[contains(text(), "Ask to join")]'
        join_button = driver.find_element(By.XPATH, join_button_xpath)
        join_button.click()
        print(f"Clicked 'Join now' for {direction.replace('_', ' ')}.")

        # Waiting until the meeting have joind
        print("Waiting to ensure we have joined the meeting...")
        joined = False
        while not joined:
            try:
                meeting_element_xpath = '/html/body/div[1]/c-wiz/div/div/div[28]/div[3]/div[10]/div/div/div[2]/div/div[3]/span/button'
                driver.find_element(By.XPATH, meeting_element_xpath)
                joined = True
                print("Successfully joined the meeting.")
            except:
                print("Not yet joined the meeting. Retrying...")
                time.sleep(5)

        # click on the caption button
        try:
            action.send_keys("c").perform()
            print("Pressed 'c' to turn on captions.")
        except WebDriverException:
            try:
                caption_on_xpath = '/html/body/div[1]/c-wiz/div/div/div[28]/div[3]/div[10]/div/div/div[2]/div/div[3]/span/button'
                driver.find_element(By.XPATH, caption_on_xpath).click()
                print("Clicked on 'Turn on captions' using the button.")
            except NoSuchElementException:
                print("Failed to turn on captions with both methods.")

        time.sleep(10)

        #  Google Translate API initilization
        translator = Translator()
        
        if direction == "jp_to_en":
            # opening caption settings to set the language to Japanese
            print("Now let's try clicking on language settings.")
            caption_settings_xpath = '/html/body/div[1]/c-wiz/div/div/div[28]/div[3]/div[3]/div[2]/div/span/div[1]/button'
            caption_settings = driver.find_element(By.XPATH, caption_settings_xpath)
            caption_settings.click()
            print("Opened settings.")
            time.sleep(3)

            # simulate TAB key presses to select Japanese language ( Navigating through the settings menu )
            for _ in range(7):  # Based on the number of TAB presses required ( I checked manually)
                action.send_keys(Keys.TAB).perform()
                time.sleep(0.5)

            action.send_keys(Keys.ENTER).perform()
            print("Opened language dropdown.")
            time.sleep(2)

            action.send_keys("j").perform()
            time.sleep(1)
            action.send_keys(Keys.ENTER).perform()
            print("Selected Japanese language.")
            time.sleep(1)
            action.send_keys(Keys.ESCAPE).perform()
            print("Closed settings menu after choosing Japanese language.")
            time.sleep(2)

        # defining the XPaths for subtitles and speaker info
        speaker_info = '//*[@class="TBMuR bj4p3b"]' if direction == "en_to_jp" else '//*[@class="zs7s8d jxFHg"]'
        subtitles_xpath = '//*[@class="iTTPOb VbkSUe"]'

        while True:
            current_speaker = driver.find_elements(By.XPATH, speaker_info)
            subtitles_elements = driver.find_elements(By.XPATH, subtitles_xpath)

            if subtitles_elements:
                for speaker_iden, subtitle_element in zip(current_speaker, subtitles_elements):
                    speaker_name = speaker_iden.text
                    subtitle_text = subtitle_element.text
                    
                    # Source and destination languages detection
                    src_lang = 'en' if direction == "en_to_jp" else 'ja'
                    dest_lang = 'ja' if direction == "en_to_jp" else 'en'
                    
                    # translate the subtitle text
                    translation = translator.translate(subtitle_text, src=src_lang, dest=dest_lang)

                    # Diplsying original and translated text
                    print(f"Speaker Name: {speaker_name}")
                    print(f"Original ({src_lang.upper()}): {subtitle_text}")
                    print(f"Translated ({dest_lang.upper()}): {translation.text}")

            else:
                print("Waiting for subtitles...")

            time.sleep(10) # Waiting for subtitles to update

    except Exception as e:
        print(f"An error occurred in {direction.replace('_', ' ')} script: {e}")
    finally:
        driver.quit()

@app.post("/start")
def start_translation(meet_url: MeetURL):
    global g_meet_url
    g_meet_url = meet_url.meet_url
    
    # start both translation scripts in separate threads
    threading.Thread(target=run_translation_script, args=("en_to_jp",)).start()
    threading.Thread(target=run_translation_script, args=("jp_to_en",)).start()
    
    return {"message": "Translation scripts started."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
