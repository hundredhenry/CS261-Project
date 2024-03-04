function toggleSidebar() {
    var sidebar = document.getElementById("sidebar");
    var content = document.querySelector(".content");
    var arrowIcon = document.getElementById("arrow-icon");
    var button = document.querySelector(".button");
    
    if (sidebar.classList.contains("open")) {
        sidebar.classList.remove("open");
        content.style.marginLeft = "0%"; 
        button.style.backgroundColor = "white"; 
        arrowIcon.src="https://cdn.animaapp.com/projects/65db38b26cce403ea94fca79/releases/65db38dbd8a7585f62fd00f2/img/forward@2x.png"
    } else {
        sidebar.classList.add("open");
        content.style.marginLeft = "40%"; 
        button.style.backgroundColor = "black"; 
        arrowIcon.src="https://cdn.animaapp.com/projects/65db38b26cce403ea94fca79/releases/65dce3fc5df743f8480a7019/img/chevron-left@2x.png"
    }
}

function toggleDropdown() {
    var dropdownContent = document.getElementById("dropdownContent");
    if (dropdownContent.style.display === "none") {
        dropdownContent.style.display = "block";
    } else {
        dropdownContent.style.display = "none";
    }
}
