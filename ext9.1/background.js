chrome.action.onClicked.addListener((tab) => {
    chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => {
            const popup = document.getElementById('captionsPopup');
            if (popup) {
                popup.style.display = (popup.style.display === 'none' || popup.style.display === '') ? 'block' : 'none';
            } else {
                createPopup(); // Call to create the popup if it doesn't exist
            }
        },
        args: [] // No arguments needed
    });
});
