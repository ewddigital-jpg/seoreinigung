#!/usr/bin/env python3
import re
import glob

# HTML-Template Header (mit Link zur style.css)
def get_header_template(title, description, keywords, canonical):
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <meta name="keywords" content="{keywords}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{canonical}">
    <link rel="icon" type="image/x-icon" href="favicon.ico">
    <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
    <link rel="stylesheet" href="style.css">
</head>
<body>
'''

# Footer Template
FOOTER_TEMPLATE = '''    <footer>
        <div class="container">
            <div class="footer-main">
                <div class="footer-brand">
                    <a href="https://kkreinigung.com/index.html" class="logo">
                        <img src="apple-touch-icon.png" alt="K.K. Reinigung Logo">
                        <div class="logo-text">
                            <span class="brand-name" style="color:#fff">K.K. Reinigung</span>
                            <span class="brand-sub">Gebäudereinigung & Reinigungsservice</span>
                        </div>
                    </a>
                    <p>Ihre Reinigungsfirma für Gebäudereinigung, Büroreinigung, Unterhaltsreinigung, Sonderreinigung und Bauendreinigung in Friedrichshafen und rund um den Bodensee.</p>
                </div>
                <div class="footer-col">
                    <h4>Navigation</h4>
                    <ul>
                        <li><a href="https://kkreinigung.com/index.html">Start</a></li>
                        <li><a href="leistungen.html">Leistungen</a></li>
                        <li><a href="ueber-uns.html">Über uns</a></li>
                        <li><a href="kontakt.html">Kontakt</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>Leistungen</h4>
                    <ul>
                        <li><a href="gebaeudereinigung-friedrichshafen.html">Gebäudereinigung Friedrichshafen</a></li>
                        <li><a href="bueroreinigung-friedrichshafen.html">Büroreinigung Friedrichshafen</a></li>
                        <li><a href="unterhaltsreinigung-friedrichshafen.html">Unterhaltsreinigung Friedrichshafen</a></li>
                        <li><a href="leistungen.html#sonderreinigung">Sonderreinigung</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>Kontakt</h4>
                    <ul>
                        <li><a href="tel:01778740889">0177 8740889</a></li>
                        <li><a href="mailto:kurdi.reinigungsservice@gmail.com">kurdi.reinigungsservice@gmail.com</a></li>
                        <li><a href="kontakt.html#kontaktformular">Zum Kontaktformular</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>© 2025 K.K. Reinigung Friedrichshafen</p>
                <div class="footer-legal">
                    <a href="impressum.html">Impressum</a>
                    <a href="datenschutz.html">Datenschutz</a>
                </div>
            </div>
        </div>
    </footer>

    <script data-cfasync="false" src="/cdn-cgi/scripts/5c5dd728/cloudflare-static/email-decode.min.js"></script>
    <script>
        function toggleMenu(btn) {
            const nav = document.getElementById('nav');
            const isActive = nav.classList.toggle('active');
            btn.setAttribute('aria-expanded', isActive);
            btn.textContent = isActive ? '✕' : '☰';
        }
    </script>
</body>
</html>'''

# Funktion zum Reparieren von Links
def fix_links(content):
    # Repariere <a https:// zu <a href="https://
    content = re.sub(r'<a\s+https://', '<a href="https://', content)
    # Repariere <a href zu <a href="
    content = re.sub(r'<a\s+href\s+https://', '<a href="https://', content)
    return content

print("Starte Reparatur aller HTML-Dateien...")
print("=" * 60)

# Alle HTML-Dateien finden
html_files = ['index.html', 'kontakt.html', 'leistungen.html', 'ueber-uns.html',
              'bueroreinigung-friedrichshafen.html', 'gebaeudereinigung-friedrichshafen.html',
              'unterhaltsreinigung-friedrichshafen.html']

for filename in html_files:
    try:
        print(f"Repariere {filename}...")
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extrahiere Meta-Infos
        title_match = re.search(r'<title>(.*?)</title>', content)
        desc_match = re.search(r'<meta name="description" content="(.*?)"', content)
        keywords_match = re.search(r'<meta name="keywords" content="(.*?)"', content)
        canonical_match = re.search(r'<link rel="canonical" href="(.*?)"', content)
        
        title = title_match.group(1) if title_match else "K.K. Reinigung"
        description = desc_match.group(1) if desc_match else ""
        keywords = keywords_match.group(1) if keywords_match else ""
        canonical = canonical_match.group(1) if canonical_match else "https://kkreinigung.com/"
        
        # Extrahiere Body-Content (zwischen <body> und </body>)
        body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL)
        if not body_match:
            print(f"  ⚠️  Konnte Body nicht finden in {filename}")
            continue
            
        body_content = body_match.group(1)
        
        # Entferne altes Footer und Script
        body_content = re.sub(r'<footer>.*?</footer>', '', body_content, flags=re.DOTALL)
        body_content = re.sub(r'<script[^>]*>.*?</script>', '', body_content, flags=re.DOTALL)
        
        # Repariere Links
        body_content = fix_links(body_content)
        
        # Baue neue Datei zusammen
        new_content = get_header_template(title, description, keywords, canonical)
        new_content += body_content
        new_content += FOOTER_TEMPLATE
        
        # Schreibe reparierte Datei
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"  ✓ {filename} repariert")
        
    except Exception as e:
        print(f"  ✗ Fehler bei {filename}: {e}")

print("=" * 60)
print("Alle Dateien wurden repariert!")
