let lastTimeout = null;

// Initialize global variables for selected coordinates
window.selectedLat = null;
window.selectedLon = null;

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

            // Store selected coordinates globally
            window.selectedLat = item.properties.lat;
            window.selectedLon = item.properties.lon;

            console.log("Selected:", item.properties.formatted);
            console.log("Coordinates:", window.selectedLat, window.selectedLon);
          };

          list.appendChild(li);
        });
      });
  }, 150);
});
