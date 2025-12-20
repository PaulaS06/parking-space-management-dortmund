let lastTimeout = null;

document.getElementById("search").addEventListener("input", function () {
  document.getElementById("submitBtn").disabled = true;
});

document.getElementById("search").addEventListener("input", function () {
  const query = this.value;

  clearTimeout(lastTimeout);

  if (query.length < 3) {
    document.getElementById("suggestions").innerHTML = "";
    return;
  }

  // Debounce 300ms
  lastTimeout = setTimeout(() => {
    fetch(`/autocomplete?q=${encodeURIComponent(query)}`)
      .then(res => res.json())
      .then(data => {
        const list = document.getElementById("suggestions");
        list.innerHTML = "";

        data.forEach(item => {
          const li = document.createElement("li");
          li.textContent = item.properties.formatted;

          li.onclick = () => {
            document.getElementById("search").value = item.properties.formatted;
            list.innerHTML = "";

            const lat = item.properties.lat;
            const lon = item.properties.lon;
            console.log("Koordinaten:", lat, lon);
            fetch("/set_location", {
                method: "POST",
                headers: {
                  "Content-Type": "application/json"
                },
                body: JSON.stringify({
                  lat: lat,
                  lon: lon
                })
              })
              .then(res => {
                if (!res.ok) {
                  throw new Error("Backend-Fehler");
                }
                return res.json();
              })
              .then(data => {
                if (data.status === "ok") {
                  // ✅ Button aktivieren
                  document.getElementById("submitBtn").disabled = false;
                }
              })
              .catch(err => {
                console.error(err);
                document.getElementById("submitBtn").disabled = true;
              });
          };

          list.appendChild(li);
        });
      });
  }, 150);
});
