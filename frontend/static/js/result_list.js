function openModal() {
    document.getElementById("filterModal").style.display = "block";
}

function closeModal() {
    document.getElementById("filterModal").style.display = "none";
}

function applyFilter() {
    let checkbox = document.getElementById("evChargingCheckbox");
        // Use API route that both sets the filter and returns updated results
        const ev = checkbox.checked ? "true" : "false";
        fetch(`/api/filter?ev_charging=${ev}`)
                .then(response => response.json())
                .then(data => updateParkingList(data))
                .catch(() => {
                        // Keep UI responsive even if filter refresh fails
                        console.warn("Failed to refresh filtered results");
                });

    closeModal();
}

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
            window.location.href = "/details";
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
                        <p class="card-text">${item.walkingTimeMinutes} min walk</p>
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
        const startTime = document.getElementById("startTime").value; // "HH:MM"
        const endTime = document.getElementById("endTime").value;

        console.log(startTime, endTime);
        const response = await fetch("/set_time", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                start_time: startTime,
                end_time: endTime
            })
        });

        if (!response.ok) {
            console.error("Fehler beim Setzen der Zeit");
            return;
        }
        const apiResponse = await fetch("/api/search");

        let payload = null;
        try {
            payload = await apiResponse.json();
        } catch {
            showError("Ungültige Serverantwort.");
            return;
        }

        if (!apiResponse.ok) {
            handleApiError(apiResponse.status, payload);
            return;
        }
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
            updateParkingList([]); // Liste leeren
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
