
(function () {
    // Check for saved theme preference, otherwise default to dark
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);

    window.toggleTheme = function () {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        // Toggle betwen 'dark' (Red/Black) and 'gold' (Midnight Gold)
        const newTheme = currentTheme === 'dark' ? 'gold' : 'dark';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);

        // Update icon visibility
        updateThemeIcon(newTheme);
    };

    function updateThemeIcon(theme) {
        const icon = document.getElementById('theme-icon');
        if (icon) {
            icon.className = 'fas'; // Reset classes
            if (theme === 'dark') {
                icon.classList.add('fa-moon');
            } else {
                icon.classList.add('fa-crown'); // Crown icon for 'Executive/Gold' theme
            }
        }
    }

    // Initialize icon on load
    document.addEventListener('DOMContentLoaded', () => {
        updateThemeIcon(localStorage.getItem('theme') || 'dark');
    });
})();
