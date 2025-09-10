let mentors = [];
const mentorsPerPage = 6;
let currentPage = 1;
let filteredMentors = [];

const mentorsContainer = document.getElementById('mentors-container');
const paginationNumbers = document.getElementById('pagination-numbers');
const prevButton = document.getElementById('prev-btn');
const nextButton = document.getElementById('next-btn');
const searchInput = document.getElementById('search-input');

async function fetchMentors() {
    try {
        const response = await fetch(window.location.href, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (response.ok) {
            const data = await response.json();
            mentors = data.mentors;
            filteredMentors = [...mentors];
            displayMentors();
            setupPagination();
        } else {
            throw new Error('Failed to fetch mentors');
        }
    } catch (error) {
        console.error('Error fetching mentors:', error);
        mentorsContainer.innerHTML = `
            <div class="col-span-full text-center py-12">
                <i class="fas fa-exclamation-triangle text-4xl text-red-400 mb-4"></i>
                <h3 class="text-xl font-semibold text-gray-300 mb-2">Error loading mentors</h3>
                <p class="text-gray-400">Please try refreshing the page</p>
            </div>
        `;
    }
}

function displayMentors() {
    mentorsContainer.innerHTML = '';

    const startIndex = (currentPage - 1) * mentorsPerPage;
    const endIndex = startIndex + mentorsPerPage;
    const paginatedMentors = filteredMentors.slice(startIndex, endIndex);

    if (paginatedMentors.length === 0) {
        mentorsContainer.innerHTML = `
            <div class="col-span-full text-center py-12">
                <i class="fas fa-search text-4xl text-gray-400 mb-4"></i>
                <h3 class="text-xl font-semibold text-gray-300 mb-2">No mentors found</h3>
                <p class="text-gray-400">Try adjusting your search criteria</p>
            </div>
        `;
        return;
    }

    paginatedMentors.forEach(mentor => {
        const profileImage = mentor.profile_photo_url ?
            `<img src="${mentor.profile_photo_url}" alt="${mentor.name}" class="w-16 h-16 sm:w-20 sm:h-20 rounded-full mx-auto mb-4 object-cover">` :
            `<div class="w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-r ${mentor.gradient} rounded-full mx-auto mb-4 flex items-center justify-center text-white font-semibold text-lg sm:text-xl">${mentor.initials}</div>`;

        const mentorCard = `
            <div class="bg-white rounded-xl p-6 sm:p-8 shadow-sm card-hover">
                <div class="text-center">
                    ${profileImage}
                    <h3 class="text-lg sm:text-xl font-bold mb-2 text-gray-800">${mentor.name}</h3>
                    <p class="text-purple-600 font-medium mb-1">${mentor.university}</p>
                    <p class="text-gray-600 text-sm sm:text-base mb-4">${mentor.department}</p>
                    
                    <div class="flex flex-col sm:flex-row gap-2 justify-center">
                        <a href="/mentors/ask-question/${mentor.slug}/" class="bg-gray-200 text-gray-800 py-2 px-4 rounded-lg text-sm font-medium hover:bg-gray-300 transition-colors text-center">
                            Ask a Question
                        </a>
                    </div>
                </div>
            </div>
        `;
        mentorsContainer.innerHTML += mentorCard;
    });
}

function setupPagination() {
    const pageCount = Math.ceil(filteredMentors.length / mentorsPerPage);
    paginationNumbers.innerHTML = '';

    if (pageCount <= 1) {
        prevButton.disabled = true;
        nextButton.disabled = true;
        return;
    }

    prevButton.disabled = currentPage === 1;

    nextButton.disabled = currentPage === pageCount;

    let startPage = Math.max(1, currentPage - 1);
    let endPage = Math.min(pageCount, startPage + 2);

    if (endPage - startPage < 2) {
        startPage = Math.max(1, endPage - 2);
    }

    if (startPage > 1) {
        const pageButton = document.createElement('button');
        pageButton.textContent = '1';
        pageButton.className = 'pagination-btn px-3 py-2 sm:px-4 sm:py-2 rounded-xl text-sm font-medium focus-ring';
        pageButton.addEventListener('click', () => goToPage(1));
        paginationNumbers.appendChild(pageButton);

        if (startPage > 2) {
            const ellipsis = document.createElement('span');
            ellipsis.textContent = '...';
            ellipsis.className = 'text-white/60 px-2';
            paginationNumbers.appendChild(ellipsis);
        }
    }

    for (let i = startPage; i <= endPage; i++) {
        const pageButton = document.createElement('button');
        pageButton.textContent = i;
        pageButton.className = i === currentPage ?
            'pagination-current px-3 py-2 sm:px-4 sm:py-2 rounded-xl text-sm font-medium focus-ring' :
            'pagination-btn px-3 py-2 sm:px-4 sm:py-2 rounded-xl text-sm font-medium focus-ring';
        pageButton.addEventListener('click', () => goToPage(i));
        paginationNumbers.appendChild(pageButton);
    }

    if (endPage < pageCount) {
        if (endPage < pageCount - 1) {
            const ellipsis = document.createElement('span');
            ellipsis.textContent = '...';
            ellipsis.className = 'text-white/60 px-2';
            paginationNumbers.appendChild(ellipsis);
        }

        const pageButton = document.createElement('button');
        pageButton.textContent = pageCount;
        pageButton.className = 'pagination-btn px-3 py-2 sm:px-4 sm:py-2 rounded-xl text-sm font-medium focus-ring';
        pageButton.addEventListener('click', () => goToPage(pageCount));
        paginationNumbers.appendChild(pageButton);
    }
}

function goToPage(page) {
    currentPage = page;
    displayMentors();
    setupPagination();
    window.scrollTo({
        top: mentorsContainer.offsetTop - 100,
        behavior: 'smooth'
    });
}

function filterMentors() {
    const searchTerm = searchInput.value.toLowerCase();

    if (searchTerm === '') {
        filteredMentors = [...mentors];
    } else {
        filteredMentors = mentors.filter(mentor =>
            mentor.name.toLowerCase().includes(searchTerm) ||
            mentor.university.toLowerCase().includes(searchTerm) ||
            mentor.department.toLowerCase().includes(searchTerm)
        );
    }

    currentPage = 1;
    displayMentors();
    setupPagination();
}

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

    fetchMentors();

    setupMobileMenu();

    if (searchInput) {
        searchInput.addEventListener('input', filterMentors);
    }
    if (prevButton) {
        prevButton.addEventListener('click', () => goToPage(currentPage - 1));
    }
    if (nextButton) {
        nextButton.addEventListener('click', () => goToPage(currentPage + 1));
    }
    window.addEventListener('scroll', handleNavbarScroll);
});