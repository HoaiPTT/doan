"use strict";

fetch('/api/subscription_report/')
  .then(response => response.json())
  .then(data => {
    const ctx = document.getElementById("myChart").getContext('2d');
    const myChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.labels,
        datasets: [{
          label: 'Doanh thu (VNĐ)',
          data: data.revenues,
          borderWidth: 2,
          borderColor: 'rgba(63,82,227,.8)',
          backgroundColor: 'rgba(63,82,227,.2)',
          fill: true,
          tension: 0.3
        }, {
          label: 'Số người đăng ký',
          data: data.counts,
          borderWidth: 2,
          borderColor: 'rgba(254,86,83,.8)',
          backgroundColor: 'rgba(254,86,83,.1)',
          fill: true,
          tension: 0.3
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: true },
          tooltip: {
            callbacks: {
              label: (ctx) => ctx.dataset.label + ': ' + ctx.formattedValue
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: 'VNĐ / Người' }
          },
          x: {
            title: { display: true, text: 'Tháng' }
          }
        }
      }
    });
  })
  .catch(error => console.error('Error loading chart data:', error));
