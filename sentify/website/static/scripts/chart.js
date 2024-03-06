document.addEventListener('DOMContentLoaded', function() {
    var ctx = document.getElementById('sentimentChart').getContext('2d');

    var sentimentChart = new Chart(ctx, {
        type: 'line',
        data: chartData, // Use chartData directly
        options: {
            scales: {
                y: {
                    beginAtZero: true
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
