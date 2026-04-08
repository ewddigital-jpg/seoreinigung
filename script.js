// K.K. Reinigung – script.js

// ── Mobile menu ─────────────────────────────────────────────
const menuBtn  = document.getElementById('menu-btn');
const mobileNav = document.getElementById('mobile-nav');

if (menuBtn && mobileNav) {
  menuBtn.addEventListener('click', () => {
    const open = mobileNav.classList.toggle('open');
    menuBtn.setAttribute('aria-expanded', open);
    menuBtn.innerHTML = open
      ? `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M6 18L18 6M6 6l12 12"/></svg>`
      : `<svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg>`;
  });
}

// ── Header scroll shadow ────────────────────────────────────
const header = document.getElementById('site-header');
if (header) {
  window.addEventListener('scroll', () => {
    header.classList.toggle('scrolled', window.scrollY > 20);
  }, { passive: true });
}

// ── Scroll-reveal ───────────────────────────────────────────
const revealEls = document.querySelectorAll('.reveal');
if (revealEls.length) {
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  revealEls.forEach(el => io.observe(el));
}

// ── Contact form ────────────────────────────────────────────
const contactForm = document.getElementById('contact-form');
if (contactForm) {
  contactForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = contactForm.querySelector('[type="submit"]');
    const orig = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Wird gesendet…';

    const data = new FormData(contactForm);
    try {
      const res = await fetch(contactForm.action, {
        method: 'POST',
        body: data,
        headers: { 'Accept': 'application/json' }
      });
      if (res.ok) {
        contactForm.innerHTML = `
          <div class="text-center py-8">
            <div class="text-4xl mb-3">✅</div>
            <h3 class="text-lg font-bold text-gray-900 mb-2">Vielen Dank!</h3>
            <p class="text-gray-600">Wir melden uns in der Regel noch am selben Tag bei Ihnen.</p>
          </div>`;
      } else {
        throw new Error('Server error');
      }
    } catch {
      btn.disabled = false;
      btn.textContent = orig;
      alert('Etwas ist schiefgelaufen. Bitte rufen Sie uns direkt an: 0177 8740889');
    }
  });
}

// ── Track WhatsApp clicks (console log – replace with GA4) ──
document.querySelectorAll('a[href*="wa.me"]').forEach(a => {
  a.addEventListener('click', () => {
    // gtag('event', 'whatsapp_click', { event_category: 'contact' });
    console.log('WhatsApp click tracked');
  });
});

// ── Track phone clicks ───────────────────────────────────────
document.querySelectorAll('a[href^="tel:"]').forEach(a => {
  a.addEventListener('click', () => {
    // gtag('event', 'phone_click', { event_category: 'contact' });
    console.log('Phone click tracked');
  });
});
