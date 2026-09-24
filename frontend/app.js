const form = document.querySelector("#predict-form");
const results = document.querySelector("#results");
const statusEl = document.querySelector("#status");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  statusEl.textContent = "Calculating...";

  const payload = {};
  for (const [key, value] of new FormData(form).entries()) {
    if (value === "") continue;
    payload[key] = ["area_ha", "crop_year", "rainfall_mm", "latitude", "longitude"].includes(key)
      ? Number(value)
      : value;
  }

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Prediction failed");
    }

    document.querySelector("#yield-value").textContent = data.predicted_yield_t_ha;
    document.querySelector("#production-value").textContent = data.estimated_production_tonnes;
    document.querySelector("#history-value").textContent =
      data.historical_average_yield_t_ha ?? "Not available";

    const weather = data.weather || {};
    const weatherParts = [];
    if (weather.temperature_c != null) weatherParts.push(`${weather.temperature_c}°C`);
    if (weather.humidity != null) weatherParts.push(`${weather.humidity}% humidity`);
    if (weather.precip_mm != null) weatherParts.push(`${weather.precip_mm} mm rain`);
    if (!weatherParts.length && weather.rainfall_mm != null) {
      weatherParts.push(`${weather.rainfall_mm} mm seasonal rain`);
    }
    document.querySelector("#weather-value").textContent = weatherParts.slice(0, 2).join(" · ") || "Records only";
    document.querySelector("#weather-note").textContent =
      weather.condition || "OpenWeather key not set, so rainfall from crop records is shown.";

    document.querySelector("#outlook-label").textContent = data.outlook.label;
    document.querySelector("#outlook-detail").textContent = data.outlook.detail;

    results.classList.remove("hidden");
    statusEl.textContent = "Done. These are the 5 results for your field.";
  } catch (error) {
    statusEl.textContent = String(error);
  }
});

const chartColors = ["#1f6f43", "#3d8b5f", "#c4a35a", "#4f7cac", "#8c5e58"];

function makeChart(id, type, title, labels, values, color) {
  const canvas = document.getElementById(id);
  if (!canvas || typeof Chart === "undefined") return;
  const isDoughnut = type === "doughnut";
  new Chart(canvas, {
    type,
    data: {
      labels,
      datasets: [
        {
          label: title,
          data: values,
          backgroundColor: isDoughnut || type === "bar" ? color || chartColors : "rgba(31, 111, 67, 0.18)",
          borderColor: "#1f6f43",
          borderWidth: type === "line" ? 2 : 0,
          fill: type === "line",
          tension: 0.25,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: isDoughnut },
      },
      scales: isDoughnut
        ? {}
        : {
            y: {
              beginAtZero: true,
              ticks: { color: "#5c6b60" },
              grid: { color: "#e6eee3" },
            },
            x: {
              ticks: { color: "#5c6b60" },
              grid: { display: false },
            },
          },
    },
  });
}

async function loadAnalysisCharts() {
  try {
    const response = await fetch("/analysis");
    const data = await response.json();
    if (!response.ok) return;
    makeChart(
      "chart-crop",
      "bar",
      "Yield t/ha",
      data.yield_by_crop.labels,
      data.yield_by_crop.values,
    );
    makeChart(
      "chart-state",
      "bar",
      "Yield t/ha",
      data.yield_by_state.labels,
      data.yield_by_state.values,
      "#3d8b5f",
    );
    makeChart(
      "chart-year",
      "line",
      "Yield t/ha",
      data.yield_by_year.labels,
      data.yield_by_year.values,
    );
    makeChart(
      "chart-season",
      "doughnut",
      "Rainfall mm",
      data.rainfall_by_season.labels,
      data.rainfall_by_season.values,
    );
  } catch (error) {
    console.error(error);
  }
}

loadAnalysisCharts();
