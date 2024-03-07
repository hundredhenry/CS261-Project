window.addEventListener('load', function() {
    fetch('/api/get/notifications')
      .then(response => response.json())
      .then(notifications => {
        const dropdownContent = document.getElementById('dropdownContent');
          dropdownContent.innerHTML = `
          <div class="inbox-header">
            <h1 class='inbox-heading'>Inbox</h1>
          </div>`; 
        const inboxHeader = dropdownContent.querySelector('.inbox-header');
        if (notifications.length > 0) {   
          inboxHeader.innerHTML += `<button id="clear-inbox" class="clear-inbox-button">Clear inbox</button>`;
          notifications.forEach(notification => {
            const notificationDate = new Date(notification.time);
            const timeText = constructTimeText(notificationDate);
            const row = constructNotification(notification.message, timeText, notification.id);
            dropdownContent.appendChild(row);
          });
        } else {
          dropdownContent.innerHTML += `<div class='empty-inbox-row'> No notifications </div>`;
        }
        const clearInboxButton = document.getElementById('clear-inbox');
        clearInboxButton.onclick = clearInbox;
      })
      .catch(error => console.error('Error fetching notifications:', error));
});

function constructTimeText(notificationDate) {
  let timeText;
  const currentDate = new Date();
  const dateFormatter = new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: '2-digit',
    year: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  });
  if (notificationDate.toDateString() === currentDate.toDateString()) {
    timeText = 'Today • ' + dateFormatter.format(notificationDate).split(', ')[1];
  } else {
    timeText = dateFormatter.format(notificationDate).replace(', ', ' • ');
  }
  return timeText;
}

function constructNotification(message, timeText, notificationId) {
  const row = document.createElement('div');
  row.className = 'dropdown-row';
  row.title = 'Click to delete'; // Add a tooltip

  const timeDiv = document.createElement('div');
  timeDiv.className = 'notification-time';
  timeDiv.textContent = timeText;
  row.appendChild(timeDiv); // Add the time div to the row

  const messageDiv = document.createElement('div');
  messageDiv.className = 'notification-message';
  messageDiv.textContent = message;
  row.appendChild(messageDiv); // Add the message div to the row

  // Add an event listener to delete the notification when it's clicked
  row.addEventListener('click', function() {
    fetch(`/api/delete/notification/${notificationId}`, { method: 'DELETE' })
      .then(response => {
        if (!response.ok) {
          throw new Error('HTTP error ' + response.status);
        }
        return response.json();  // we only proceed once the promise is resolved
      })
      .then(() => {
        row.remove();
        toastr.success('Notification deleted!');

        // Check if there are any notifications left
        const dropdownContent = document.getElementById('dropdownContent');
        if (!dropdownContent.querySelector('.dropdown-row')) {
          // If there are no notifications left, add the "No notifications" message
          const emptyRow = document.createElement('div');
          emptyRow.className = 'empty-inbox-row';
          emptyRow.textContent = 'No notifications';
          dropdownContent.appendChild(emptyRow);
          const clearInboxButton = document.getElementById('clear-inbox');
          if (clearInboxButton) {
            clearInboxButton.remove();
          }

        }
      })
      .catch(error => toastr.error('Error deleting notification: ' + error));
  });

  return row;
}

function clearInbox() {
  fetch('/api/delete/notifications', { method: 'DELETE' })
    .then(() => {
      const dropdownContent = document.getElementById('dropdownContent');
      dropdownContent.innerHTML = `
        <div class="inbox-header">
          <h1 class='inbox-heading'>Inbox</h1>
        </div>
        <div class="empty-inbox-row">No notifications</div>
      `;
      toastr.success('Inbox cleared!');
    })
    .catch(error => toastr.error('Error deleting notifications:'));
}