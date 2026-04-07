/* museum.js — Ленинградский мясокомбинат им. С.М. Кирова */

// ============================================================
// MOBILE DRAWER
// ============================================================
function toggleDrawer() {
  const drawer = document.getElementById('mobile-drawer');
  const hamburger = document.getElementById('hamburger');
  if (!drawer) return;
  const isOpen = drawer.classList.contains('open');
  drawer.classList.toggle('open', !isOpen);
  hamburger.classList.toggle('open', !isOpen);
  hamburger.setAttribute('aria-expanded', String(!isOpen));
  document.body.style.overflow = isOpen ? '' : 'hidden';
}

function closeDrawer(e) {
  if (e.target === document.getElementById('mobile-drawer')) {
    closeDrawerDirect();
  }
}

function closeDrawerDirect() {
  const drawer = document.getElementById('mobile-drawer');
  const hamburger = document.getElementById('hamburger');
  if (!drawer) return;
  drawer.classList.remove('open');
  hamburger.classList.remove('open');
  hamburger.setAttribute('aria-expanded', 'false');
  document.body.style.overflow = '';
}

// Close drawer on Escape
document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') {
    closeDrawerDirect();
  }
});

// ============================================================
// ACTIVE NAV HIGHLIGHT
// Ensures correct item is highlighted based on current path
// ============================================================
document.addEventListener('DOMContentLoaded', function () {
  const path = window.location.pathname;
  document.querySelectorAll('#header nav a, .mobile-nav-links a').forEach(function (a) {
    const href = a.getAttribute('href');
    if (href && href !== '/' && path.startsWith(href)) {
      a.classList.add('active');
    } else if (href === '/' && path === '/') {
      a.classList.add('active');
    }
  });

  // Bottom nav
  document.querySelectorAll('.bottom-nav-btn').forEach(function (btn) {
    const href = btn.getAttribute('href');
    if (href && href !== '/' && path.startsWith(href)) {
      btn.classList.add('active');
    } else if (href === '/' && path === '/') {
      btn.classList.add('active');
    }
  });
});

// ============================================================
// CAROUSEL
// ============================================================
function scrollCarousel(id, amount) {
  const el = document.getElementById(id);
  if (!el) return;
  const maxScrollLeft = el.scrollWidth - el.clientWidth;
  // If we're at the end (or very close), loop back to start
  if (el.scrollLeft >= maxScrollLeft - 10) {
    el.scrollTo({ left: 0, behavior: 'smooth' });
  } else {
    el.scrollBy({ left: amount, behavior: 'smooth' });
  }
}

// ============================================================
// SMOOTH SCROLL for anchor links
// ============================================================
document.querySelectorAll('a[href^="#"]').forEach(function (a) {
  a.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});
