"""
Updates all subpages of kkreinigung to match index.html header/footer/widgets.
"""
import re, os

REPO = r'C:\Users\danie\seoreinigung-repo'

with open(os.path.join(REPO, 'index.html'), 'r', encoding='utf-8') as f:
    idx = f.read()

# ── Extract sections from index.html ────────────────────────────
header_m  = re.search(r'(<!-- ── Header ─+.*?</header>)', idx, re.DOTALL)
mobnav_m  = re.search(r'(<!-- Mobile Nav -->\s*<nav class="mobile-nav".*?</nav>)', idx, re.DOTALL)
footer_m  = re.search(r'(<footer class="site-footer".*?</footer>)', idx, re.DOTALL)
wa_m      = re.search(r'(<!-- ── WhatsApp Button ─+.*?</a>)', idx, re.DOTALL)
ki_m      = re.search(r'(<!-- ── KK KI-Agent Widget ─+.*?<!-- /KK KI-Agent Widget -->)', idx, re.DOTALL)
ck_m      = re.search(r'(<!-- ── Cookie Banner ─+.*?</script>)', idx, re.DOTALL)
gsap_m    = re.search(r'(<!-- ── GSAP Animations ─+.*?</script>)', idx, re.DOTALL)

new_header  = header_m.group(1)
new_mobnav  = mobnav_m.group(1)
new_footer  = footer_m.group(1)
new_wa      = wa_m.group(1)
new_ki      = ki_m.group(1)
new_ck      = ck_m.group(1)

# Simplified GSAP for subpages (no hero-specific selectors)
new_gsap = '''<!-- ── GSAP Animations ─────────────────────────────────────── -->
<script>
(function () {
  if (typeof gsap === 'undefined') return;
  gsap.registerPlugin(ScrollTrigger);
  function once(trigger, startPos) {
    return { trigger: trigger, start: startPos || 'top 88%', once: true };
  }
  gsap.utils.toArray('.section-header').forEach(function(el) {
    gsap.fromTo(el,
      { opacity: 0, y: 14 },
      { opacity: 1, y: 0, duration: 0.55, ease: 'power2.out',
        scrollTrigger: once(el, 'top 90%') }
    );
  });
  gsap.utils.toArray('.hero-title, .hero-lead, .hero-ctas').forEach(function(el, i) {
    gsap.fromTo(el,
      { opacity: 0, y: 20 },
      { opacity: 1, y: 0, duration: 0.6, ease: 'power2.out', delay: i * 0.1 }
    );
  });
})();
</script>'''

FONTS_GSAP = '''
  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap" rel="stylesheet">

  <!-- Favicon -->
  <link rel="apple-touch-icon" href="apple-touch-icon.png">

  <!-- GSAP -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>'''

PAGES = [
    'bauendreinigung-friedrichshafen.html',
    'bueroreinigung-friedrichshafen.html',
    'datenschutz.html',
    'faq.html',
    'gebaeudereinigung-friedrichshafen.html',
    'grundreinigung-friedrichshafen.html',
    'hotelreinigung-friedrichshafen.html',
    'impressum.html',
    'kontakt.html',
    'leistungen.html',
    'polsterreinigung-friedrichshafen.html',
    'praxisreinigung-friedrichshafen.html',
    'reinigungsfirma-lindau.html',
    'reinigungsfirma-ravensburg.html',
    'schulreinigung-friedrichshafen.html',
    'ueber-uns.html',
    'unterhaltsreinigung-friedrichshafen.html',
]

TAIL = '\n\n' + new_wa + '\n\n' + new_ki + '\n\n' + new_ck + '\n\n' + new_gsap + '\n</body>\n</html>'

for page in PAGES:
    path = os.path.join(REPO, page)
    if not os.path.exists(path):
        print(f'SKIP (missing): {page}')
        continue

    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()

    # 1. Remove kk-tw.min.css
    c = re.sub(r'\n?\s*<link\s+rel=["\']stylesheet["\']\s+href=["\']kk-tw\.min\.css["\'][^>]*>', '', c)

    # 2. Remove script.js reference
    c = re.sub(r'\n?\s*<script\s+src=["\']script\.js["\'][^>]*></script>', '', c)

    # 3. Add fonts + GSAP after style.css (only if not already present)
    if 'fonts.googleapis.com' not in c:
        c = c.replace(
            '<link rel="stylesheet" href="style.css">',
            '<link rel="stylesheet" href="style.css">' + FONTS_GSAP
        )

    # 4. Fix body tag
    c = re.sub(r'<body[^>]*>', '<body>', c)

    # 5a. Replace old header
    c = re.sub(
        r'(?s)(<!--\s*Header\s*-->\s*)?<header[^>]*>.*?</header>',
        new_header,
        c, count=1
    )

    # 5b. Strip ALL mobile-nav blocks (old and any previously injected)
    c = re.sub(r'(?s)\s*<!-- Mobile Nav -->\s*<nav class="mobile-nav"[^>]*>.*?</nav>', '', c)

    # 5c. Reinsert the correct mobile-nav once, right after </header>
    c = c.replace('</header>', '</header>\n\n' + new_mobnav, 1)

    # 6. Remove aria-current="page" from subpage headers (homepage-specific)
    c = c.replace(' aria-current="page"', '')

    # 7. Fix <main> tag (remove class attributes)
    c = re.sub(r'<main\b[^>]*>', '<main>', c)

    # 8. Replace footer + everything after with new footer + widgets
    c = re.sub(r'(?s)<footer\b.*\Z', new_footer + TAIL, c)

    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(c)

    print(f'OK: {page}')

print('\nAll done.')
