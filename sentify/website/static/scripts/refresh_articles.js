function truncateText(text, maxLength) {
    if (text.length > maxLength) {
      return text.substring(0, maxLength) + '...';
    } else {
      return text;
    }
  }
  
  function refreshArticles(tickers, currentArticles, articlesTab) {
    var tickersString = tickers.join(',');
    // Fetch the articles from the server
    fetch(`/api/get/articles?tickers=${tickersString}`)
      .then(response => response.json())
      .then(newArticles => {
        if (JSON.stringify(newArticles) !== JSON.stringify(currentArticles)) {
          // Clear the existing articles
          var articlesSection = document.querySelector('.' + articlesTab);
  
          function generateTags(topics) {
            return topics.map(topic => `<span class="tag">${topic}</span>`).join('');
          }
          // Clear the existing articles
          articlesSection.innerHTML = '';
          // Loop through each ticker
          // Loop through each article
          newArticles.articles.forEach(article => {
            // Generate the HTML for the article
            var str = article.sentiment_label.toLowerCase();
  
            var articleHTML = `
                      <div class="article">
                          <div class="article-left">
                              <div class="article-header">
                                  <h2 class="article-source">
                                  <a href="http://${article.source_domain}" target="_blank">
                                      ${article.source}</a> • ${article.published}
                                  </h2>                           
                          </div>
                              <a href="${article.url}">
                                  <h1 class="article-title">${truncateText(article.title, 80)}</h1>
                              </a>
                              <p class="article-content">${article.description ? truncateText(article.description, 225) : 'No description available for this article.'}</p>
                              <div class="article-tags">
                                  ${generateTags(article.topics)}
                              </div>
                          </div>
                          <div class="article-right">
                          <img src="${article.banner_image ? article.banner_image : '/static/images/'+article.ticker+'.png'}" alt="Banner Image">
                          <button class="article-rating ${article.sentiment_label.toLowerCase()}" data-confidence="${article.sentiment_score}">${str.charAt(0).toUpperCase() + str.slice(1)}</button>
                          </div>
                      </div>
                      <hr style='width: 100%;'>
                  `;
  
            // Insert the article HTML into the page
            articlesSection.innerHTML += articleHTML;
          });
  
        }
        addEventListenersToButtons();
        currentArticles = newArticles;
        return currentArticles;
      })
      .catch(error => console.error('Error:', error));
  }
  
  function addEventListenersToButtons() {
    // Get all buttons with the class 'article-rating'
    var buttons = document.querySelectorAll('.article-rating');
  
    // Add event listeners to each button
    buttons.forEach(button => {
      var originalText = button.textContent;
      button.addEventListener('mouseover', function() {
        // Change the text of the button to the confidence rating
        var confidence = this.getAttribute('data-confidence');
        var percentage = (confidence * 100).toFixed(1) + '%';
        this.textContent = percentage + ' Sure';
      });
      button.addEventListener('mouseout', function() {
        // Change the text of the button back to the original text
        this.textContent = originalText;
      });
    });
  }