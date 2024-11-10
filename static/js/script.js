document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('a.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href.startsWith('#')) {
                e.preventDefault();
                document.querySelector(href).scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    document.querySelector('.navbar-toggler').addEventListener('click', function() {
        this.classList.toggle('rotate');
    });
});
