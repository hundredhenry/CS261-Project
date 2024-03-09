function toggleSidebar() {
    var sidebar = document.getElementById("sidebar");
    var content = document.querySelector(".content");
    var arrowIcon = document.getElementById("arrow-icon");
    var button = document.querySelector(".button");
  
    if (sidebar.classList.contains("open")) {
      sidebar.classList.remove("open");
      content.style.marginLeft = "0%";
      button.style.backgroundColor = "white";
      arrowIcon.src = "https://cdn.animaapp.com/projects/65db38b26cce403ea94fca79/releases/65db38dbd8a7585f62fd00f2/img/forward@2x.png"
    } else {
      sidebar.classList.add("open");
      content.style.marginLeft = "40%";
      button.style.backgroundColor = "black";
      arrowIcon.src = "https://cdn.animaapp.com/projects/65db38b26cce403ea94fca79/releases/65dce3fc5df743f8480a7019/img/chevron-left@2x.png"
    }
  }
  
  var dropdownContent = document.getElementById("dropdownContent");
  
  function toggleDropdown(event) {
    event.stopPropagation(); // Prevent this event from triggering the click event on the document
    if (dropdownContent.style.display === "none") {
      dropdownContent.style.display = "block";
    } else {
      dropdownContent.style.display = "none";
    }
  }
  
  // Add an event listener to the document that hides the dropdown when you click outside of it
  document.addEventListener('click', function(event) {
    var isClickInside = dropdownContent.contains(event.target);
    if (!isClickInside) {
      dropdownContent.style.display = "none";
    }
  });