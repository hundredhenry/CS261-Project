window.addEventListener('load', function() {
  if (isAuthenticated) {
    fetch('/api/get/notifications')
      .then(response => response.json())
      .then(notifications => {
        const dropdownContent = document.getElementById('dropdownContent');
          dropdownContent.innerHTML = `
          <div class="inbox-header">
            <h1 class='inbox-heading'>Inbox</h1>
            <button id="clear-inbox" class="clear-inbox-button">Clear inbox</button>
          </div>`; // Clear the dropdown content

        if (notifications.length > 0) {          
          notifications.forEach(notification => {
            const notificationDate = new Date(notification.time);
            const currentDate = new Date();
            let timeText;
            const dateFormatter = new Intl.DateTimeFormat('en-GB', {
              day: '2-digit',
              month: '2-digit',
              year: '2-digit',
              hour: '2-digit',
              minute: '2-digit',
              hour12: false
          });      
            if (notificationDate.toDateString() !== currentDate.toDateString()) {
              timeText = 'Today • ' + dateFormatter.format(notificationDate).split(', ')[1];
            } else {
              timeText = dateFormatter.format(notificationDate).replace(', ', ' • ');
            }
            const row = document.createElement('div');
            row.className = 'dropdown-row';
            row.title = 'Click to delete'; // Add a tooltip

            const timeDiv = document.createElement('div');
            timeDiv.className = 'notification-time';
            timeDiv.textContent = timeText;
            row.appendChild(timeDiv); // Add the time div to the row

            const messageDiv = document.createElement('div');
            messageDiv.className = 'notification-message';
            messageDiv.textContent = notification.message;

            row.appendChild(messageDiv); // Add the message div to the row
            dropdownContent.appendChild(row);
          });
        } else {
          const row = document.createElement('div');
          row.className = 'empty-inbox-row';
          row.textContent = 'No notifications';
          dropdownContent.appendChild(row);
        }
      })
      .catch(error => console.error('Error fetching notifications:', error));
  }
});