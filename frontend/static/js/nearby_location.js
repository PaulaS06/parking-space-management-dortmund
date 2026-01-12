document.addEventListener("DOMContentLoaded", () => {
    const locationSpan = document.getElementById("currentLocation");
    getCurrentLocation(locationSpan);
});

function getCurrentLocation(element) {
    if (!navigator.geolocation) {
        element.textContent = "Geolocation not supported";
        return;
    }

    navigator.geolocation.getCurrentPosition(
        async (position) => {
            const { latitude, longitude } = position.coords;

            let address = "Unknown location";
            try {
                const res = await fetch(
                    `https://nominatim.openstreetmap.org/reverse?lat=${latitude}&lon=${longitude}&format=json`
                );
                const data = await res.json();
                address = data.display_name || address;
            } catch (error) {
                console.error("Error fetching address:", error);
            }

            element.textContent = address;

            element.dataset.lat = latitude;
            element.dataset.lon = longitude;
            element.dataset.address = address;

            searchParking({
                latitude,
                longitude,
                address
            });
        },
        (error) => {
            element.textContent = "Unable to get location";
            showError(error);
        }
    );
}

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