// Capturar ubicación del dispositivo
function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

// Mostrar la posición en el label
function showPosition(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;

    // Usar un servicio de geocodificación (ejemplo con OpenStreetMap)
    fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`)
        .then(response => response.json())
        .then(data => {
            const address = data.display_name || "Ubicación desconocida";
            document.getElementById("location-label").innerText = address;
        })
        .catch(error => console.error("Error al obtener la dirección:", error));
}

// Manejar errores de geolocalización
function showError(error) {
    switch (error.code) {
        case error.PERMISSION_DENIED:
            alert("El usuario denegó la solicitud de geolocalización.");
            break;
        case error.POSITION_UNAVAILABLE:
            alert("La información de ubicación no está disponible.");
            break;
        case error.TIMEOUT:
            alert("La solicitud para obtener la ubicación ha caducado.");
            break;
        case error.UNKNOWN_ERROR:
            alert("Se produjo un error desconocido.");
            break;
    }
}

// Llamar a la función al cargar la página
window.onload = getLocation;