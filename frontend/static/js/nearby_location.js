// document.addEventListener("DOMContentLoaded", () => {
//     const input = document.getElementById("location_input");
//     // const dropdown = document.getElementById("locationDropdown");
//     const getLocationOption = document.getElementById("getLocationOption");

//     // Mostrar dropdown al hacer focus
//     input.addEventListener("focus", () => {
//         dropdown.classList.remove("d-none");
//     });

//     // Ocultar si se hace click fuera
//     document.addEventListener("click", (e) => {
//         if (!e.target.closest(".location")) {
//             dropdown.classList.add("d-none");
//         }
//     });

//     // Click en "Get current location"
//     getLocationOption.addEventListener("click", () => {
//         dropdown.classList.add("d-none");
//         getCurrentLocation(input);
//     });
// });


document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("location_input");

    getCurrentLocation(input);
});

function getCurrentLocation(input) {
    // const submitBtn = document.getElementById("submitBtn");
    
    if (!navigator.geolocation) {
        alert("Geolocation not supported");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        async (position) => {
            const { latitude, longitude } = position.coords;
    
            let address = "Unknown location";
            try {
                const res = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`);
                const data = await res.json();
                address = data.display_name || address;
                input.value = address;
            } catch (err) {
                console.error("Reverse geocoding failed", err);
                input.value = "Unknown location";
            }
    
            // submitBtn.dataset.lat = latitude;
            // submitBtn.dataset.lon = longitude;
            // submitBtn.dataset.address = address;

            location_input.dataset.lat = latitude;
            location_input.dataset.lon = longitude;
            location_input.dataset.address = address;
        }
    );   

    // submitBtn.addEventListener("click", () => {
    //     if (!submitBtn.disabled) {
    //         searchParking();
    //     }
    // });    
}


// Manejar geolocation errors
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