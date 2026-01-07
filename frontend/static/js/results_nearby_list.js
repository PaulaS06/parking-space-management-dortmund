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

async function searchParking() {
    clearError();
    showLoading();
    try{
        const submitBtn = document.getElementById("submitBtn");
        const latitude = parseFloat(submitBtn.dataset.lat);
        const longitude = parseFloat(submitBtn.dataset.lon);
        const address = submitBtn.dataset.address;
        
        // Mandar datos al backend
        const response = await fetch("/api/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                address,
                latitude,
                longitude,
            })
        });

        if (!response.ok) {
            showError("Error fetching parking data.");
            return;
        }

        const payload = await response.json();

        updateParkingList(payload);

    } finally {
        hideLoading();
    }
}

function showError(message) {
    const box = document.getElementById("errorBox");
    box.textContent = message;
    box.classList.remove("d-none");
}

function clearError() {
    const box = document.getElementById("errorBox");
    box.textContent = "";
    box.classList.add("d-none");
}

function handleApiError(status, payload) {
    switch (status) {
        case 400:
            showError("Server error. Please try again later.");
            break;

        case 401:
            showError("Server error. Please try again later.");
            break;

        case 404:
            showError("No free parking houses found. Please try again later.");
            updateParkingList([]); 
            break;

        case 502:
            showError("Server not reachable. Please try again later.");
            break;

        case 500:
            showError("Server error. Please try again later.");
            break;

        default:
            showError("Unknown Error. Please try again later.");
    }
}

function showLoading() {
    document.getElementById("loadingOverlay").classList.remove("d-none");
}

function hideLoading() {
    document.getElementById("loadingOverlay").classList.add("d-none");
}
