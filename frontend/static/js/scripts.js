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