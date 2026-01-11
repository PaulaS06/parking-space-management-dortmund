const MOCK_MODE = false; // Ready to use the backend data

const MOCK_PARKINGS = [
    {
        id: 1,
        name: "Parking Centro",
        fullAddress: "Calle 123, Ciudad",
        latitude: 4.710989,
        longitude: -74.072090,
        capacity: 12,
        priceTotal: 5,
        pricePerHour: 1.5,
        drivingDistanceKm: 0.8,
        drivingTimeMinutes: 3,
        evCharging: true
    },
    {
        id: 2,
        name: "Parking Norte",
        fullAddress: "Avenida 45, Ciudad",
        latitude: 4.715000,
        longitude: -74.070000,
        capacity: 3,
        priceTotal: 7,
        pricePerHour: 2,
        drivingDistanceKm: 1.2,
        drivingTimeMinutes: 5,
        evCharging: false
    }
];



function updateParkingList(list) {
    let container = document.getElementById("parkingList");
    container.innerHTML = "";

    if (!list || list.length === 0) {
        container.innerHTML = `
            <div class="text-muted text-center mt-3">
                Keine Parkplätze verfügbar.
            </div>`;
        return;
    }

    list.forEach(item => {
        const card = document.createElement("div");
        card.className = "card mb-1";
        card.addEventListener("click", () => {
            sessionStorage.setItem("selectedParking", JSON.stringify(item));
            window.location.href = "/nearby_details";
        });

        card.innerHTML = `
        <div class="card-body">
        <table class="table table-borderless parking-table">
            <tbody>
                <tr>
                    <td class="table-cell-left">
                        <h5 class="card-title">
                            ${item.name}
                        </h5>
                    </td>
                    <td></td>
                    <td class="table-cell-right">
                        <img class="parking-img" src="${item.capacity > 5 ? 'static/images/green-parking-lot.png' : 'static/images/red-parking-lot.png'}"
                        alt="status">
                    </td>
                </tr>
                <tr>
                    <td class="table-cell-left">
                        <p class="card-text">
                            <span class="dot ${item.capacity > 5 ? 'dot-green' : 'dot-red'}"></span>
                            ${item.capacity} available
                        </p>
                    </td>
                    <td class="table-cell-middle">
                        <p class="card-text">
                            ${item.priceTotal}€
                        </p>
                    </td>
                    <td class="table-cell-right">
                        <p class="card-text">${item.drivingTimeMinutes} min by car</p>
                    </td>
                </tr>
            </tbody>
        </table>
        </div>
        `;

        container.appendChild(card);
    });
}


async function searchParking({ latitude, longitude, address }) {
    clearError();

    try {
        let payload;

        if (MOCK_MODE) {
            payload = MOCK_PARKINGS;
            await new Promise(resolve => setTimeout(resolve, 500));
        } else {
            const response = await fetch("/api/search", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ latitude, longitude })
            });

            if (!response.ok) {
                handleApiError(response.status);
                return;
            }

            try {
                payload = await response.json();
            } catch {
                showErrors("Invalid server response");
                return;
            }
        }

        updateParkingList(payload);

    } catch (err) {
        console.error("Network error:", err);
        showErrors("Backend not available. Please try again later.");
        updateParkingList([]);
    }
}


function showErrors(message) {
    const box = document.getElementById("errorBox");
    box.textContent = message;
    box.classList.remove("d-none");
}

function clearError() {
    const box = document.getElementById("errorBox");
    box.textContent = "";
    box.classList.add("d-none");
}

function handleApiError(status) {
    switch (status) {
        case 400:
            showErrors("Server error. Please try again later.");
            break;

        case 401:
            showErrors("Server error. Please try again later.");
            break;

        case 404:
            showErrors("No free parking houses found. Please try again later.");
            updateParkingList([]); 
            break;

        case 502:
            showErrors("Server not reachable. Please try again later.");
            break;

        case 500:
            showErrors("Server error. Please try again later.");
            break;

        default:
            showErrors("Unknown Error. Please try again later.");
    }
}
