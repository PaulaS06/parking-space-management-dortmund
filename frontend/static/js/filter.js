document.getElementById('filterModal').addEventListener('show.bs.modal', function () {
    document.getElementById('evChargingCheckbox').checked = evFilterState;
});

function openModal() {
    document.getElementById("filterModal").style.display = "block";
}

function closeModal() {
    document.getElementById("filterModal").style.display = "none";
}

function applyFilter() {
    // Set filter then update results
    let checkbox = document.getElementById("evChargingCheckbox");
    evFilterState = checkbox.checked;

    fetch("/set_filter", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            ev_charging: window.evFilterState
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "ok") {
            searchParking();
        }
    });

    closeModal();
}