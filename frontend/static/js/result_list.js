function openModal() {
    document.getElementById("filterModal").style.display = "block";
}

function closeModal() {
    document.getElementById("filterModal").style.display = "none";
}

function applyFilter() {
    let checkbox = document.getElementById("evChargingCheckbox");
    let ev = checkbox.checked ? "true" : "false";

    // AJAX-Call
    fetch(`/api/filter?ev_charging=${ev}`)
        .then(response => response.json())
        .then(data => updateParkingList(data));

    closeModal();
}

function updateParkingList(list) {
    let container = document.getElementById("parkingList");
    container.innerHTML = "";

    list.forEach(item => {
        const card = document.createElement("div");
        card.className = "card mb-1";

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


function searchParking() {
    // Get search parameters
    const address = document.getElementById("search").value;
    const startTime = document.getElementById("startTime").value;
    const endTime = document.getElementById("endTime").value;
    
    // Get coordinates if set by autocomplete
    const lat = window.selectedLat;
    const lon = window.selectedLon;
    
    if (!address && !lat) {
        alert("Please enter a location to search");
        return;
    }
    
    if (!startTime || !endTime) {
        alert("Please select start and end times");
        return;
    }
    
    // Build query parameters
    let params = new URLSearchParams();
    if (lat && lon) {
        params.append('lat', lat);
        params.append('lon', lon);
    } else if (address) {
        params.append('address', address);
    }
    params.append('start_time', startTime);
    params.append('end_time', endTime);
    
    // AJAX-Call
    fetch(`/api/search?${params.toString()}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("Error: " + data.error);
            } else {
                updateParkingList(data);
            }
        })
        .catch(error => {
            console.error("Search error:", error);
            alert("Failed to search parking. Please try again.");
        });
}

