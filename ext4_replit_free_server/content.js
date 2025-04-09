// defining the func to create a floating, draggable popup for displaying captions and speakers
function createPopup() {
    const popup = document.createElement('div');
    popup.id = 'captionsPopup';
    popup.style.position = 'fixed';
    popup.style.bottom = '20px';
    popup.style.right = '20px';
    popup.style.width = '300px';
    popup.style.height = '200px';
    popup.style.overflowY = 'scroll';
    popup.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
    popup.style.color = 'white';
    popup.style.padding = '10px';
    popup.style.zIndex = '9999';
    popup.style.border = '1px solid white';
    popup.style.borderRadius = '8px';
    popup.style.cursor = 'move';
  
    const startButton = document.createElement('button');
    startButton.innerText = 'Start';
    startButton.onclick = startLogging;
  
    const stopButton = document.createElement('button');
    stopButton.innerText = 'Stop';
    stopButton.onclick = stopLogging;
  
    const closeButton = document.createElement('button');
    closeButton.innerText = 'Close';
    closeButton.onclick = () => {
      popup.style.display = 'none';
    };
  
    popup.appendChild(startButton);
    popup.appendChild(stopButton);
    popup.appendChild(closeButton);
    
    document.body.appendChild(popup);
  
    // Making the popup draggable
    popup.onmousedown = function (event) {
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
  
    return popup;
  }
  
  const popup = createPopup();
  let intervalId;
  
  // Function to get captions and speaker names from the page
  function getCaptionsAndSpeakers() {
    const captionsElements = document.querySelectorAll('.iTTPOb.VbkSUe'); // we need to keep the exact class names as they are in the page if the meet updates this.... I kept it based on 2024
    const speakersElements = document.querySelectorAll('.zs7s8d.jxFHg'); 
  
    const captions = Array.from(captionsElements).map(caption => caption.innerText);
    const speakers = Array.from(speakersElements).map(speaker => speaker.innerText);
  
    return { captions, speakers };
  }
  
  // Function to translate text to English using a free translation API
  async function translateToEnglish(text) {
    // const response = await fetch('http://localhost:8000/translate', {
      const response = await fetch('https://1de41bcb-3269-4c01-9144-5262324b7103-00-4frtlbqftclw.pike.replit.dev/translate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        q: text,
        source: 'auto',
        target: 'en',
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
          // Translate the caption to English
          const translatedCaption = await translateToEnglish(caption);
          const entry = `${speaker}: ${translatedCaption}`;
  
          // Log to console
          console.log(entry);
  
          // Display in popup
          const p = document.createElement('p');
          p.innerText = entry;
          popup.appendChild(p);
  
          // Keep the popup scrolled to the bottom
          popup.scrollTop = popup.scrollHeight;
        } catch (error) {
          console.error('Translation error:', error);
        }
      }
    }
  }
  
  // Function to start logging captions
  function startLogging() {
    if (!intervalId) {
      intervalId = setInterval(logCaptionsAndSpeakers, 10000);
    }
  }
  
  // Function to stop logging captions
  function stopLogging() {
    clearInterval(intervalId);
    intervalId = null;
  }
  
  // initialize the popup
  popup;
  