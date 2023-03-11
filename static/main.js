const nav_burger = document.querySelector('.navbar-burger');
const nav_menu = document.querySelector('.navbar-menu');

nav_burger.addEventListener('click', () => {
    nav_burger.classList.toggle('is-active');
    nav_menu.classList.toggle('is-active');
});