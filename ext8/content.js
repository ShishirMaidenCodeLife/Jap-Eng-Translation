// Global Variables
let intervalId;
let currentSourceLang = 'en'; // Default to English to Japanese
let currentTargetLang = 'ja';   // Default to Japanese
const popupId = 'captionsPopup'; // ID for the popup
let captionsEnabled = true; // Track if captions are enabled

// Function to create a floating, draggable, and resizable popup for displaying captions and speakers
function createPopup() {
    let existingPopup = document.getElementById(popupId);
    if (existingPopup) {
        existingPopup.style.display = 'block'; // Show if exists
        return existingPopup;
    }

    const popup = document.createElement('div');
    popup.id = popupId;
    popup.style.position = 'fixed';
    popup.style.bottom = '20px';
    popup.style.right = '20px';
    popup.style.width = '400px';  // Increased width
    popup.style.height = '300px';  // Increased height for buttons
    popup.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
    popup.style.color = 'white';
    popup.style.padding = '10px';
    popup.style.zIndex = '9999';
    popup.style.border = '1px solid white';
    popup.style.borderRadius = '8px';
    popup.style.cursor = 'move';

    // Add resizable edges (for dragging to resize)
    addResizeHandles(popup);

    const buttonContainer = document.createElement('div');
    buttonContainer.style.display = 'flex';
    buttonContainer.style.marginBottom = '10px'; // Space between buttons and captions

    // Toggle Captions Button
    const toggleCaptionsButton = document.createElement('button');
    toggleCaptionsButton.innerText = 'Caption';
    toggleCaptionsButton.style.backgroundColor = '#3b3b3b'; // Default background
    toggleCaptionsButton.style.color = 'white'; // Default text color
    toggleCaptionsButton.style.marginRight = '5px'; // Margin to separate buttons
    toggleCaptionsButton.onclick = async () => {
        captionsEnabled = !captionsEnabled; // Toggle the state
        if (captionsEnabled) {
            await toggleCaptions(); // Turn on captions
            toggleCaptionsButton.innerText = 'Hide Captions'; // Change button text
        } else {
            await toggleCaptions(); // Turn off captions
            toggleCaptionsButton.innerText = 'Show Captions'; // Change button text
        }
    };

    const langToggleButtonEnToJa = document.createElement('button');
    langToggleButtonEnToJa.innerText = 'English to Japanese';
    langToggleButtonEnToJa.style.backgroundColor = '#3b3b3b'; // Default background
    langToggleButtonEnToJa.style.color = 'white'; // Default text color
    langToggleButtonEnToJa.style.marginRight = '5px'; // Margin to separate buttons
    langToggleButtonEnToJa.onclick = async () => {
        currentSourceLang = 'en';
        currentTargetLang = 'ja';
        langToggleButtonEnToJa.style.backgroundColor = '#00bfff'; // Highlight color
        langToggleButtonJaToEn.style.backgroundColor = '#3b3b3b'; // Default color

        await changeCaptionLanguageToEnglish(); // Change the caption language to Japanese
    };

    const langToggleButtonJaToEn = document.createElement('button');
    langToggleButtonJaToEn.innerText = 'Japanese to English';
    langToggleButtonJaToEn.style.backgroundColor = '#3b3b3b'; // Default background
    langToggleButtonJaToEn.style.color = 'white'; // Default text color
    langToggleButtonJaToEn.onclick = async () => {
        currentSourceLang = 'ja';
        currentTargetLang = 'en';
        langToggleButtonJaToEn.style.backgroundColor = '#00bfff'; // Highlight color
        langToggleButtonEnToJa.style.backgroundColor = '#3b3b3b'; // Default color

        await changeCaptionLanguageToJapanese(); // Change the caption language to English
    };

    buttonContainer.appendChild(toggleCaptionsButton); // Add toggle button
    buttonContainer.appendChild(langToggleButtonEnToJa);
    buttonContainer.appendChild(langToggleButtonJaToEn);

    const minimizeButton = document.createElement('button');
    minimizeButton.innerHTML = '➖'; // Minimize icon (minus)
    minimizeButton.style.fontSize = '20px';
    minimizeButton.onclick = () => {
        popup.style.display = 'none'; // Hide the popup
    };

    const closeButton = document.createElement('button');
    closeButton.innerHTML = '❌'; // Close icon (cross)
    closeButton.style.fontSize = '20px';
    closeButton.onclick = () => {
        clearInterval(intervalId); // Stop logging captions
        popup.remove(); // Remove the popup
    };

    buttonContainer.appendChild(minimizeButton);
    buttonContainer.appendChild(closeButton);
    popup.appendChild(buttonContainer);

    const captionsContainer = document.createElement('div');
    captionsContainer.style.overflowY = 'scroll';
    captionsContainer.style.height = '220px'; // Adjust height for captions
    popup.appendChild(captionsContainer);

    makeDraggable(popup);
    startLogging();

    document.body.appendChild(popup);
    return popup;
}

// Function to add resize handles to the popup
function addResizeHandles(popup) {
    const handleSize = '10px';

    const createHandle = (cursor) => {
        const handle = document.createElement('div');
        handle.style.position = 'absolute';
        handle.style.width = handleSize;
        handle.style.height = handleSize;
        handle.style.backgroundColor = 'transparent'; // Invisible but functional
        handle.style.cursor = cursor;
        return handle;
    };

    // Create the bottom-right corner handle for resizing
    const bottomRightHandle = createHandle('se-resize');
    bottomRightHandle.style.right = '0';
    bottomRightHandle.style.bottom = '0';
    popup.appendChild(bottomRightHandle);

    // Resize functionality
    const handleResize = (e) => {
        const startX = e.clientX;
        const startY = e.clientY;
        const startWidth = parseInt(document.defaultView.getComputedStyle(popup).width, 10);
        const startHeight = parseInt(document.defaultView.getComputedStyle(popup).height, 10);

        const doDrag = (e) => {
            popup.style.width = `${startWidth + e.clientX - startX}px`;
            popup.style.height = `${startHeight + e.clientY - startY}px`;
        };

        const stopDrag = () => {
            document.removeEventListener('mousemove', doDrag);
            document.removeEventListener('mouseup', stopDrag);
        };

        document.addEventListener('mousemove', doDrag);
        document.addEventListener('mouseup', stopDrag);
    };

    // Attach the resize event to the handle
    bottomRightHandle.addEventListener('mousedown', (e) => {
        e.stopPropagation(); // Prevent triggering dragging while resizing
        e.preventDefault();
        handleResize(e);
    });
}

// Function to make the popup draggable
function makeDraggable(popup) {
    let isResizing = false; // Flag to track if resizing is happening

    popup.onmousedown = function (event) {
        // Ignore dragging if resizing is in progress
        if (isResizing) return;

        let shiftX = event.clientX - popup.getBoundingClientRect().left;
        let shiftY = event.clientY - popup.getBoundingClientRect().top;

        function moveAt(pageX, pageY) {
            popup.style.left = pageX - shiftX + 'px';
            popup.style.top = pageY - shiftY + 'px';
        }

        function onMouseMove(event) {
            moveAt(event.pageX, event.pageY);
        }

        document.addEventListener('mousemove', onMouseMove);

        popup.onmouseup = function () {
            document.removeEventListener('mousemove', onMouseMove);
            popup.onmouseup = null;
        };
    };

    popup.ondragstart = function () {
        return false;
    };

    // Make sure resizing flag is reset properly
    const bottomRightHandle = popup.querySelector('div[style*="se-resize"]');
    bottomRightHandle.addEventListener('mousedown', () => {
        isResizing = true; // Set resizing flag
    });

    document.addEventListener('mouseup', () => {
        isResizing = false; // Reset resizing flag on mouseup
    });
}


// Function to get captions and speakers from the page
function getCaptionsAndSpeakers() {
    const captionsElements = document.querySelectorAll('.iTTPOb.VbkSUe'); // Update selectors as needed
    const speakersElements = document.querySelectorAll('.zs7s8d.jxFHg'); // Update selectors as needed

    const captions = Array.from(captionsElements).map(caption => caption.innerText);
    const speakers = Array.from(speakersElements).map(speaker => speaker.innerText);

    return { captions, speakers };
}


// Function to translate text using the API based on selected languages
async function translateToEnglish(text) {
    // const response = await fetch('https://a0169f5b-1d1a-4553-9855-a7dfc5ffa788-00-uwap8teg2pwm.sisko.replit.dev/translate', {
        const response = await fetch('https://localhost:8000/translate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            q: text,
            source: currentSourceLang,
            target: currentTargetLang,
            format: 'text',
        }),
    });

    const data = await response.json();
    return data.translatedText;
}

// Function to log captions and speakers to the console and display them in the popup
async function logCaptionsAndSpeakers() {
    const { captions, speakers } = getCaptionsAndSpeakers();

    for (let index = 0; index < captions.length; index++) {
        if (index < speakers.length) {
            const speaker = speakers[index];
            const caption = captions[index];

            try {
                const translatedCaption = await translateToEnglish(caption);
                const entry = `${speaker}: ${translatedCaption}`;

                console.log(entry);

                const p = document.createElement('p');
                p.innerText = entry;
                const captionsContainer = document.querySelector(`#${popupId} div:last-child`);
                captionsContainer.appendChild(p);
                captionsContainer.scrollTop = captionsContainer.scrollHeight;
            } catch (error) {
                console.error('Translation error:', error);
            }
        }
    }
}

// Function to start logging captions
function startLogging() {
    clearInterval(intervalId);
    intervalId = setInterval(logCaptionsAndSpeakers, 10000);
}

// Function to toggle captions on by simulating 'c' keypress
async function toggleCaptions() {
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'c', bubbles: true }));
    await new Promise(resolve => setTimeout(resolve, 1000)); // Wait a bit to allow captions to toggle
}

async function changeCaptionLanguageToJapanese() {
    const captionSettingsXPath = '/html/body/div[1]/c-wiz/div/div/div[28]/div[3]/div[3]/div[2]/div/span/div[1]/button';
    const captionSettingsButton = document.evaluate(captionSettingsXPath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;

    if (captionSettingsButton) {
        captionSettingsButton.click();
        await new Promise(resolve => setTimeout(resolve, 3000)); // Wait for settings to open
        console.log("Clicked Caption Settings Button");

        // Find the caption option dropdown (this should work for any visible language)
        const captionDropdownOption = Array.from(document.querySelectorAll('span.VfPpkd-uusGie-fmcmS'))
            .find(span => span.textContent.trim().toLowerCase().includes("english") || span.textContent.trim() !== "");

        if (captionDropdownOption) {
            captionDropdownOption.click(); // Click the caption option to open the dropdown
            console.log("Clicked caption language option dropdown");

            // Wait for dropdown options to be available
            await new Promise(resolve => setTimeout(resolve, 1000)); // Wait a moment for the dropdown to load

            // Now find and click the Japanese language option
            const japaneseLanguageOption = Array.from(document.querySelectorAll('li[role="option"]'))
                .find(li => li.getAttribute('aria-label') === "Japanese");

            if (japaneseLanguageOption) {
                japaneseLanguageOption.click(); // Click the Japanese option
                console.log("Clicked Japanese language option");

                // Wait for the change in language option to Japanese
                await new Promise(resolve => setTimeout(resolve, 1000)); // Wait for language switch
            } else {
                console.log("Japanese caption option not found");
            }

            // Close the settings dialog using the close button element
            const closeButton = document.querySelector('button[aria-label="Close dialog"]');
            if (closeButton) {
                closeButton.click(); // Click the close button
                console.log("Clicked close button to close settings");
            } else {
                console.log("Close button not found");
            }
        } else {
            console.log("Caption dropdown option not found or is in a different language");

            // Try to close the settings window even if the dropdown was not found
            const closeButton = document.querySelector('button[aria-label="Close dialog"]');
            if (closeButton) {
                closeButton.click(); // Click the close button
                console.log("Closed settings dialog despite dropdown failure");
            }
        }
    } else {
        console.log("Caption Settings Button not found");
    }
}




// Function to simulate key presses for changing caption setting source language to English
async function changeCaptionLanguageToEnglish() {
    const captionSettingsXPath = '/html/body/div[1]/c-wiz/div/div/div[28]/div[3]/div[3]/div[2]/div/span/div[1]/button';
    const captionSettingsButton = document.evaluate(captionSettingsXPath, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;

    if (captionSettingsButton) {
        captionSettingsButton.click();
        await new Promise(resolve => setTimeout(resolve, 3000)); // Wait for settings to open
        console.log("Clicked Caption Settings Button");

        // // function to check if the langague is already "English" ()
        // const invalidDropdownOption = Array.from(document.querySelectorAll('span.VfPpkd-uusGie-fmcmS')).find(span => span.textContent.trim() === "English");

         // Find the caption option dropdown (this should work for any visible language)
         const captionDropdownOption = Array.from(document.querySelectorAll('span.VfPpkd-uusGie-fmcmS'))
         .find(span => span.textContent.trim().toLowerCase().includes("japanese") || span.textContent.trim() !== "");

        if (captionDropdownOption) {
            captionDropdownOption.click(); // Click the caption option to open the dropdown
            console.log("Clicked caption language option dropdown");

            // Wait for dropdown options to be available
            await new Promise(resolve => setTimeout(resolve, 1000)); // Wait a moment for the dropdown to load

            // Now find and click the English language option
            const englishLanguageOption = Array.from(document.querySelectorAll('li[role="option"]')).find(li => li.getAttribute('aria-label') === "English");

            if (englishLanguageOption) {
                englishLanguageOption.click(); // Click the English option
                console.log("Clicked English language option");

                // Wait for change in lanaguage option to japanese
                await new Promise(resolve => setTimeout(resolve, 1000)); // Wait a moment for the langauage switch

                // Close the settings dialog using the close button element
                const closeButton = document.querySelector('button[aria-label="Close dialog"]');

                if (closeButton) {
                    closeButton.click(); // Click the close button
                    console.log("Clicked close button to close settings");
                } else {
                    console.log("Close button not found");
                }
            } else {
                console.log("English caption option not found");
            }
        } else {
            console.log("Caption dropdown option not found");
        }
    } else {
        console.log("Caption Settings Button not found");
    }
}


// Listen for messages from the popup (popup.js)
chrome.runtime.onMessage.addListener((message) => {
    if (message.action === 'openPopup') {
        createPopup();
    }
});
