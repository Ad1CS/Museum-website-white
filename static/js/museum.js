/* museum.js — Ленинградский мясокомбинат им. С.М. Кирова */

// ============================================================
// PAGE TRANSITIONS
// ============================================================
const PAGE_TRANSITION_DURATION = 320;
// DOMContentLoaded can fire in the same task as the page's first paint, or
// even before it, on a page that loads fast enough (a local server, a warm
// cache, a simple page). Reveal the page the instant that event fires and
// there's nothing for the fade to visibly fade FROM — the overlay was never
// actually painted as opaque, so the "cover, then reveal" effect collapses
// into the page just appearing outright. This is a floor, not a fixed
// delay: it guarantees at least one real frame paints with the overlay
// fully opaque before the reveal starts, so the fade always has something
// to animate from, regardless of how fast the page loaded.
const PAGE_REVEAL_HOLD_MS = 120;
const PAGE_TRANSITION_DOWNLOAD_RE = /\.(?:pdf|docx?|xlsx?|pptx?|zip|rar|7z|jpe?g|png|gif|webp|mp4|mov|avi|mp3|wav)$/i;
let pageTransitionActive = false;

function setPageLoaded() {
  pageTransitionActive = false;
  const root = document.documentElement;
  root.classList.add('page-loaded');
  root.classList.remove('page-leaving');
}

function prefersReducedPageMotion() {
  return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

function shouldUsePageTransition(link, currentUrl) {
  if (!link || (link.target && link.target !== '_self')) return false;
  if (link.hasAttribute('download') || link.closest('[data-no-page-transition="true"]')) return false;
  if (link.dataset.noPageTransition === 'true') return false;

  const href = link.getAttribute('href') || '';
  if (!href || href.charAt(0) === '#') return false;

  let nextUrl;
  try {
    nextUrl = new URL(link.href, window.location.href);
  } catch (error) {
    return false;
  }

  if (nextUrl.origin !== currentUrl.origin) return false;
  if (!['http:', 'https:'].includes(nextUrl.protocol)) return false;
  if (nextUrl.pathname === '/admin' || nextUrl.pathname.startsWith('/admin/')) return false;
  if (PAGE_TRANSITION_DOWNLOAD_RE.test(nextUrl.pathname)) return false;
  if (nextUrl.href === currentUrl.href) return false;
  if (nextUrl.pathname === currentUrl.pathname && nextUrl.search === currentUrl.search && nextUrl.hash) return false;

  return nextUrl;
}

function startPageTransitionTo(href) {
  if (!href) return;

  if (prefersReducedPageMotion()) {
    window.location.assign(href);
    return;
  }

  if (pageTransitionActive) return;
  pageTransitionActive = true;

  const root = document.documentElement;
  root.classList.add('page-transition');
  root.classList.add('page-loaded');
  root.classList.remove('page-leaving');
  // Forces the browser to commit the "not leaving" state above before the
  // class change below, so the opacity transition still animates from 0
  // instead of jumping straight to 1. This used to happen inside a
  // requestAnimationFrame callback, but rAF is suspended entirely while the
  // tab is backgrounded — if focus moved away between the click and the
  // next frame (switching tabs, alt-tabbing, anything), that callback would
  // simply never run, and the click would silently do nothing forever: no
  // error, no navigation, the page just sits there. The forced reflow above
  // already provides the same guarantee synchronously, so the class change
  // below doesn't need to wait for a frame at all.
  void root.offsetWidth;
  root.classList.add('page-leaving');

  window.setTimeout(function () {
    window.location.assign(href);
  }, PAGE_TRANSITION_DURATION);
}

window.startPageTransitionTo = startPageTransitionTo;

document.addEventListener('DOMContentLoaded', function () {
  window.setTimeout(setPageLoaded, PAGE_REVEAL_HOLD_MS);
});

window.addEventListener('pageshow', function () {
  window.setTimeout(setPageLoaded, PAGE_REVEAL_HOLD_MS);
});

document.addEventListener('click', function (event) {
  if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  if (prefersReducedPageMotion()) return;

  const clickTarget = event.target instanceof Element ? event.target : event.target.parentElement;
  if (!clickTarget) return;

  const link = clickTarget.closest('a[href]');
  const currentUrl = new URL(window.location.href);
  const nextUrl = shouldUsePageTransition(link, currentUrl);
  if (!nextUrl) return;

  event.preventDefault();
  startPageTransitionTo(nextUrl.href);
});

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
