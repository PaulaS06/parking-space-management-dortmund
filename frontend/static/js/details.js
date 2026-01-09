const parking = JSON.parse(sessionStorage.getItem("selectedParking"));

if (!parking) {
    alert("No parking house selected");
    history.back();
}

document.getElementById("parkingName").textContent = parking.name;
document.getElementById("parkingAddress").textContent = parking.fullAddress;
document.getElementById("priceTotal").textContent = parking.priceTotal + " €";
document.getElementById("distance").textContent =
    `${parking.walkingDistanceInKm} km • ${parking.walkingTimeMinutes} min`;

document.getElementById("evCharging").textContent =
    parking.evCharging ? "Available" : "Not available";

const dot = document.getElementById("capacityDot");
dot.classList.add(parking.capacity > 5 ? "dot-green" : "dot-red");

document.getElementById("capacityText").textContent =
    `${parking.capacity} free spots`;

/* Google Maps Route */
const button = document.getElementById("mapsLink");

button.addEventListener("click", () => {
    const isAppleDevice = /iPad|iPhone|iPod|Macintosh/.test(navigator.userAgent);

    const mapsUrl = isAppleDevice
        ? `https://maps.apple.com/?daddr=${parking.latitude},${parking.longitude}`
        : `https://www.google.com/maps/dir/?api=1&destination=${parking.latitude},${parking.longitude}`;

    window.open(mapsUrl, "_blank");
});
