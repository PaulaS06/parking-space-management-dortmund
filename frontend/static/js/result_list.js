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
        <table class="table table-borderless">
            <tbody>
                <tr>
                    <td class="table-cell-left">
                        <h5 class="card-title">
                            ${item.name}
                        </h5>
                        <p class="card-text">
                            ${item.fullAddress}
                        </p>
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
                            ${item.capacity} Available
                        </p>
                    </td>
                    <td class="table-cell-middle">
                        <p class="card-text">
                            ${item.priceTotal}€
                        </p>
                    </td>
                    <td class="table-cell-right">
                        <p class="card-text">${item.walkingTimeMinutes} minutes walk</p>
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
    // AJAX-Call
    fetch(`/api/search`)
        .then(response => response.json())
        .then(data => updateParkingList(data));
}

