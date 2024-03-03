function modifyFollowCompany(event, button, followText, unfollowText) {
    event.preventDefault();
    var ticker = button.getAttribute('data-ticker');
    fetch('/modify-follow/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ticker: ticker}),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'following') {
            button.textContent = unfollowText;
        } else if (data.status === 'unfollowing') {
            button.textContent = followText;
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
