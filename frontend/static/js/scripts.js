    function roundToNextQuarter(date) {
        const minutes = date.getMinutes();
        const nextQuarter = Math.ceil(minutes / 15) * 15;
        date.setMinutes(nextQuarter);
        date.setSeconds(0);
        return date;
    }

    function pad(num) {
        return num.toString().padStart(2, '0');
    }

    window.onload = function() {
        const now = new Date();
        // Startzeit = nächster 15-Minuten-Schritt
        const start = roundToNextQuarter(new Date(now));
        // Endzeit = Startzeit + 2 Stunden
        const end = new Date(start.getTime() + 2 * 60 * 60 * 1000);
        // In HH:MM für <input type="time">
        const startTimeInput = document.getElementById("startTime");
        const endTimeInput = document.getElementById("endTime");
        if(!startTimeInput || !endTimeInput){
            return;
        }
        startTimeInput.value = pad(start.getHours()) + ':' + pad(start.getMinutes());
        endTimeInput.value = pad(end.getHours()) + ':' + pad(end.getMinutes());

        fetch("/get_address")
        .then(r => r.json())
        .then(data => {
          if (data.address) {
              document.getElementById("search").value = data.address;
          }
          if (data.lat && data.lon && data.address) {
              document.getElementById("submitBtn").disabled = false;
          } else{
              document.getElementById("submitBtn").disabled = true;
          }
        });
    };

    // Browser Speech API
    const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    const voiceBtn = document.getElementById("voiceBtn");

    if (!SpeechRecognition) {
      console.warn("Speech recognition is not supported in this browser");
      disableVoiceButton("Speech recognition is not supported in this browser");
    } else {
      const recognition = new SpeechRecognition();
      recognition.lang = "de-DE";
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "de-DE";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onresult = function (event) {
        const text = event.results[0][0].transcript;
        const input = document.getElementById("search");

        input.value = text;
        input.dispatchEvent(new Event("input", { bubbles: true }));
    };

    recognition.onerror = function (event) {
        console.error("Fehler:", event.error);
        voiceBtn.disabled = true;
        disableVoiceButton("Speech recognition is not supported in this browser");
    };

    function startSpeech() {
        recognition.start();
    }

    function disableVoiceButton(reason) {
        const voiceBtn = document.getElementById("voiceBtn");

        voiceBtn.disabled = true;
        voiceBtn.classList.add("voice-error");
        voiceBtn.title = reason;
    }