document.addEventListener("DOMContentLoaded", () => {
    const hamburgerIcon = document.getElementById("hamburgerMenu");
    const sidebar = document.getElementById("sidebar");
    const darkOverlay = document.getElementById("darkOverlay");
    
    hamburgerIcon.addEventListener("click", openMenu);
    darkOverlay.addEventListener("click", closeMenu);
    
    function openMenu() {
        sidebar.classList.add("active");
        darkOverlay.classList.add("active");
    }
    
    function closeMenu() {
        sidebar.classList.remove("active");
        darkOverlay.classList.remove("active");
    }
});