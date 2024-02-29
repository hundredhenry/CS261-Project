let companies = [];

window.onload = function() {
    fetch('/retrieve_companies/')
        .then(response => response.json())
        .then(data => companies = data);
}

function searchFunction(query) {
    let results = query ? companies.filter(company => company.company_name.toLowerCase().includes(query.toLowerCase()) || company.stock_ticker.toLowerCase().includes(query.toLowerCase())) : [];
    results = results.slice(0, 5); // limit the results to a maximum of 5

    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = ''; // clear previous results
    if (results.length === 0) {  
        if (query) {
            resultsDiv.textContent = 'No matches';
        } else {
            resultsDiv.style.display = 'none';
        }
    } else {
        resultsDiv.style.display = 'block';
        results.forEach(company => {
            const a = document.createElement('a');
            a.href = '/company/' + company.stock_ticker;

            const div = document.createElement('div');
            div.className = 'result-item'; // apply the CSS class

            const nameSpan = document.createElement('span');
            nameSpan.textContent = company.company_name;
            div.appendChild(nameSpan);

            const tickerSpan = document.createElement('span');
            tickerSpan.textContent = company.stock_ticker;
            tickerSpan.className = 'ticker'; // apply a different CSS class
            div.appendChild(tickerSpan);

            a.appendChild(div);
            resultsDiv.appendChild(a);
        });
    }
}