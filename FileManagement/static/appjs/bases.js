document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar on mobile
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');

    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('sidebar-open');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', function(event) {
        if (window.innerWidth < 768 &&
            !sidebar.contains(event.target) &&
            !sidebarToggle.contains(event.target) &&
            sidebar.classList.contains('sidebar-open')) {
            sidebar.classList.remove('sidebar-open');
        }
    });

    // Simulate user data (in a real app, this would come from your backend)
    const userData = {
        first_name: "John",
        last_name: "Doe",
        profile_pic: "https://ui-avatars.com/api/?name=John+Doe&background=random",
        last_login: new Date().toLocaleString()
    };

    // Update user info in navbar
    const profileImg = document.querySelector('.nav-profile img');
    const profileName = document.querySelector('.nav-profile-name');
    const lastLogin = document.querySelector('.nav-user-status p');

    profileImg.src = userData.profile_pic;
    profileName.textContent = `${userData.first_name} ${userData.last_name}`;
    lastLogin.textContent = `Last login: ${userData.last_login}`;

    // Add active class to clicked nav items
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
});