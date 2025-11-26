let lastTimeout = null;

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

            console.log("Ausgewählt:", item.properties.formatted);
            console.log("Koordinaten:", item.properties.lat, item.properties.lon);
          };

          list.appendChild(li);
        });
      });
  }, 150);
});
