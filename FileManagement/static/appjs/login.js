// Login Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Password visibility toggle
    const passwordToggle = document.getElementById('passwordToggle');
    const passwordField = document.getElementById('id_password');

    if (passwordToggle && passwordField) {
        passwordToggle.addEventListener('click', function() {
            const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField.setAttribute('type', type);

            // Toggle icon
            this.querySelector('i').classList.toggle('fa-eye');
            this.querySelector('i').classList.toggle('fa-eye-slash');
        });
    }

    // Form validation
    const loginForm = document.querySelector('form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            let isValid = true;
            const username = document.getElementById('id_username');
            const password = document.getElementById('id_password');

            // Reset previous errors
            username.classList.remove('is-invalid');
            password.classList.remove('is-invalid');

            // Validate username
            if (!username.value.trim()) {
                username.classList.add('is-invalid');
                isValid = false;
            }

            // Validate password
            if (!password.value.trim()) {
                password.classList.add('is-invalid');
                isValid = false;
            }

            if (!isValid) {
                e.preventDefault();

                // Show error message if not already shown
                if (!document.querySelector('.alert-danger')) {
                    const alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-danger';
                    alertDiv.innerHTML = '<i class="fas fa-exclamation-circle me-2"></i> Please fill in all required fields.';
                    loginForm.prepend(alertDiv);

                    // Remove alert after 5 seconds
                    setTimeout(() => {
                        alertDiv.remove();
                    }, 5000);
                }
            } else {
                // Add loading animation to button
                const submitBtn = this.querySelector('button[type="submit"]');
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging in...';
                submitBtn.disabled = true;

                // Revert after 3 seconds (for demo purposes)
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 3000);
            }
        });
    }

    // Input focus effects
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
    });

    // Add animation to form elements
    const formGroups = document.querySelectorAll('.mb-3');
    formGroups.forEach((group, index) => {
        group.style.opacity = '0';
        group.style.transform = 'translateY(10px)';
        group.style.transition = 'opacity 0.5s ease, transform 0.5s ease';

        setTimeout(() => {
            group.style.opacity = '1';
            group.style.transform = 'translateY(0)';
        }, 100 + (index * 100));
    });

    // Language toggle functionality
    const languageBtn = document.getElementById('languageToggle');
    if (languageBtn) {
        languageBtn.addEventListener('click', function() {
            const currentLang = this.getAttribute('data-current-lang');
            const newLang = currentLang === 'en' ? 'mr' : 'en';

            // Update button text and data attribute
            this.innerHTML = currentLang === 'en' ? 'MR' : 'EN';
            this.setAttribute('data-current-lang', newLang);

            // Here you would typically redirect to the language-specific URL
            // or use a translation library to update the page content
            console.log('Switching to language:', newLang);
        });
    }
});