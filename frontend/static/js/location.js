document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("location_input");
    const dropdown = document.getElementById("locationDropdown");
    const getLocationOption = document.getElementById("getLocationOption");

    // Mostrar dropdown al hacer focus
    input.addEventListener("focus", () => {
        dropdown.classList.remove("d-none");
    });

    // Ocultar si se hace click fuera
    document.addEventListener("click", (e) => {
        if (!e.target.closest(".location")) {
            dropdown.classList.add("d-none");
        }
    });

    // Click en "Get current location"
    getLocationOption.addEventListener("click", () => {
        dropdown.classList.add("d-none");
        getCurrentLocation(input);
    });
});


// ---- GEOLOCATION ----
function getCurrentLocation(input) {
    if (!navigator.geolocation) {
        alert("Geolocation not supported");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const { latitude, longitude } = position.coords;

            fetch(`https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`)
                .then(res => res.json())
                .then(data => {
                    input.value = data.display_name || "Unknown location";
                });
        },
        () => {
            alert("Unable to retrieve location");
        }
    );
}

// Handle geolocation errors
function showError(error) {
    switch (error.code) {
        case error.PERMISSION_DENIED:
            alert("User denied the request for Geolocation.");
            break;
        case error.POSITION_UNAVAILABLE:
            alert("Location information is unavailable.");
            break;
        case error.TIMEOUT:
            alert("The request to get user location timed out.");
            break;
        case error.UNKNOWN_ERROR:
            alert("An unknown error occurred.");
            break;
    }
}