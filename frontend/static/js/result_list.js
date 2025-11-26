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
    let ul = document.getElementById("parkingList");
    ul.innerHTML = "";

    list.forEach(item => {
        let li = document.createElement("li");
        li.textContent = `${item.name} (${item.distance}m)`;
        ul.appendChild(li);
    });
}

function searchParking() {
    // AJAX-Call
    fetch(`/api/search`)
        .then(response => response.json())
        .then(data => updateParkingList(data));
}

