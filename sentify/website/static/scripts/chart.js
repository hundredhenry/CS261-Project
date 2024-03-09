document.addEventListener('DOMContentLoaded', function() {

    var sentimentChartElement = document.querySelector('.sentiment-doughnut');
    var positive = sentimentChartElement.getAttribute('data-positive');
    var negative = sentimentChartElement.getAttribute('data-negative');
  
    // Check if positive and negative values are not provided or "None"
    var isDataUnavailable = !positive || !negative || positive === 'None' || negative === 'None';
    var data, backgroundColor;
  
    if (isDataUnavailable) {
      // If data is unavailable, use dummy values and grey color
      data = [100]; // Dummy value to create a single slice
      backgroundColor = ['rgba(211, 211, 211, 0.8)']; // Light grey color
    } else {
      // If data is available, use actual values and specified colors
      data = [positive, negative];
      backgroundColor = [
        'rgba(75, 192, 132, 0.8)', // Green color
        'rgba(255, 99, 132, 0.8)' // Red color
      ];
    }
  
    var ctx = document.getElementById('sentimentDoughnut').getContext('2d');
    var sentimentDoughnutChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: isDataUnavailable ? ['Data Unavailable'] : ['Positive Articles', 'Negative Articles'],
        datasets: [{
          label: 'Percentage',
          data: data,
          backgroundColor: backgroundColor,
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
        responsive: true
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
  
        var text, color;
        if (isDataUnavailable) {
          // Display "0" in grey color if data is unavailable
          text = "-";
          color = 'rgba(169, 169, 169, 1)'; // Darker grey color for the text
        } else {
          var positivePercentage = parseFloat(positive) / (parseFloat(positive) + parseFloat(negative));
          text = `${Math.round(positivePercentage * 100)}`;
          color = `rgb(${Math.round((255 - 75) * (1 - positivePercentage) + 75)}, ${Math.round((192 - 99) * positivePercentage + 99)}, 132)`;
        }
  
        ctx.fillStyle = color;
  
        var textX = Math.round((width - ctx.measureText(text).width) / 2);
        var textY = height / 2;
  
        ctx.fillText(text, textX, textY);
        ctx.save();
      }
    });
  
  
    var ctx2 = document.getElementById('sentimentChart').getContext('2d');
  
    var sentimentChart = new Chart(ctx2, {
      type: 'line',
      data: chartData, // Use chartData directly
      options: {
        scales: {
          y: {
            beginAtZero: true,
            max: 100,
            ticks: {
              stepSize: 10
            }
          }
        },
        plugins: {
          legend: {
            display: false
          }
        },
      }
    });
  });