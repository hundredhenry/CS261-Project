function modifyFollowCompany(event, button, followText, unfollowText) {
    event.preventDefault();
    var ticker = button.getAttribute('data-ticker');
    fetch('/api/modify/follow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ticker: ticker
        }),
      })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'followed') {
          button.textContent = followText;
          toastr.success('Followed ' + ticker + '!');
        } else if (data.status === 'unfollowed') {
          button.textContent = unfollowText;
          toastr.success('No longer following ' + ticker + '!');
        }
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  }