document.addEventListener('DOMContentLoaded', function() {
  var sentimentChartElement = document.querySelector('.sentiment-doughnut');
  var positive = sentimentChartElement.getAttribute('data-positive');
  var negative = sentimentChartElement.getAttribute('data-negative');

  var ctx = document.getElementById('sentimentDoughnut').getContext('2d');
  var sentimentDoughnutChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
          labels: ['Positive Articles', 'Negative Articles'],
          datasets: [{
              label: 'Percentage',
              data: [positive, negative],
              backgroundColor: [
                  'rgba(75, 192, 132, 0.8)',
                  'rgba(255, 99, 132, 0.8)'
              ],
              borderWidth: 2,
              borderColor: 'white'
          }]
      },
      options: {
          plugins: {
              legend: {
                  display: false
              }
          },
          responsive: false
      }
  });

  Chart.register({
      id: 'doughnutCenterText',
      beforeDraw: function(chart) {
          if (chart.canvas.id !== 'sentimentDoughnut') return; // Ensure this applies to doughnut chart only

          var width = chart.width,
              height = chart.height,
              ctx = chart.ctx;

          ctx.restore();
          var fontSize = (height / 140).toFixed(2);
          ctx.font = fontSize + "em sans-serif";
          ctx.textBaseline = "middle";

          var positivePercentage = parseFloat(positive) / (parseFloat(positive) + parseFloat(negative));

          var color = `rgb(${Math.round((255 - 75) * (1 - positivePercentage) + 75)}, ${Math.round((192 - 99) * positivePercentage + 99)}, 132)`;

          ctx.fillStyle = color;

          var text = `${Math.round(positivePercentage * 100)}`;
          var textX = Math.round((width - ctx.measureText(text).width) / 2);
          var textY = height / 2;

          ctx.fillText(text, textX, textY);
          ctx.save();
      }
  });
});
