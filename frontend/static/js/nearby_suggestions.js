const submitBtn = document.getElementById("submitBtn");
const locationInput = document.getElementById("location_input");

submitBtn.disabled = true;

document.getElementById("getLocationOption").addEventListener("click", () => {
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
                locationInput.value = address;
            } catch (err) {
                console.error("Reverse geocoding failed", err);
            }

            submitBtn.dataset.lat = latitude;
            submitBtn.dataset.lon = longitude;
            submitBtn.dataset.address = address;

            submitBtn.disabled = false;
        },
        () => {
            alert("Unable to retrieve location");
        }
    );
});

submitBtn.addEventListener("click", async () => {
    if (submitBtn.disabled) return;

    const latitude = parseFloat(submitBtn.dataset.lat);
    const longitude = parseFloat(submitBtn.dataset.lon);
    const address = submitBtn.dataset.address;

    try {
        const response = await fetch("/api/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                address,
                latitude,
                longitude
            })
        });

        const payload = await response.json();
        updateParkingList(payload);

    } catch (err) {
        console.error("Error fetching parking data:", err);
    }
});
