function handleNavbarScroll() {
    const navbar = document.getElementById('navbar');
    const scrollY = window.scrollY;
    const heroSection = document.getElementById('hero-section');

    if (!heroSection) return;

    const heroHeight = heroSection.offsetHeight;

    navbar.classList.remove('navbar-glass', 'navbar-white');

    if (scrollY > 50) {
        if (scrollY < heroHeight - 100) {
            navbar.classList.add('navbar-glass');
        } else {
            navbar.classList.add('navbar-white');
        }
    } else {
        navbar.classList.add('navbar-glass');
    }
}

function setupMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    const menuIcon = document.getElementById('menu-icon');

    if (!mobileMenuBtn || !mobileMenu || !menuIcon) return;

    mobileMenuBtn.addEventListener('click', function () {
        mobileMenu.classList.toggle('active');
        if (mobileMenu.classList.contains('active')) {
            menuIcon.classList.remove('fa-bars');
            menuIcon.classList.add('fa-times');
        } else {
            menuIcon.classList.remove('fa-times');
            menuIcon.classList.add('fa-bars');
        }
    });

    const mobileMenuLinks = mobileMenu.querySelectorAll('a');
    mobileMenuLinks.forEach(link => {
        link.addEventListener('click', function () {
            mobileMenu.classList.remove('active');
            menuIcon.classList.remove('fa-times');
            menuIcon.classList.add('fa-bars');
        });
    });
}

document.addEventListener('DOMContentLoaded', function () {
    handleNavbarScroll();


    setupMobileMenu();


    window.addEventListener('scroll', handleNavbarScroll);
});