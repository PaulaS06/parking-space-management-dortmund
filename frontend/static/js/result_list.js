function openModal() {
    document.getElementById("filterModal").style.display = "block";
}

function closeModal() {
    document.getElementById("filterModal").style.display = "none";
}

function applyFilter() {
    let checkbox = document.getElementById("evChargingCheckbox");
    let ev = checkbox.checked ? "True" : "False";

    fetch("/set_filter", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          ev_charging: ev
        })
    });

    closeModal();
}

function updateParkingList(list) {
    let container = document.getElementById("parkingList");
    container.innerHTML = "";

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


function searchParking() {
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
    console.log("posted time");
    // AJAX-Call
    const apiResponse = await fetch("/api/search");
    const data = await apiResponse.json();

    updateParkingList(data);
    console.log("updated list");
}

