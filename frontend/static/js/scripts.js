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
        document.getElementById("startTime").value = pad(start.getHours()) + ':' + pad(start.getMinutes());
        document.getElementById("endTime").value = pad(end.getHours()) + ':' + pad(end.getMinutes());
    };

    // Browser Speech API
    const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        alert("SpeechRecognition wird von diesem Browser nicht unterstützt.");
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
    };

    function startSpeech() {
        recognition.start();
    }