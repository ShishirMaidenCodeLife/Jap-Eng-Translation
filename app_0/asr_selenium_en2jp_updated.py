from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from googletrans import Translator
import time
from selenium.webdriver.common.action_chains import ActionChains

from const_values import g_meet_url  # Getting the google meet from the const_values.py file 

# setting up the Chrome options for selenium
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")  # to avoid detection by Google
options.add_argument("--disable-gpu")  # disabling the GPU acceleration in headless mode (optional)
options.add_argument("--no-sandbox")  # disabling sandboxing 

# Initializing WebDriver
driver_en_to_jp = webdriver.Chrome(options=options)

# Initializing ActionChains object
action = ActionChains(driver_en_to_jp)

# Opening Google Meet
meet_url = g_meet_url  # Link of the meet in the current session.
driver_en_to_jp.get(meet_url)
time.sleep(10)

try:
    # Simulate the click on "Continue without microphone and camera"
    continue_button_xpath = '//span[contains(text(), "Continue without microphone and camera")]'
    continue_button = driver_en_to_jp.find_element(By.XPATH, continue_button_xpath)
    continue_button.click()
    print("Clicked 'Continue without microphone and camera'.")

    time.sleep(5)

    # Entering the username
    username_input_xpath = '//input[@type="text"]'  # I keept this xpath based on the time I implemented this. May need update with the correct XPath for the username input field if the google meet changes the xpath.
    username_input = driver_en_to_jp.find_element(By.XPATH, username_input_xpath)
    username_input.send_keys("shishir_bot_en2jp")
    print("Entered username for Japanese-to-English.")

    time.sleep(5)

    # Autoclicking "Join now" element
    join_button_xpath = '//span[contains(text(), "Ask to join")]'
    join_button = driver_en_to_jp.find_element(By.XPATH, join_button_xpath)
    join_button.click()
    print("Clicked 'Join now' for English to Japanese.")

    # # Waiting for the meeting to start
    # time.sleep(15)
       # Wait until the meeting have joind
    print("Waiting to ensure we have joined the meeting...")
    joined = False
    while not joined:
        try:
            # Wait for an element that confirms we are in the meeting ( ie: looking for presene of caption button in the UI ensures we are in google meet now.)
            meeting_element_xpath = '/html/body/div[1]/c-wiz/div/div/div[28]/div[3]/div[10]/div/div/div[2]/div/div[3]/span/button'  
            driver_en_to_jp.find_element(By.XPATH, meeting_element_xpath)
            joined = True
            print("Successfully joined the meeting.")
        except:
            print("Not yet joined the meeting. Retrying...")
            time.sleep(5)  # Retry after a short wait of 5 seconds...



    # click on the caption button
    
    try:
        # trying first pressing 'c' to toggle captions as first option
        action.send_keys("c").perform()
        print("Pressed 'c' to turn on captions.")
    except WebDriverException:
        # if that fails, click the caption button
        try:
            caption_on_xpath = '/html/body/div[1]/c-wiz/div/div/div[28]/div[3]/div[10]/div/div/div[2]/div/div[3]/span/button'
            driver_en_to_jp.find_element(By.XPATH, caption_on_xpath).click()
            print("Clicked on 'Turn on captions' using the button.")
        except NoSuchElementException:
            print("Failed to turn on captions with both methods.")

    time.sleep(10)


    # Google Translate API initialization
    translator = Translator()

    # XPath for subtitles (Make sure this XPath is accurate in future Google Meet UI changes)
    # subtitles_xpath = '//*[@class="T4LgNb"]'
    speaker_info = '//*[@class="TBMuR bj4p3b"]'
    subtitles_xpath = '//*[@class="iTTPOb VbkSUe"]'  #correct XPath for subtitles

    while True:
        # Locating the subtitles container
        current_speaker = driver_en_to_jp.find_elements(By.XPATH, speaker_info)
        subtitles_elements = driver_en_to_jp.find_elements(By.XPATH, subtitles_xpath)

        if subtitles_elements:
            for speaker_iden, subtitle_element in zip(current_speaker,subtitles_elements):
                speaker_name = speaker_iden.text
                subtitle_text = subtitle_element.text

                # Translate the subtitle text from Japanese to English
                translation = translator.translate(subtitle_text, src='en', dest='ja')

                # original and translated text
                print(f"Speaker Name: {speaker_name}")
                print(f"Original (EN): {subtitle_text}")
                print(f"Translated (JP): {translation.text}")

        else:
            print("Waiting for subtitles...")

        # Waiting for subtitles to update
        time.sleep(10) 

except Exception as e:
    print(f"An error occurred in Japanese-to-English script: {e}")

finally:
    driver_en_to_jp.quit()
