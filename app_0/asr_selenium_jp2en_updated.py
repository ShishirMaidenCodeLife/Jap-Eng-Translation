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
driver_jp_to_en = webdriver.Chrome(options=options)

# Initializing ActionChains object
action = ActionChains(driver_jp_to_en)

# Opening Google Meet
meet_url = g_meet_url  # Link of the meet in the current session
driver_jp_to_en.get(meet_url)
time.sleep(10)

try:
    # Simulate the click on "Continue without microphone and camera"
    continue_button_xpath = '//span[contains(text(), "Continue without microphone and camera")]'
    continue_button = driver_jp_to_en.find_element(By.XPATH, continue_button_xpath)
    continue_button.click()
    print("Clicked 'Continue without microphone and camera'.")

    time.sleep(5)

    # Enter the username
    username_input_xpath = '//input[@type="text"]'  # I keept this xpath based on the time I implemented this. May need update with the correct XPath for the username input field if the google meet changes the xpath.
    username_input = driver_jp_to_en.find_element(By.XPATH, username_input_xpath)
    username_input.send_keys("shishir_bot_jp_2_en")
    print("Entered username for Japanese-to-English.")

    time.sleep(5)

    # Autoclicking "Join now" element
    join_button_xpath = '//span[contains(text(), "Ask to join")]'
    join_button = driver_jp_to_en.find_element(By.XPATH, join_button_xpath)
    join_button.click()
    print("Clicked 'Join now' for Japanese-to-English.")

    # # Waiting for the meeting to start
    # time.sleep(15)
       # Wait until the meeting have joind
    print("Waiting to ensure we have joined the meeting...")
    joined = False
    while not joined:
        try:
            # Wait for an element that confirms we are in the meeting ( ie: looking for presene of caption button in the UI ensures we are in google meet now.)
            meeting_element_xpath = '/html/body/div[1]/c-wiz/div/div/div[28]/div[3]/div[10]/div/div/div[2]/div/div[3]/span/button'  
            driver_jp_to_en.find_element(By.XPATH, meeting_element_xpath)
            joined = True
            print("Successfully joined the meeting.")
        except:
            print("Not yet joined the meeting. Retrying...")
            time.sleep(5)  # Retry after a short wait of 5 seconds...

    # to handle potential pop-ups (noticed the popup from permission requests were common)
    try:
        allow_button = driver.find_element(By.XPATH, '//button[contains(text(), "Allow")]')
        allow_button.click()
        print("Clicked 'Allow' button for permissions.")
    except Exception as e:
        # print(f"No permission pop-up or already handled: {e}")
        print(f"No permission pop-up or already handled")

    # click on the caption button
    
    try:
        # trying first pressing 'c' to toggle captions as first option
        action.send_keys("c").perform()
        print("Pressed 'c' to turn on captions.")
    except WebDriverException:
        # If that fails, click the caption button
        try:
            caption_on_xpath = '/html/body/div[1]/c-wiz/div/div/div[28]/div[3]/div[10]/div/div/div[2]/div/div[3]/span/button'
            driver_jp_to_en.find_element(By.XPATH, caption_on_xpath).click()
            print("Clicked on 'Turn on captions' using the button.")
        except NoSuchElementException:
            print("Failed to turn on captions with both methods.")

    time.sleep(10)

    print("Now let's try clicking on language settings.")

    # Click on the caption settings
    caption_settings_xpath = '/html/body/div[1]/c-wiz/div/div/div[28]/div[3]/div[3]/div[2]/div/span/div[1]/button'
    caption_settings = driver_jp_to_en.find_element(By.XPATH, caption_settings_xpath)
    caption_settings.click()
    print("Opened settings.")

    time.sleep(3)

    # select Japanese language for captions using key presses'

    # Simulate pressing TAB key, then ENTER, 'j', ENTER, and ESC keys
    try:
    # simulating TAB key press directly using action chain
        for _ in range(7):
            action.send_keys(Keys.TAB).perform()
    except WebDriverException as e:
        print(f"Action chain failed: {e}")
        try:
            # Fallback: Use the traditional way to find and click on the window box
            caption_settingswindow_xpath = '/html/body'
            caption_settingswindow = driver_jp_to_en.find_element(By.XPATH, caption_settingswindow_xpath)
            # Press TAB 8 times (adjust if necessary)
            for _ in range(8):  # here dont know whay it needs 8 number of TAB presses to reach the target option though it should be 7.
                caption_settingswindow.send_keys(Keys.TAB)
                time.sleep(0.5)  # Reduced sleep time for faster execution
        except NoSuchElementException as e:
            print(f"Element not found: {e}")
            raise  # Re-raise the exception if needed

    time.sleep(2)
    # Press ENTER to open the language dropdown
   
    # Use ActionChains to send ENTER key
    action = ActionChains(driver_jp_to_en)
    action.send_keys(Keys.ENTER).perform()  # Send ENTER key using ActionChains
    print("Opened language dropdown.")

    time.sleep(2)

    # pressing 'j' to select the language that starts with 'j' (Japanese)
    action.send_keys("j").perform()
    time.sleep(1)

    # Pressing ENTER to confirm the selection of Japanese
    action.send_keys(Keys.ENTER).perform()
    print("Selected Japanese language.")

    time.sleep(1)

    # Pressing ESC to close the settings menu
    action.send_keys(Keys.ESCAPE).perform()
    print("Closed settings menu after choosing japanese langauge.")

    time.sleep(2)

    # Initializing the Google Translate API
    translator = Translator()

    # XPath for subtitles (we need to make sure this XPath is accurate in future Google Meet UI changes)
    # speaker_info_and_msg_together = '//*[@class="TBMuR bj4p3b"]'
    speaker_info = '//*[@class="zs7s8d jxFHg"]'
    subtitles_xpath = '//*[@class="iTTPOb VbkSUe"]'  

    while True:
        # Locating the subtitles container
        current_speaker = driver_jp_to_en.find_elements(By.XPATH, speaker_info)
        subtitles_elements = driver_jp_to_en.find_elements(By.XPATH, subtitles_xpath)

        if subtitles_elements:
            for speaker_iden, subtitle_element in zip(current_speaker,subtitles_elements):
                speaker_name = speaker_iden.text
                subtitle_text = subtitle_element.text

                # Translate the subtitle text from Japanese to English
                translation = translator.translate(subtitle_text, src='ja', dest='en')

                # Print original and translated text
                print(f"Speaker Name: {speaker_name}")
                print(f"Original (JP): {subtitle_text}")
                print(f"Translated (EN): {translation.text}")

        else:
            print("Waiting for subtitles...")

        # Waiting for subtitles to update
        time.sleep(10)

except Exception as e:
    print(f"An error occurred in Japanese-to-English script: {e}")

finally:
    driver_jp_to_en.quit()
