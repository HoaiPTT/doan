"use strict";

// ========== BIỂU ĐỒ DOANH THU (LẤY DỮ LIỆU TỪ API) ==========
var chartCanvas = document.getElementById("myChart");

if (chartCanvas) {
  fetch("/api/subscription_report/")
    .then(response => response.json())
    .then(data => {
      const ctx = chartCanvas.getContext("2d");
      new Chart(ctx, {
        type: "line",
        data: {
          labels: data.labels,
          datasets: [
            {
              label: "Doanh thu (VNĐ)",
              data: data.revenues,
              borderWidth: 4,
              borderColor: "#6777ef",
              backgroundColor: "rgba(103,119,239,0.15)",
              pointBackgroundColor: "#fff",
              pointBorderColor: "#6777ef",
              pointRadius: 4,
              fill: true,
              tension: 0.3
            },
            {
              label: "Lượt đăng ký",
              data: data.counts,
              borderWidth: 4,
              borderColor: "#fc544b",
              backgroundColor: "rgba(252,84,75,0.15)",
              pointBackgroundColor: "#fff",
              pointBorderColor: "#fc544b",
              pointRadius: 4,
              fill: true,
              tension: 0.3
            }
          ]
        },
        options: {
          plugins: {
            legend: { display: true },
          },
          scales: {
            y: {
              beginAtZero: true,
              title: { display: true, text: "Giá trị" },
              grid: { color: "#f2f2f2" }
            },
            x: {
              title: { display: true, text: "Tháng" },
              grid: { color: "#fbfbfb" }
            }
          }
        }
      });
    })
    .catch(error => {
      console.error("❌ Lỗi khi tải dữ liệu biểu đồ:", error);
    });
}

// ========== BẢN ĐỒ ==========
$('#visitorMap').vectorMap({
  map: 'world_en',
  backgroundColor: '#ffffff',
  borderColor: '#f2f2f2',
  borderOpacity: .8,
  borderWidth: 1,
  hoverColor: '#000',
  hoverOpacity: .8,
  color: '#ddd',
  normalizeFunction: 'linear',
  selectedRegions: false,
  showTooltip: true,
  pins: {
    id: '<div class="jqvmap-circle"></div>',
    my: '<div class="jqvmap-circle"></div>',
    th: '<div class="jqvmap-circle"></div>',
    sy: '<div class="jqvmap-circle"></div>',
    eg: '<div class="jqvmap-circle"></div>',
    ae: '<div class="jqvmap-circle"></div>',
    nz: '<div class="jqvmap-circle"></div>',
    tl: '<div class="jqvmap-circle"></div>',
    ng: '<div class="jqvmap-circle"></div>',
    si: '<div class="jqvmap-circle"></div>',
    pa: '<div class="jqvmap-circle"></div>',
    au: '<div class="jqvmap-circle"></div>',
    ca: '<div class="jqvmap-circle"></div>',
    tr: '<div class="jqvmap-circle"></div>',
  },
});


