// main.js - Custom JavaScript for Data Management System

document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle functionality
    const sidebarToggle = document.querySelector('[data-toggle="minimize"]');
    const sidebar = document.getElementById('sidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
            // You can add additional toggle logic here
        });
    }

    // Initialize Bootstrap tooltips for action icons
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Table row selection
    const tableRows = document.querySelectorAll('.table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('click', function(e) {
            // Avoid triggering when clicking on action icons
            if (!e.target.closest('.action-icons')) {
                this.classList.toggle('table-active');
            }
        });
    });

    // Search functionality
    const searchButton = document.querySelector('.btn-search');
    if (searchButton) {
        searchButton.addEventListener('click', function() {
            // Implement search functionality here
            const searchTerm = prompt('Enter search term:');
            if (searchTerm) {
                // Filter table rows based on search term
                filterTable(searchTerm);
            }
        });
    }

    // Download functionality
    const downloadButton = document.querySelector('.btn-download');
    if (downloadButton) {
        downloadButton.addEventListener('click', function() {
            // Implement download functionality here
            alert('Download functionality would be implemented here');
        });
    }

    // Create functionality
    const createButton = document.querySelector('.btn-create');
    if (createButton) {
        createButton.addEventListener('click', function() {
            // Implement create functionality here
            window.location.href = '/create/'; // Adjust URL as needed
        });
    }
});

function filterTable(searchTerm) {
    const rows = document.querySelectorAll('.table tbody tr');
    const searchLower = searchTerm.toLowerCase();

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchLower)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

// Additional utility functions
function formatDate(dateString) {
    // Format date for display
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

function showNotification(message, type = 'info') {
    // Show notification to user
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.querySelector('.main-content').prepend(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// main.js - For sidebar and interactive elements
document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle functionality for mobile
    const sidebarToggle = document.createElement('button');
    sidebarToggle.innerHTML = '<i class="fas fa-bars"></i>';
    sidebarToggle.className = 'btn btn-light d-md-none';
    sidebarToggle.style.position = 'fixed';
    sidebarToggle.style.top = '70px';
    sidebarToggle.style.left = '10px';
    sidebarToggle.style.zIndex = '1000';

    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');

    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('show');
        mainContent.classList.toggle('sidebar-collapsed');
    });

    document.querySelector('.navbar').appendChild(sidebarToggle);

    // Add active class to clicked nav items
    const navLinks = document.querySelectorAll('.sidebar .nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
});