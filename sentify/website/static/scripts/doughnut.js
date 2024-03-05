document.addEventListener('DOMContentLoaded', function() {
    var sentimentChartElement = document.querySelector('.sentiment-chart');
    var positive = sentimentChartElement.getAttribute('data-positive');
    var negative = sentimentChartElement.getAttribute('data-negative');
  
    var ctx = document.getElementById('sentimentChart').getContext('2d');
    var sentimentChart = new Chart(ctx, {
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
          doughnutCenterText: {  
          },
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
        var width = chart.width,
            height = chart.height,
            ctx = chart.ctx;
  
        ctx.restore();
        var fontSize = (height / 140).toFixed(2); 
        ctx.font = fontSize + "em sans-serif";
        ctx.textBaseline = "middle";
  
        var positivePercentage = parseFloat(positive) / (parseFloat(positive) + parseFloat(negative));
        
        // Interpolating the RGB channels based on positive percentage
        var redChannel = Math.round((255 - 75) * (1 - positivePercentage) + 75);
        var greenChannel = Math.round((192 - 99) * positivePercentage + 99);
        var blueChannel = 132; // Keeping the blue channel constant as in your colors
        
        var color = `rgb(${redChannel}, ${greenChannel}, ${blueChannel})`;
        
        ctx.fillStyle = color; 
  
        var text = positive; 
        var textX = Math.round((width - ctx.measureText(text).width) / 2);
        var textY = height / 2; // Adjusted to center the text
  
        ctx.fillText(text, textX, textY);
        ctx.save();
      }
    });
}); 
