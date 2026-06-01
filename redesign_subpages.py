"""
Replaces <main>...</main> content on all 17 subpages with new style.css-based design.
Run once, then run update_pages.py to sync header/footer/widgets.
"""
import re, os

REPO = r'C:\Users\danie\seoreinigung-repo'

# ── SVG helpers ──────────────────────────────────────────────────
PHONE_SVG = '<svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true" style="flex-shrink:0"><path stroke-linecap="round" stroke-linejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 7V5z"/></svg>'
WA_SVG = '<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true" style="flex-shrink:0"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>'

# ── Component helpers ────────────────────────────────────────────
def bc(crumbs):
    parts = []
    for i,(href,label) in enumerate(crumbs):
        if i == len(crumbs)-1:
            parts.append(f'<span>{label}</span>')
        else:
            parts.append(f'<a href="{href}">{label}</a><span aria-hidden="true">›</span>')
    return f'''<div class="breadcrumb-wrap">
  <div class="container">
    <nav class="breadcrumb" aria-label="Breadcrumb">{''.join(parts)}</nav>
  </div>
</div>'''

def ctas(wa_text):
    return f'''<div class="subpage-hero-ctas">
      <a href="tel:01778740889" class="btn btn-primary btn-lg">{PHONE_SVG} 0177 8740889</a>
      <a href="https://wa.me/491778740889?text={wa_text}" class="btn btn-success btn-lg">{WA_SVG} WhatsApp</a>
    </div>'''

def form(emoji, h2, subject, placeholder):
    return f'''<div class="hero-form-card">
        <span class="card-emoji">{emoji}</span>
        <h2 style="font-family:var(--font-body);font-size:1.25rem;font-weight:700;color:var(--color-primary-dark);margin-bottom:18px">{h2}</h2>
        <form action="https://formspree.io/f/xvzgeldw" method="POST">
          <div class="form-group"><label>Name *</label><input type="text" name="name" required placeholder="Ihr Name"></div>
          <div class="form-group"><label>Telefon oder E-Mail *</label><input type="text" name="contact" required placeholder="Wie können wir Sie erreichen?"></div>
          <div class="form-group"><label>Kurze Beschreibung</label><textarea name="message" rows="3" placeholder="{placeholder}"></textarea></div>
          <input type="hidden" name="_subject" value="{subject}">
          <button type="submit" class="btn btn-cta" style="width:100%;justify-content:center;margin-top:8px">Anfrage senden</button>
          <p style="font-size:.75rem;color:var(--color-text-muted);text-align:center;margin-top:8px">Kostenlos &amp; unverbindlich. Rückmeldung am selben Tag.</p>
        </form>
      </div>'''

def checks(items):
    li = '\n'.join(f'          <li>{x}</li>' for x in items)
    return f'<ul class="check-list">\n{li}\n        </ul>'

def svc_grid(cards):
    divs = '\n'.join(f'      <div class="service-card"><span class="card-emoji">{e}</span><h3>{t}</h3><p>{d}</p></div>' for e,t,d in cards)
    return f'<div class="service-grid">\n{divs}\n    </div>'

def uc_grid(cases):
    divs = '\n'.join(f'      <div class="use-case-card"><span style="font-size:1.5rem;display:block;margin-bottom:10px">{e}</span><h3 style="font-size:1rem;font-weight:700;color:var(--color-primary-dark);margin-bottom:6px">{t}</h3><p style="font-size:.9rem;color:var(--color-text-secondary);line-height:1.6">{d}</p></div>' for e,t,d in cases)
    return f'<div class="use-case-grid">\n{divs}\n    </div>'

def faq(items):
    divs = '\n'.join(f'      <div class="sp-faq-item"><h3 style="font-size:1rem;font-weight:700;color:var(--color-primary-dark);margin-bottom:8px">{q}</h3><p style="font-size:.9375rem;color:var(--color-text-secondary);line-height:1.7;margin:0">{a}</p></div>' for q,a in items)
    return f'<div class="sp-faq-list">\n{divs}\n    </div>'

def cta_sec(h2, text):
    return f'''<section class="cta-section">
  <div class="container"><div class="cta-inner">
    <h2>{h2}</h2><p>{text}</p>
    <div class="cta-btns">
      <a href="kontakt" class="btn btn-cta btn-lg">Kostenloses Angebot anfordern</a>
      <a href="tel:01778740889" class="btn btn-white btn-lg">{PHONE_SVG} 0177 8740889</a>
    </div>
    <p class="cta-note">Montag bis Samstag, 7–20 Uhr</p>
  </div></div>
</section>'''

def pills(items):
    links = '\n    '.join(f'<a href="{h}" class="region-pill">{l}</a>' for h,l in items)
    return f'''<section class="section" style="padding:clamp(28px,3.5vw,44px) 0">
  <div class="container">
    <h3 style="font-family:var(--font-body);font-size:1rem;font-weight:700;color:var(--color-text-secondary);margin-bottom:16px">Weitere Leistungen</h3>
    <div class="region-pills">
    {links}
    </div>
  </div>
</section>'''

# ── Default related pills sets ───────────────────────────────────
ALL_SERVICES = [
    ('gebaeudereinigung-friedrichshafen','Gebäudereinigung'),
    ('unterhaltsreinigung-friedrichshafen','Unterhaltsreinigung'),
    ('bueroreinigung-friedrichshafen','Büroreinigung'),
    ('bauendreinigung-friedrichshafen','Bauendreinigung'),
    ('grundreinigung-friedrichshafen','Grundreinigung'),
    ('praxisreinigung-friedrichshafen','Praxisreinigung'),
    ('hotelreinigung-friedrichshafen','Hotelreinigung'),
    ('schulreinigung-friedrichshafen','Schulreinigung'),
    ('polsterreinigung-friedrichshafen','Polsterreinigung'),
    ('reinigungsfirma-lindau','Reinigungsfirma Lindau'),
    ('reinigungsfirma-ravensburg','Reinigungsfirma Ravensburg'),
]

def related(exclude=None):
    return [(h,l) for h,l in ALL_SERVICES if (exclude and exclude not in h) or not exclude]

# ── Page content definitions ─────────────────────────────────────

def page_bueroreinigung():
    return f'''<main>
{bc([('/','Startseite'),('leistungen','Leistungen'),(None,'Büroreinigung Friedrichshafen')])}
<section class="subpage-hero">
  <div class="container">
    <div class="subpage-hero-grid">
      <div>
        <p class="eyebrow">Büroreinigung Friedrichshafen</p>
        <h1>Sauberes Büro,<br><em>motiviertes Team.</em></h1>
        <p class="subpage-hero-lead">Ihre Mitarbeiter sollen sich wohlfühlen. K.K. Reinigung übernimmt die Büroreinigung diskret, pünktlich und im laufenden Betrieb oder außerhalb Ihrer Arbeitszeiten.</p>
        {checks(['Reinigung morgens, abends oder während des Betriebs','Schreibtische, Böden, Sanitäranlagen, Küche &amp; Besprechungsräume','Flexible Intervalle: wöchentlich, zweiwöchentlich oder individuell','Festes Team – kein ständig wechselndes Personal'])}
        {ctas('Hallo%2C%20ich%20ben%C3%B6tige%20B%C3%BCroreinigung%20in%20Friedrichshafen.')}
      </div>
      {form('💼','Büroreinigung anfragen','Büroreinigung Anfrage – kkreinigung.com','z.B. Büro 200m², wöchentliche Reinigung, Friedrichshafen')}
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Büroreinigung – was ist enthalten?</h2></div>
    {svc_grid([('💼','Arbeitsplätze &amp; Schreibtische','Abwischen, Staubbeseitigung, Bildschirme und Oberflächen – ohne Ihre Unterlagen zu verschieben.'),('🚿','Sanitäranlagen','Toiletten, Waschbecken, Spiegel und Böden – gründlich desinfiziert und gereinigt.'),('🍽️','Küche &amp; Pausenraum','Arbeitsflächen, Küchengeräte außen, Spüle und Böden – damit der Pausenraum einladend bleibt.'),('🏛️','Besprechungsräume','Tische, Stühle, Böden – für einen gepflegten Eindruck bei jedem Meeting.'),('🚪','Empfang &amp; Eingang','Der erste Eindruck zählt – sauberer Empfangsbereich für Kunden und Besucher.'),('🧹','Böden &amp; Flure','Saugen, wischen, polieren – je nach Bodenbelag und Anforderung.')])}
  </div>
</section>
<section class="section" style="background:var(--color-surface)">
  <div class="container">
    <div class="section-header"><h2>Wer unsere Büroreinigung nutzt</h2></div>
    {uc_grid([('🏢','Büros &amp; Kanzleien','Anwaltskanzleien, Steuerbüros, Agenturen – saubere Arbeitsumgebung für Ihr Team und Ihre Kunden.'),('🏥','Arztpraxen &amp; Praxen','Hygiene hat hier oberste Priorität – wir reinigen nach Ihren Anforderungen, diskret und gründlich.'),('🏪','Kleinbetriebe &amp; Gewerbe','Handwerksbetriebe, kleine Unternehmen – flexible Lösung ohne lange Vertragslaufzeiten.')])}
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Häufige Fragen</h2></div>
    {faq([('Was kostet Büroreinigung in Friedrichshafen?','Die Kosten richten sich nach Fläche, Reinigungsumfang und Häufigkeit. Für ein Büro mit 100 m² und wöchentlicher Reinigung beginnen die Preise ab ca. 120–200 € pro Monat. Wir erstellen ein individuelles Angebot.'),('Wann reinigen Sie das Büro?','Wir richten uns nach Ihren Arbeitszeiten – morgens vor Arbeitsbeginn, abends nach Feierabend oder auch während des Betriebs. Wir sind flexibel.'),('Wie oft sollte ein Büro gereinigt werden?','Bei normaler Nutzung empfehlen wir wöchentliche Reinigung. Intensiv genutzte Büros oder Praxen profitieren von täglicher oder zweimaliger Wochenreinigung.'),('Bringen Sie eigene Reinigungsmittel mit?','Ja, wir kommen mit allem Material und Geräten. Auf Wunsch verwenden wir auch umweltfreundliche Reinigungsmittel.'),('Gibt es einen festen Ansprechpartner?','Ja. Sie haben bei uns immer denselben Ansprechpartner und nach Möglichkeit dasselbe Reinigungsteam.')])}
  </div>
</section>
{cta_sec('Büroreinigung Friedrichshafen anfragen','Schildern Sie uns kurz Ihren Bedarf – wir melden uns noch am selben Tag.')}
{pills([(h,l) for h,l in related('bueroreinigung')][:8])}
</main>'''

def page_bauendreinigung():
    return f'''<main>
{bc([('/','Startseite'),('leistungen','Leistungen'),(None,'Bauendreinigung Friedrichshafen')])}
<section class="subpage-hero">
  <div class="container">
    <div class="subpage-hero-grid">
      <div>
        <p class="eyebrow">Bauendreinigung Friedrichshafen</p>
        <h1>Übergabereif –<br><em>im ersten Einsatz.</em></h1>
        <p class="subpage-hero-lead">Nach dem Bau kommt die Übergabe. K.K. Reinigung macht Ihr Objekt termingerecht übergabereif – Baustaub, Kalkflecken, Folien, Fenster: vollständig und ohne Nacharbeit.</p>
        {checks(['Neubau, Umbau und Renovierung aller Größen','Baustaub, Kalkflecken, Klebereste, Folien entfernen','Fenster, Böden, Sanitäranlagen und Innenräume','Termingerecht – pünktlich zur Übergabe'])}
        {ctas('Hallo%2C%20ich%20ben%C3%B6tige%20Bauendreinigung%20in%20Friedrichshafen.')}
      </div>
      {form('🏗️','Bauendreinigung anfragen','Bauendreinigung Anfrage – kkreinigung.com','z.B. Neubau 300m², Übergabe in 2 Wochen, Friedrichshafen')}
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Bauendreinigung – was ist enthalten?</h2></div>
    {svc_grid([('🏗️','Baustaub &amp; Grobschmutz','Böden, Wände, Decken – vollständige Entstaubung aller Flächen nach dem Bau.'),('🪟','Fenster &amp; Rahmen','Fenster innen und außen, Rahmen, Fensterbänke – streifenfrei und glänzend.'),('🧱','Böden &amp; Fliesen','Kalkflecken, Farbreste und Bauschmutz entfernen – je nach Belag mit Spezialreiniger.'),('🚿','Sanitäranlagen','Badezimmer, Toiletten, Waschbecken und Wannen – sauber für die Erstbenutzung.'),('🚪','Türen &amp; Beschläge','Klebereste von Folien entfernen, Türen und Griffe reinigen und polieren.'),('✅','Detailreinigung','Steckdosen, Schalter, Lichtschutzgitter, Heizungen – jedes Detail sauber.')])}
  </div>
</section>
<section class="section" style="background:var(--color-surface)">
  <div class="container">
    <div class="section-header"><h2>Wer Bauendreinigung beauftragt</h2></div>
    {uc_grid([('🏘️','Neubau &amp; Erstbezug','Bauträger, Architekten und Eigentümer – übergabereif für den ersten Mieter oder Käufer.'),('🔨','Umbau &amp; Sanierung','Renovierungen, Umbauten, Kernsanierungen – nach dem Handwerker kommt unser Team.'),('🏢','Gewerbe &amp; Industrie','Bürogebäude, Produktionshallen, Praxen – auch bei großen Objekten termingerecht.')])}
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Häufige Fragen</h2></div>
    {faq([('Was kostet eine Bauendreinigung?','Der Preis richtet sich nach Quadratmeterzahl und Verschmutzungsgrad. Wir erstellen nach kurzer Beschreibung oder Besichtigung ein festes Angebot.'),('Wie schnell kann die Reinigung durchgeführt werden?','Wir sind flexibel und können kurzfristig reagieren. Kontaktieren Sie uns mit Ihrem Wunschtermin – wir versuchen, diesen zu erfüllen.'),('Bringen Sie alle Geräte und Reinigungsmittel mit?','Ja, wir kommen mit allem Notwendigen. Sie müssen nichts bereitstellen.'),('Wird der Bauschutt auch entsorgt?','Die Bauendreinigung umfasst das Reinigen, nicht die Entsorgung von Bauschutt. Kleinstmengen an Bauschmutz werden von uns entsorgt.'),('Können Sie auch kurzfristig bei Übergaben helfen?','Ja. Teilen Sie uns rechtzeitig den Übergabetermin mit, und wir koordinieren den Einsatz.')])}
  </div>
</section>
{cta_sec('Bauendreinigung Friedrichshafen anfragen','Teilen Sie uns Ihr Objekt und den Übergabetermin mit – wir planen den Einsatz.')}
{pills([(h,l) for h,l in related('bauendreinigung')][:8])}
</main>'''

def page_gebaeudereinigung():
    return f'''<main>
{bc([('/','Startseite'),('leistungen','Leistungen'),(None,'Gebäudereinigung Friedrichshafen')])}
<section class="subpage-hero">
  <div class="container">
    <div class="subpage-hero-grid">
      <div>
        <p class="eyebrow">Gebäudereinigung Friedrichshafen</p>
        <h1>Professionelle Reinigung –<br><em>für jede Immobilie.</em></h1>
        <p class="subpage-hero-lead">K.K. Reinigung reinigt Bürogebäude, Wohnanlagen, Treppenhäuser und Gewerbeimmobilien im Bodenseekreis – zuverlässig, termingerecht und zu klaren Festpreisen.</p>
        {checks(['Bürogebäude, Praxen und Gewerbeimmobilien','Treppenhäuser und Gemeinschaftsflächen','Außenanlagen, Eingänge und Parkflächen','Langfristige Partnerschaft mit festem Ansprechpartner'])}
        {ctas('Hallo%2C%20ich%20ben%C3%B6tige%20Geb%C3%A4udereinigung%20in%20Friedrichshafen.')}
      </div>
      {form('🏢','Gebäudereinigung anfragen','Gebäudereinigung Anfrage – kkreinigung.com','z.B. Bürogebäude 500m², monatliche Reinigung, Friedrichshafen')}
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Gebäudereinigung – unsere Leistungen</h2></div>
    {svc_grid([('🏢','Bürogebäude &amp; Gewerbe','Alle Etagen, Böden, Sanitäranlagen und Gemeinschaftsflächen – regelmäßig und zuverlässig.'),('🏠','Treppenhäuser','Treppenläufe, Handläufe, Briefkästen, Fensterflächen – sauber für Mieter und Besucher.'),('🪟','Eingangsbereiche','Glasfronten, Türen, Briefkastenanlage – der erste Eindruck zählt.'),('🌿','Außenanlagen','Gehwege, Parkflächen, Eingänge – gepflegt und sicher.'),('🚿','Sanitärräume','Gemeinschaftstoiletten und -duschen in Gewerbeobjekten – hygienisch desinfiziert.'),('🔑','Hausverwaltungen','Regelmäßige Berichterstellung auf Wunsch, direkter Kontakt für Sonderbeauftragungen.')])}
  </div>
</section>
<section class="section" style="background:var(--color-surface)">
  <div class="container">
    <div class="section-header"><h2>Für wen eignet sich Gebäudereinigung?</h2></div>
    {uc_grid([('🏛️','Hausverwaltungen','Zuverlässiger Partner für Treppenhäuser, Außenanlagen und Gemeinschaftsflächen in Wohnanlagen.'),('🏗️','Gewerbeobjekte','Bürogebäude, Praxen, Agenturen – regelmäßige Reinigung für professionelles Erscheinungsbild.'),('🏘️','Eigentümergemeinschaften','WEGs und Eigentümer – saubere Gemeinschaftsflächen ohne eigenen Aufwand.')])}
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Häufige Fragen</h2></div>
    {faq([('Was kostet Gebäudereinigung in Friedrichshafen?','Die Kosten hängen von Objektgröße, Reinigungsumfang und Häufigkeit ab. Wir erstellen ein individuelles Angebot nach Besichtigung oder kurzer Beschreibung.'),('Reinigen Sie auch Treppenhäuser für Hausverwaltungen?','Ja. Treppenhausreinigung ist ein Schwerpunkt unserer Arbeit. Wir übernehmen regelmäßige Reinigungsintervalle und stimmen uns direkt mit der Hausverwaltung ab.'),('Wie oft wird ein Gebäude gereinigt?','Je nach Nutzungsintensität empfehlen wir wöchentliche bis zweiwöchentliche Reinigung. Für weniger frequentierte Bereiche auch monatlich.'),('Sind Sie versichert?','Ja, wir sind haftpflichtversichert. Auf Anfrage stellen wir entsprechende Nachweise bereit.'),('Gibt es einen festen Ansprechpartner?','Ja – direkter Kontakt zu Khaled Kurdi, keine Vermittlung über eine Zentrale.')])}
  </div>
</section>
{cta_sec('Gebäudereinigung Friedrichshafen anfragen','Beschreiben Sie kurz Ihr Objekt – wir melden uns am selben Tag.')}
{pills([(h,l) for h,l in related('gebaeudereinigung')][:8])}
</main>'''

def page_grundreinigung():
    return f'''<main>
{bc([('/','Startseite'),('leistungen','Leistungen'),(None,'Grundreinigung Friedrichshafen')])}
<section class="subpage-hero">
  <div class="container">
    <div class="subpage-hero-grid">
      <div>
        <p class="eyebrow">Grundreinigung Friedrichshafen</p>
        <h1>Tiefenreinigung –<br><em>von Grund auf sauber.</em></h1>
        <p class="subpage-hero-lead">Die Grundreinigung geht weiter als normale Unterhaltsreinigung: Hartnäckige Verschmutzungen, Kalkablagerungen, Fettbeläge und versteckte Bereiche werden gründlich behandelt.</p>
        {checks(['Einmalig oder saisonal – flexibel buchbar','Böden tiefenreinigen, imprägnieren und polieren','Küchengeräte, Herde, Dunstabzüge entfetten','Kalkablagerungen in Sanitäranlagen entfernen'])}
        {ctas('Hallo%2C%20ich%20ben%C3%B6tige%20Grundreinigung%20in%20Friedrichshafen.')}
      </div>
      {form('🧽','Grundreinigung anfragen','Grundreinigung Anfrage – kkreinigung.com','z.B. Büroküche + Sanitäranlagen, 150m², einmalig')}
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Grundreinigung – was ist enthalten?</h2></div>
    {svc_grid([('🧱','Böden tiefenreinigen','Maschinelles Schrubbern, Entfernen von Belägen, Imprägnierung oder Polierung je nach Bodenart.'),('🚿','Sanitäranlagen entkalken','Kalkablagerungen, Verfärbungen und Schimmel in Waschbecken, Toiletten, Duschen und Badewannen.'),('🍳','Küche &amp; Geräte','Herde, Backöfen, Dunstabzüge, Kühlschränke außen – Fett und Verkrustungen restlos entfernen.'),('🪟','Fenster &amp; Glasflächen','Innen- und außen, Fensterbänke, Rahmen – für klare Sicht.'),('🚪','Türen &amp; Griffe','Türen abwischen, Fingerabdrücke, Klebereste und Schmutzränder entfernen.'),('📦','Regale &amp; Versteckte Bereiche','Hinter Möbeln, unter Geräten, in Ecken – Bereiche die bei der Unterhaltsreinigung übergangen werden.')])}
  </div>
</section>
<section class="section" style="background:var(--color-surface)">
  <div class="container">
    <div class="section-header"><h2>Wann ist eine Grundreinigung sinnvoll?</h2></div>
    {uc_grid([('📅','Saisonal &amp; jährlich','Frühjahrsputz, Jahresreinigung oder vor wichtigen Terminen – einmalige Tiefenreinigung als Frischekur.'),('🔄','Bei Mieterwechsel','Wohnungen, Büros oder Gewerbeflächen – übergabereif nach Mieterwechsel oder Auszug.'),('🏗️','Nach Umbauarbeiten','Wenn Unterhaltsreinigung nicht ausreicht – nach Renovierungen oder Restaurierungen.')])}
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Häufige Fragen</h2></div>
    {faq([('Was ist der Unterschied zur normalen Reinigung?','Die Grundreinigung ist intensiver und gründlicher. Bereiche, die normalerweise nicht erreicht werden, Kalkflecken, Fettbeläge und hartnäckige Verschmutzungen stehen im Fokus.'),('Wie lange dauert eine Grundreinigung?','Das hängt von Größe und Zustand des Objekts ab. Typischerweise dauert es 2–5 Stunden für ein Büro mit 200 m².'),('Wie oft sollte eine Grundreinigung durchgeführt werden?','Je nach Intensität der Nutzung empfehlen wir ein- bis zweimal jährlich.'),('Kann ich die Grundreinigung mit der Unterhaltsreinigung kombinieren?','Ja. Viele unserer Kunden kombinieren beides: regelmäßige Unterhaltsreinigung plus halbjährliche Grundreinigung.'),('Was kostet eine Grundreinigung?','Der Preis richtet sich nach Fläche und Umfang. Kontaktieren Sie uns für ein individuelles Angebot.')])}
  </div>
</section>
{cta_sec('Grundreinigung Friedrichshafen anfragen','Teilen Sie uns die Fläche und den gewünschten Umfang mit – Angebot am selben Tag.')}
{pills([(h,l) for h,l in related('grundreinigung')][:8])}
</main>'''

def page_hotelreinigung():
    return f'''<main>
{bc([('/','Startseite'),('leistungen','Leistungen'),(None,'Hotelreinigung Friedrichshafen')])}
<section class="subpage-hero">
  <div class="container">
    <div class="subpage-hero-grid">
      <div>
        <p class="eyebrow">Hotelreinigung Friedrichshafen</p>
        <h1>Zimmer, die beeindrucken –<br><em>jeden Gast, jeden Tag.</em></h1>
        <p class="subpage-hero-lead">Sauberkeit ist im Hotel kein Hygienefaktor – sie ist Gästeerlebnis. K.K. Reinigung reinigt Zimmer, öffentliche Bereiche und Frühstücksraum diskret, schnell und zuverlässig.</p>
        {checks(['Zimmerreinigung nach Check-out und für Langzeitgäste','Frühstücksraum, Lobby und öffentliche Bereiche','Flexible Einsatzzeiten – angepasst an Check-in/Check-out','Festes Team für gleichbleibende Qualität'])}
        {ctas('Hallo%2C%20ich%20ben%C3%B6tige%20Hotelreinigung%20in%20Friedrichshafen.')}
      </div>
      {form('🏨','Hotelreinigung anfragen','Hotelreinigung Anfrage – kkreinigung.com','z.B. Boutique-Hotel 20 Zimmer, tägliche Reinigung, Friedrichshafen')}
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Hotelreinigung – was ist enthalten?</h2></div>
    {svc_grid([('🛏️','Zimmerreinigung','Betten beziehen, Staubwischen, Böden reinigen, Sanitäranlagen desinfizieren – nach Check-out und für Stayover.'),('🚿','Badezimmer','Waschbecken, Dusche/Badewanne, Toilette, Spiegel, Böden – nach jedem Gast hygienisch sauber.'),('☕','Frühstücksraum','Tische, Stühle, Buffetflächen, Böden – täglich gereinigt, bereit für den nächsten Morgen.'),('🛎️','Lobby &amp; Empfang','Eingangsbereich, Rezeption, Wartebereich – sauber und einladend für jeden Ankommenden.'),('🏊','Gemeinschaftsflächen','Flure, Treppenhäuser, Aufzüge, Wellnessbereiche – regelmäßig gereinigt und gepflegt.'),('🧺','Wäschewechsel','Bettwäsche und Handtücher wechseln, Verbrauchsmaterial auffüllen auf Wunsch.')])}
  </div>
</section>
<section class="section" style="background:var(--color-surface)">
  <div class="container">
    <div class="section-header"><h2>Für wen eignet sich Hotelreinigung?</h2></div>
    {uc_grid([('🏨','Hotels &amp; Pensionen','Kleine bis mittelgroße Häuser am Bodensee – verlässliche Zimmerreinigung für zufriedene Gäste.'),('🏠','Ferienwohnungen','Regelmäßige Reinigung und Wäschewechsel zwischen Buchungen – auch kurzfristig.'),('🏢','Gästehäuser &amp; Seminarhäuser','Gruppenunterkünfte und Seminarhotels – Zimmer und Veranstaltungsräume.')])}
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Häufige Fragen</h2></div>
    {faq([('Können Sie kurzfristig einspringen?','Ja. Teilen Sie uns möglichst früh mit, wann Sie unsere Unterstützung brauchen. Wir versuchen, flexibel zu reagieren.'),('Bringen Sie Ihre eigenen Reinigungsmittel mit?','Ja. Wenn Sie bestimmte Produkte bevorzugen, stimmen wir uns ab.'),('Reinigen Sie auch Ferienwohnungen zwischen Buchungen?','Ja. Wir koordinieren die Reinigung nach Check-out und bereiten die Unterkunft für den nächsten Gast vor.'),('Wie wird die Qualität sichergestellt?','Wir arbeiten mit einem festen Team, das Ihr Haus kennt. Auf Wunsch gibt es eine Checkliste je Zimmer.'),('Was kostet Hotelreinigung?','Der Preis richtet sich nach Zimmeranzahl, Reinigungsumfang und Häufigkeit. Wir erstellen gerne ein Angebot.')])}
  </div>
</section>
{cta_sec('Hotelreinigung Friedrichshafen anfragen','Erzählen Sie uns von Ihrem Betrieb – wir senden Ihnen ein passendes Angebot.')}
{pills([(h,l) for h,l in related('hotelreinigung')][:8])}
</main>'''

def page_polsterreinigung():
    return f'''<main>
{bc([('/','Startseite'),('leistungen','Leistungen'),(None,'Polsterreinigung Friedrichshafen')])}
<section class="subpage-hero">
  <div class="container">
    <div class="subpage-hero-grid">
      <div>
        <p class="eyebrow">Polsterreinigung Friedrichshafen</p>
        <h1>Polster, Sofas, Stühle –<br><em>wie neu gereinigt.</em></h1>
        <p class="subpage-hero-lead">Polster nehmen Staub, Gerüche und Flecken auf, die normale Reinigung nicht erfasst. K.K. Reinigung reinigt Polstermöbel in Büros, Hotels und öffentlichen Einrichtungen gründlich und schonend.</p>
        {checks(['Sofas, Sessel, Bürostühle und Konferenzstühle','Fleckenentfernung und Geruchsneutralisierung','Schonende Reinigung – materialgerecht','Keine langen Trocknungszeiten'])}
        {ctas('Hallo%2C%20ich%20ben%C3%B6tige%20Polsterreinigung%20in%20Friedrichshafen.')}
      </div>
      {form('🛋️','Polsterreinigung anfragen','Polsterreinigung Anfrage – kkreinigung.com','z.B. 3 Konferenzstühle + 2 Sofas im Empfang, Friedrichshafen')}
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Polsterreinigung – was ist enthalten?</h2></div>
    {svc_grid([('🛋️','Sofas &amp; Sessel','Aufpolstern, Entstauben und Tiefenreinigung – für frisch wirkende Möbel im Büro oder Hotel.'),('🪑','Bürostühle &amp; Konferenzstühle','Sitzflächen und Rückenlehnen reinigen, Flecken entfernen – für repräsentative Besprechungsräume.'),('💨','Geruchsneutralisierung','Unangenehme Gerüche durch spezielle Behandlung eliminieren, nicht nur überdecken.'),('🔴','Fleckenentfernung','Kaffee, Tinte, Fett – gezieltes Vorbehandeln und Tiefenreinigung je nach Stoff.'),('🧵','Materialgerechte Behandlung','Stoff, Kunstleder oder Mischgewebe – wir passen das Verfahren an Ihr Material an.'),('🌿','Hygienische Tiefenreinigung','Allergene, Milben und Keime reduzieren – wichtig für Büros mit Gesundheitsanspruch.')])}
  </div>
</section>
<section class="section" style="background:var(--color-surface)">
  <div class="container">
    <div class="section-header"><h2>Für wen eignet sich Polsterreinigung?</h2></div>
    {uc_grid([('🏢','Büros &amp; Kanzleien','Konferenzstühle, Empfangssofas, Wartezimmermöbel – für einen gepflegten Eindruck bei Kunden.'),('🏨','Hotels &amp; Pensionen','Zimmersessel, Lobbysofas, Restaurantstühle – Hygiene und Frische für jeden Gast.'),('🏥','Praxen &amp; medizinische Einrichtungen','Wartezimmerstühle und Behandlungsliegen – regelmäßige Reinigung für Hygienestandards.')])}
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Häufige Fragen</h2></div>
    {faq([('Wie lange trocknen gereinigte Polster?','In der Regel 2–4 Stunden, je nach Material und Belüftung. Die Möbel können danach wieder normal genutzt werden.'),('Können alle Stoffe gereinigt werden?','Wir reinigen die meisten Gewebe und Kunstleder. Bei empfindlichen Materialien beraten wir Sie vorab.'),('Werden Flecken garantiert entfernt?','Frische Flecken lassen sich meist vollständig entfernen. Ältere, eingetrocknete Flecken können in ihrer Intensität reduziert werden.'),('Wie oft sollten Polster gereinigt werden?','Für Büros und Empfangsbereiche empfehlen wir ein- bis zweimal jährlich. In Arztpraxen und Hotels häufiger.'),('Was kostet Polsterreinigung?','Der Preis richtet sich nach Anzahl der Möbelstücke. Kontaktieren Sie uns für ein individuelles Angebot.')])}
  </div>
</section>
{cta_sec('Polsterreinigung Friedrichshafen anfragen','Beschreiben Sie kurz, welche Möbel gereinigt werden sollen – wir senden ein Angebot.')}
{pills([(h,l) for h,l in related('polsterreinigung')][:8])}
</main>'''

def page_praxisreinigung():
    return f'''<main>
{bc([('/','Startseite'),('leistungen','Leistungen'),(None,'Praxisreinigung Friedrichshafen')])}
<section class="subpage-hero">
  <div class="container">
    <div class="subpage-hero-grid">
      <div>
        <p class="eyebrow">Praxisreinigung Friedrichshafen</p>
        <h1>Hygienestandards –<br><em>die Patienten schützen.</em></h1>
        <p class="subpage-hero-lead">Praxen stellen höhere Anforderungen an die Reinigung als normale Büros. K.K. Reinigung reinigt Arzt- und Zahnarztpraxen, Physiotherapeuten und Heilpraktiker nach Ihren Hygienestandards.</p>
        {checks(['Wartebereich, Behandlungsräume und Sanitäranlagen','Desinfektion von Kontaktflächen und Türgriffen','Diskrete Reinigung außerhalb der Sprechzeiten','Festes, eingearbeitetes Team für Ihre Praxis'])}
        {ctas('Hallo%2C%20ich%20ben%C3%B6tige%20Praxisreinigung%20in%20Friedrichshafen.')}
      </div>
      {form('🏥','Praxisreinigung anfragen','Praxisreinigung Anfrage – kkreinigung.com','z.B. Zahnarztpraxis 120m², täglich nach Praxisschluss')}
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Praxisreinigung – was ist enthalten?</h2></div>
    {svc_grid([('🏥','Wartezimmer','Stühle, Tische, Boden, Lesematerial – täglich gereinigt, für einen gepflegten ersten Eindruck.'),('🔬','Behandlungsräume','Liegen abwischen, Böden reinigen, Kontaktflächen desinfizieren – nach Ihren Vorgaben.'),('🚿','Sanitäranlagen','WC, Waschbecken, Spiegel – gründlich desinfiziert für Patienten und Personal.'),('🖥️','Empfang &amp; Anmeldung','Tresen, Telefon, Tastaturen, Böden – sauber und repräsentativ für den ersten Kontakt.'),('🚪','Türgriffe &amp; Schalter','Desinfektion aller Kontaktflächen – ein wichtiger Beitrag zur Hygiene in Ihrer Praxis.'),('🧴','Verbrauchsmaterial','Seifenspender, Handtücher und Hygienebeutel auffüllen auf Wunsch.')])}
  </div>
</section>
<section class="section" style="background:var(--color-surface)">
  <div class="container">
    <div class="section-header"><h2>Für welche Praxen geeignet?</h2></div>
    {uc_grid([('🦷','Zahnarztpraxen','Behandlungsräume, Wartebereich und Empfang – hygienisch sauber für Ihre Patienten.'),('👩‍⚕️','Arztpraxen','Allgemeinmedizin, Fachärzte – Reinigung nach Praxisschluss, diskret und gründlich.'),('💪','Therapiepraxen','Physiotherapie, Ergotherapie, Heilpraktiker – Liegen, Böden und Wartebereich regelmäßig gereinigt.')])}
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Häufige Fragen</h2></div>
    {faq([('Wann wird die Praxis gereinigt?','Meist abends nach Praxisschluss oder morgens vor Beginn der Sprechzeiten – je nach Ihrer Präferenz.'),('Welche Desinfektionsmittel verwenden Sie?','Wir passen uns Ihren Vorgaben an. Wenn Sie bevorzugte Mittel haben, setzen wir diese ein. Alternativ bringen wir geeignete Produkte mit.'),('Ist das Team eingearbeitet und zuverlässig?','Ja. Sie bekommen ein festes Team, das Ihre Praxis kennt und auf Ihre Anforderungen eingespielt ist.'),('Reinigen Sie auch am Wochenende?','Auf Anfrage ja. Teilen Sie uns Ihren Bedarf mit.'),('Was kostet Praxisreinigung?','Der Preis richtet sich nach Fläche, Umfang und Häufigkeit. Wir erstellen ein individuelles Angebot.')])}
  </div>
</section>
{cta_sec('Praxisreinigung Friedrichshafen anfragen','Beschreiben Sie Ihre Praxis kurz – wir erstellen ein passendes Angebot.')}
{pills([(h,l) for h,l in related('praxisreinigung')][:8])}
</main>'''

def page_schulreinigung():
    return f'''<main>
{bc([('/','Startseite'),('leistungen','Leistungen'),(None,'Schulreinigung Friedrichshafen')])}
<section class="subpage-hero">
  <div class="container">
    <div class="subpage-hero-grid">
      <div>
        <p class="eyebrow">Schulreinigung Friedrichshafen</p>
        <h1>Saubere Schule –<br><em>sicheres Lernumfeld.</em></h1>
        <p class="subpage-hero-lead">Schulen und Kindergärten brauchen zuverlässige Reinigungspartner. K.K. Reinigung reinigt Klassenzimmer, Flure, Sanitäranlagen und Gemeinschaftsbereiche im Bodenseekreis.</p>
        {checks(['Klassenzimmer, Flure, Aula und Sanitäranlagen','Reinigung außerhalb der Schulzeiten oder am Wochenende','Hygienegeprüfte Reinigungsmittel','Langfristige Zusammenarbeit mit stabilem Team'])}
        {ctas('Hallo%2C%20ich%20ben%C3%B6tige%20Schulreinigung%20in%20Friedrichshafen.')}
      </div>
      {form('🏫','Schulreinigung anfragen','Schulreinigung Anfrage – kkreinigung.com','z.B. Grundschule 800m², täglich Reinigung nach Schulschluss')}
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Schulreinigung – was ist enthalten?</h2></div>
    {svc_grid([('📚','Klassenzimmer','Böden reinigen, Tische wischen, Tafeln und Oberflächen – täglich oder nach Bedarf.'),('🚿','Sanitäranlagen','WC-Anlagen, Waschbecken, Böden – nach jedem Schultag gründlich gereinigt und desinfiziert.'),('🏃','Flure &amp; Treppen','Böden, Handläufe, Spinde – sauber für eine sichere Bewegung im Schulgebäude.'),('🍽️','Mensa &amp; Pausenraum','Tische, Stühle, Böden und Küchenflächen – täglich nach dem Betrieb gereinigt.'),('🖥️','EDV-Räume &amp; Bibliothek','Oberflächen abwischen, Böden reinigen – schonend für empfindliche Geräte.'),('🌿','Eingänge &amp; Außenbereiche','Eingangsbereiche, Außenstiegen und überdachte Außenflächen auf Wunsch.')])}
  </div>
</section>
<section class="section" style="background:var(--color-surface)">
  <div class="container">
    <div class="section-header"><h2>Für welche Bildungseinrichtungen?</h2></div>
    {uc_grid([('🏫','Schulen &amp; Gymnasien','Grund-, Mittel- und Oberschulen – verlässliche Reinigung für Schüler und Lehrer.'),('🧒','Kindergärten &amp; Kitas','Spielbereiche, Schlafräume, Sanitäranlagen – besonders gründlich und mit kindgerechten Mitteln.'),('🏛️','VHS &amp; Bildungszentren','Seminarräume, Verwaltung, Sanitäranlagen – für Kursanbieter und Bildungsträger.')])}
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Häufige Fragen</h2></div>
    {faq([('Wann wird die Schule gereinigt?','Üblicherweise abends nach Schulschluss oder am Wochenende, damit der Schulbetrieb nicht beeinträchtigt wird.'),('Welche Reinigungsmittel werden eingesetzt?','Wir verwenden für Kindergärten und Schulen besonders schadstoffarme und kindgerechte Reinigungsmittel.'),('Gibt es Erfahrung mit öffentlichen Ausschreibungen?','Ja. Wir können bei entsprechenden Anforderungen Nachweise und Referenzen vorlegen.'),('Wie schnell kann der Einsatz starten?','Nach einem kurzen Gespräch und Besichtigung können wir einen Starttermin vereinbaren.'),('Was kostet Schulreinigung?','Der Preis richtet sich nach Fläche, Objekttyp und Häufigkeit. Wir erstellen ein transparentes Angebot.')])}
  </div>
</section>
{cta_sec('Schulreinigung Friedrichshafen anfragen','Beschreiben Sie Ihre Einrichtung – wir erstellen ein passendes Reinigungskonzept.')}
{pills([(h,l) for h,l in related('schulreinigung')][:8])}
</main>'''

def page_unterhaltsreinigung():
    return f'''<main>
{bc([('/','Startseite'),('leistungen','Leistungen'),(None,'Unterhaltsreinigung Friedrichshafen')])}
<section class="subpage-hero">
  <div class="container">
    <div class="subpage-hero-grid">
      <div>
        <p class="eyebrow">Unterhaltsreinigung Friedrichshafen</p>
        <h1>Dauerhaft sauber –<br><em>ohne eigenen Aufwand.</em></h1>
        <p class="subpage-hero-lead">Unterhaltsreinigung bedeutet planbare, regelmäßige Sauberkeit in Ihrem Betrieb. K.K. Reinigung kommt nach festen Intervallen – zuverlässig, pünktlich und immer mit dem gleichen Team.</p>
        {checks(['Feste Reinigungsintervalle: täglich, wöchentlich oder individuell','Gleiche Ansprechpartner – keine wechselnden Fremden','Alle Bereiche: Büro, Flure, Sanitär, Küche','Einsatz außerhalb der Betriebszeiten möglich'])}
        {ctas('Hallo%2C%20ich%20ben%C3%B6tige%20Unterhaltsreinigung%20in%20Friedrichshafen.')}
      </div>
      {form('🔄','Unterhaltsreinigung anfragen','Unterhaltsreinigung Anfrage – kkreinigung.com','z.B. Gewerbefläche 400m², zweimal wöchentlich, Friedrichshafen')}
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Unterhaltsreinigung – was ist enthalten?</h2></div>
    {svc_grid([('🔄','Regelmäßige Intervalle','Täglich, wöchentlich oder zweiwöchentlich – feste Termine, planbar in Ihren Betriebsablauf.'),('🧹','Böden &amp; Flächen','Saugen, wischen, kehren – je nach Bodenbelag und Nutzungsintensität des Bereichs.'),('🚿','Sanitäranlagen','Regelmäßige Reinigung und Desinfektion – verlässlich nach jedem Reinigungstag.'),('☕','Küche &amp; Teeküche','Arbeitsflächen, Spüle, Geräte außen – sauber nach jedem Arbeitstag.'),('🖥️','Bürobereiche','Schreibtische, Bildschirme, Tastaturen – gepflegt und staubfrei.'),('📋','Protokoll auf Wunsch','Reinigungsnachweis und Checkliste für Ihr internes Qualitätsmanagement.')])}
  </div>
</section>
<section class="section" style="background:var(--color-surface)">
  <div class="container">
    <div class="section-header"><h2>Für wen ist Unterhaltsreinigung geeignet?</h2></div>
    {uc_grid([('🏢','Büros &amp; Unternehmen','Für Firmen jeder Größe, die einen verlässlichen Reinigungspartner für regelmäßige Sauberkeit suchen.'),('🏥','Praxen &amp; medizinische Einrichtungen','Tägliche oder mehrmals wöchentliche Reinigung – für die Hygieneanforderungen Ihrer Einrichtung.'),('🏠','Hausverwaltungen','Treppenhäuser, Gemeinschaftsräume, Waschküchen – planbare Reinigung für die gesamte Liegenschaft.')])}
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Häufige Fragen</h2></div>
    {faq([('Was kostet Unterhaltsreinigung in Friedrichshafen?','Der Preis richtet sich nach Fläche, Reinigungsumfang und Intervall. Wir erstellen ein individuelles Angebot nach kurzer Beschreibung oder Besichtigung.'),('Müssen wir einen langfristigen Vertrag abschließen?','Für regelmäßige Reinigung werden die Konditionen klar schriftlich festgehalten. Beim Ersteinsatz gibt es keine langen Bindungsfristen.'),('Wie flexibel sind die Reinigungszeiten?','Sehr flexibel. Wir reinigen morgens vor Betriebsbeginn, abends nach Feierabend oder auch tagsüber.'),('Gibt es ein festes Team?','Ja. Sie bekommen nach Möglichkeit immer dasselbe Team, das Ihr Objekt kennt.'),('Was passiert bei Urlaub oder Krankheit?','Wir stellen die Vertretung sicher, damit Ihre Reinigung zuverlässig stattfindet.')])}
  </div>
</section>
{cta_sec('Unterhaltsreinigung Friedrichshafen anfragen','Beschreiben Sie Ihren Bedarf – wir erstellen ein passendes Angebot für Ihren Betrieb.')}
{pills([(h,l) for h,l in related('unterhaltsreinigung')][:8])}
</main>'''

def page_leistungen():
    return '''<main>
<div class="breadcrumb-wrap">
  <div class="container">
    <nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">Startseite</a><span aria-hidden="true">›</span><span>Leistungen</span></nav>
  </div>
</div>
<section class="subpage-hero">
  <div class="container">
    <div class="subpage-hero-simple">
      <p class="eyebrow">Alle Leistungen</p>
      <h1>Professionelle Reinigung –<br><em>für jeden Bedarf.</em></h1>
      <p class="subpage-hero-lead">Vom Büro bis zur Baustelle, von der Arztpraxis bis zum Hotel: K.K. Reinigung bietet maßgeschneiderte Reinigungslösungen für Unternehmen im Bodenseekreis.</p>
      <div class="subpage-hero-ctas">
        <a href="kontakt" class="btn btn-cta btn-lg">Kostenloses Angebot</a>
        <a href="tel:01778740889" class="btn btn-primary btn-lg">''' + PHONE_SVG + ''' 0177 8740889</a>
      </div>
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Unsere Reinigungsleistungen</h2><p>Wählen Sie Ihren Bereich – oder kontaktieren Sie uns direkt für ein individuelles Reinigungskonzept.</p></div>
    <div class="service-grid">
      <a href="bueroreinigung-friedrichshafen" class="service-card" style="text-decoration:none">
        <span class="card-emoji">💼</span>
        <h3>Büroreinigung</h3>
        <p>Schreibtische, Böden, Sanitäranlagen, Küche – diskret und im laufenden Betrieb oder außerhalb der Arbeitszeiten.</p>
      </a>
      <a href="unterhaltsreinigung-friedrichshafen" class="service-card" style="text-decoration:none">
        <span class="card-emoji">🔄</span>
        <h3>Unterhaltsreinigung</h3>
        <p>Planbare, regelmäßige Reinigung mit festen Intervallen. Gleicher Ansprechpartner, verlässliche Abläufe.</p>
      </a>
      <a href="gebaeudereinigung-friedrichshafen" class="service-card" style="text-decoration:none">
        <span class="card-emoji">🏢</span>
        <h3>Gebäudereinigung</h3>
        <p>Bürogebäude, Treppenhäuser, Wohnanlagen und Gewerbeimmobilien – professionell und termingerecht.</p>
      </a>
      <a href="bauendreinigung-friedrichshafen" class="service-card" style="text-decoration:none">
        <span class="card-emoji">🏗️</span>
        <h3>Bauendreinigung</h3>
        <p>Neubau, Umbau, Renovierung – übergabereif nach dem Bau. Baustaub, Kalkflecken, Fenster, Böden.</p>
      </a>
      <a href="grundreinigung-friedrichshafen" class="service-card" style="text-decoration:none">
        <span class="card-emoji">🧽</span>
        <h3>Grundreinigung</h3>
        <p>Tiefenreinigung für Böden, Küchen, Sanitäranlagen – einmalig, saisonal oder bei Mieterwechsel.</p>
      </a>
      <a href="praxisreinigung-friedrichshafen" class="service-card" style="text-decoration:none">
        <span class="card-emoji">🏥</span>
        <h3>Praxisreinigung</h3>
        <p>Arzt- und Zahnarztpraxen, Therapiepraxen – Desinfektion, Hygienestandards, festes Team.</p>
      </a>
      <a href="hotelreinigung-friedrichshafen" class="service-card" style="text-decoration:none">
        <span class="card-emoji">🏨</span>
        <h3>Hotelreinigung</h3>
        <p>Zimmer, Lobby, Frühstücksraum und öffentliche Bereiche – diskret und zuverlässig für Ihren Betrieb.</p>
      </a>
      <a href="schulreinigung-friedrichshafen" class="service-card" style="text-decoration:none">
        <span class="card-emoji">🏫</span>
        <h3>Schulreinigung</h3>
        <p>Klassenzimmer, Flure, Sanitäranlagen und Mensabereiche – zuverlässig außerhalb der Schulzeiten.</p>
      </a>
      <a href="polsterreinigung-friedrichshafen" class="service-card" style="text-decoration:none">
        <span class="card-emoji">🛋️</span>
        <h3>Polsterreinigung</h3>
        <p>Sofas, Bürostühle, Konferenzstühle – Fleckenentfernung, Geruchsneutralisierung, materialgerecht.</p>
      </a>
    </div>
  </div>
</section>
<section class="section" style="background:var(--color-surface)">
  <div class="container">
    <div class="section-header"><h2>Unser Servicegebiet</h2></div>
    <div class="region-pills" style="justify-content:center">
      <a href="/" class="region-pill">Friedrichshafen</a>
      <a href="reinigungsfirma-lindau" class="region-pill">Lindau</a>
      <a href="reinigungsfirma-ravensburg" class="region-pill">Ravensburg</a>
      <span class="region-pill">Tettnang</span>
      <span class="region-pill">Überlingen</span>
      <span class="region-pill">Meckenbeuren</span>
      <span class="region-pill">Markdorf</span>
      <span class="region-pill">Bodenseekreis</span>
    </div>
  </div>
</section>
''' + cta_sec('Kostenloses Angebot anfragen','Beschreiben Sie kurz Ihren Reinigungsbedarf – wir melden uns am selben Tag.') + '''
</main>'''

def page_lindau():
    return f'''<main>
{bc([('/','Startseite'),(None,'Reinigungsfirma Lindau')])}
<section class="subpage-hero">
  <div class="container">
    <div class="subpage-hero-grid">
      <div>
        <p class="eyebrow">Reinigungsfirma Lindau</p>
        <h1>Professionelle Reinigung –<br><em>in Lindau &amp; Umgebung.</em></h1>
        <p class="subpage-hero-lead">K.K. Reinigung aus dem Bodenseekreis ist auch in Lindau tätig. Büroreinigung, Unterhaltsreinigung, Gebäudereinigung und Bauendreinigung – für Unternehmen und Hausverwaltungen im Raum Lindau.</p>
        {checks(['Büros, Praxen, Gewerbeobjekte und Wohnanlagen','Regelmäßige Unterhaltsreinigung mit festen Terminen','Bauendreinigung nach Neubau oder Umbau','Direkter Kontakt – keine Vermittlung'])}
        {ctas('Hallo%2C%20ich%20ben%C3%B6tige%20Reinigung%20in%20Lindau.')}
      </div>
      {form('🏙️','Reinigung in Lindau anfragen','Reinigungsanfrage Lindau – kkreinigung.com','z.B. Büro 200m², wöchentlich, Lindau')}
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Unsere Leistungen in Lindau</h2></div>
    {svc_grid([('💼','Büroreinigung Lindau','Schreibtische, Böden, Sanitäranlagen, Küche – diskret, pünktlich, mit festem Team.'),('🔄','Unterhaltsreinigung','Regelmäßige Reinigung nach Ihren Intervallen – täglich, wöchentlich oder individuell.'),('🏢','Gebäudereinigung','Treppenhäuser, Wohnanlagen, Gewerbeimmobilien – verlässlicher Partner für Hausverwaltungen.'),('🏗️','Bauendreinigung','Übergabereife Reinigung nach Bau oder Umbau – termingerecht für Ihre Übergabe.'),('🧽','Grundreinigung','Tiefenreinigung für Böden, Küchen, Sanitäranlagen – einmalig oder saisonal.'),('🏥','Praxisreinigung','Arztpraxen und Therapiepraxen – hygienische Reinigung nach Ihren Standards.')])}
  </div>
</section>
{cta_sec('Reinigung in Lindau anfragen','Kontaktieren Sie uns für ein kostenloses Angebot – Rückmeldung am selben Tag.')}
<section class="section" style="padding:clamp(28px,3.5vw,44px) 0">
  <div class="container">
    <h3 style="font-family:var(--font-body);font-size:1rem;font-weight:700;color:var(--color-text-secondary);margin-bottom:16px">Weitere Leistungen &amp; Standorte</h3>
    <div class="region-pills">
      <a href="bueroreinigung-friedrichshafen" class="region-pill">Büroreinigung Friedrichshafen</a>
      <a href="gebaeudereinigung-friedrichshafen" class="region-pill">Gebäudereinigung Friedrichshafen</a>
      <a href="unterhaltsreinigung-friedrichshafen" class="region-pill">Unterhaltsreinigung Friedrichshafen</a>
      <a href="bauendreinigung-friedrichshafen" class="region-pill">Bauendreinigung Friedrichshafen</a>
      <a href="reinigungsfirma-ravensburg" class="region-pill">Reinigungsfirma Ravensburg</a>
      <a href="leistungen" class="region-pill">Alle Leistungen</a>
    </div>
  </div>
</section>
</main>'''

def page_ravensburg():
    return f'''<main>
{bc([('/','Startseite'),(None,'Reinigungsfirma Ravensburg')])}
<section class="subpage-hero">
  <div class="container">
    <div class="subpage-hero-grid">
      <div>
        <p class="eyebrow">Reinigungsfirma Ravensburg</p>
        <h1>Professionelle Reinigung –<br><em>in Ravensburg &amp; Umgebung.</em></h1>
        <p class="subpage-hero-lead">K.K. Reinigung aus dem Bodenseekreis ist auch in Ravensburg tätig. Büroreinigung, Unterhaltsreinigung, Gebäudereinigung und Bauendreinigung – für Unternehmen und Hausverwaltungen im Raum Ravensburg.</p>
        {checks(['Büros, Praxen, Gewerbeobjekte und Wohnanlagen','Regelmäßige Unterhaltsreinigung mit festen Terminen','Bauendreinigung nach Neubau oder Umbau','Direkter Kontakt – keine Vermittlung'])}
        {ctas('Hallo%2C%20ich%20ben%C3%B6tige%20Reinigung%20in%20Ravensburg.')}
      </div>
      {form('🏙️','Reinigung in Ravensburg anfragen','Reinigungsanfrage Ravensburg – kkreinigung.com','z.B. Büro 200m², wöchentlich, Ravensburg')}
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="section-header"><h2>Unsere Leistungen in Ravensburg</h2></div>
    {svc_grid([('💼','Büroreinigung Ravensburg','Schreibtische, Böden, Sanitäranlagen, Küche – diskret, pünktlich, mit festem Team.'),('🔄','Unterhaltsreinigung','Regelmäßige Reinigung nach Ihren Intervallen – täglich, wöchentlich oder individuell.'),('🏢','Gebäudereinigung','Treppenhäuser, Wohnanlagen, Gewerbeimmobilien – verlässlicher Partner für Hausverwaltungen.'),('🏗️','Bauendreinigung','Übergabereife Reinigung nach Bau oder Umbau – termingerecht für Ihre Übergabe.'),('🧽','Grundreinigung','Tiefenreinigung für Böden, Küchen, Sanitäranlagen – einmalig oder saisonal.'),('🏥','Praxisreinigung','Arztpraxen und Therapiepraxen – hygienische Reinigung nach Ihren Standards.')])}
  </div>
</section>
{cta_sec('Reinigung in Ravensburg anfragen','Kontaktieren Sie uns für ein kostenloses Angebot – Rückmeldung am selben Tag.')}
<section class="section" style="padding:clamp(28px,3.5vw,44px) 0">
  <div class="container">
    <h3 style="font-family:var(--font-body);font-size:1rem;font-weight:700;color:var(--color-text-secondary);margin-bottom:16px">Weitere Leistungen &amp; Standorte</h3>
    <div class="region-pills">
      <a href="bueroreinigung-friedrichshafen" class="region-pill">Büroreinigung Friedrichshafen</a>
      <a href="gebaeudereinigung-friedrichshafen" class="region-pill">Gebäudereinigung Friedrichshafen</a>
      <a href="unterhaltsreinigung-friedrichshafen" class="region-pill">Unterhaltsreinigung Friedrichshafen</a>
      <a href="bauendreinigung-friedrichshafen" class="region-pill">Bauendreinigung Friedrichshafen</a>
      <a href="reinigungsfirma-lindau" class="region-pill">Reinigungsfirma Lindau</a>
      <a href="leistungen" class="region-pill">Alle Leistungen</a>
    </div>
  </div>
</section>
</main>'''

def page_ueber_uns():
    return f'''<main>
{bc([('/','Startseite'),(None,'Über uns')])}
<section class="subpage-hero">
  <div class="container">
    <div class="subpage-hero-simple">
      <p class="eyebrow">Über K.K. Reinigung</p>
      <h1>Ihr Reinigungspartner<br><em>am Bodensee.</em></h1>
      <p class="subpage-hero-lead">K.K. Reinigung steht für persönliche Betreuung, verlässliche Qualität und faire Preise. Gegründet 2016 in Friedrichshafen – seither verlässlicher Partner für Unternehmen im Bodenseekreis.</p>
      <div class="subpage-hero-ctas">
        <a href="kontakt" class="btn btn-cta btn-lg">Kontakt aufnehmen</a>
        <a href="tel:01778740889" class="btn btn-primary btn-lg">{PHONE_SVG} 0177 8740889</a>
      </div>
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="subpage-hero-grid">
      <div>
        <p class="eyebrow">Der Inhaber</p>
        <h2 style="font-family:var(--font-display);font-size:clamp(1.5rem,2.5vw,2rem);font-weight:400;color:var(--color-primary-dark);margin-bottom:16px">Khaled Kurdi</h2>
        <p style="font-size:1rem;color:var(--color-text-secondary);line-height:1.75;margin-bottom:16px">Khaled Kurdi führt K.K. Reinigung als persönlichen Betrieb. Er koordiniert jeden Auftrag selbst und ist bei Fragen, Änderungen oder Problemen direkt erreichbar.</p>
        <p style="font-size:1rem;color:var(--color-text-secondary);line-height:1.75;margin-bottom:24px">Wer K.K. Reinigung anruft oder schreibt, landet nicht bei einem Disponenten oder einer Zentrale. Die Nummer führt direkt zu Khaled Kurdi.</p>
        <div style="display:flex;flex-direction:column;gap:10px">
          <a href="tel:01778740889" style="display:flex;align-items:center;gap:10px;font-size:.9375rem;font-weight:600;color:var(--color-primary);text-decoration:none">{PHONE_SVG} 0177 8740889</a>
          <a href="mailto:kurdi.reinigungsservice@gmail.com" style="display:flex;align-items:center;gap:10px;font-size:.9375rem;font-weight:600;color:var(--color-primary);text-decoration:none"><svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" style="flex-shrink:0"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg> kurdi.reinigungsservice@gmail.com</a>
        </div>
      </div>
      <div style="background:var(--color-surface);border:1px solid var(--color-border);border-radius:var(--radius-xl);aspect-ratio:4/3;display:flex;align-items:center;justify-content:center;text-align:center;padding:32px">
        <div>
          <div style="width:72px;height:72px;border-radius:50%;background:var(--color-primary);color:#fff;font-size:1.5rem;font-weight:800;display:flex;align-items:center;justify-content:center;margin:0 auto 16px">KK</div>
          <p style="font-size:.9375rem;font-weight:600;color:var(--color-primary-dark)">Khaled Kurdi</p>
          <p style="font-size:.875rem;color:var(--color-text-muted);margin-top:4px">Inhaber K.K. Reinigung<br>Bodenseekreis · seit 2016</p>
        </div>
      </div>
    </div>
  </div>
</section>
<section class="section" style="background:var(--color-surface)">
  <div class="container">
    <div class="section-header"><h2>Wie wir arbeiten</h2></div>
    {svc_grid([('1️⃣','Verlässliche Absprachen','Was vereinbart wird, wird gemacht. Preis, Umfang und Termin werden vorab klar festgelegt.'),('2️⃣','Gründliche Ausführung','Jeder vereinbarte Bereich wird gereinigt – ohne Abkürzungen. Falls etwas nicht stimmt, kommen wir nach.'),('3️⃣','Direkter Kontakt','Erreichbar per Telefon und WhatsApp. Keine Weitervermittlung an Disponenten oder Callcenter.')])}
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="subpage-hero-grid">
      <div>
        <p class="eyebrow">Was wir mitbringen</p>
        <h2 style="font-family:var(--font-display);font-size:clamp(1.4rem,2.2vw,1.875rem);font-weight:400;color:var(--color-primary-dark);margin-bottom:20px">Erfahrung &amp; Verlässlichkeit</h2>
        <ul class="check-list">
          <li>Über 10 gewerbliche Kunden im Bodenseekreis betreut</li>
          <li>Erfahrung mit Büros, Gewerbeflächen und anspruchsvollen Hygienestandards</li>
          <li>Regelmäßige Reinigung von Sanitäranlagen an Autobahnraststätten</li>
          <li>Lokal in Friedrichshafen, Lindau und Ravensburg tätig</li>
          <li>Nachbesserung kostenlos, wenn etwas nicht dem Standard entspricht</li>
        </ul>
      </div>
      <div style="display:flex;flex-direction:column;gap:16px">
        <div style="background:rgba(4,112,186,.06);border:1px solid rgba(4,112,186,.15);border-radius:var(--radius-lg);padding:24px">
          <h3 style="font-size:.9375rem;font-weight:700;color:var(--color-primary-dark);margin-bottom:12px">Einsatzgebiet</h3>
          <div class="region-pills">
            <span class="region-pill">Friedrichshafen</span>
            <span class="region-pill">Lindau</span>
            <span class="region-pill">Ravensburg</span>
            <span class="region-pill">Tettnang</span>
            <span class="region-pill">Überlingen</span>
            <span class="region-pill">Bodenseekreis</span>
          </div>
        </div>
        <div style="background:var(--color-surface);border:1px solid var(--color-border);border-radius:var(--radius-lg);padding:24px">
          <h3 style="font-size:.9375rem;font-weight:700;color:var(--color-primary-dark);margin-bottom:8px">Erreichbarkeit</h3>
          <p style="font-size:.9375rem;color:var(--color-text-secondary);margin:0">Mo–Sa, 7–20 Uhr<br>Telefon und WhatsApp</p>
          <p style="font-size:.8125rem;color:var(--color-text-muted);margin-top:6px">Kein Büro für Besuche vor Ort. Wir kommen zu Ihnen.</p>
        </div>
      </div>
    </div>
  </div>
</section>
{cta_sec('Jetzt Kontakt aufnehmen','Beschreiben Sie kurz Ihren Bedarf – wir melden uns zeitnah.')}
</main>'''

def page_kontakt():
    return f'''<main>
{bc([('/','Startseite'),(None,'Kontakt')])}
<section class="subpage-hero">
  <div class="container">
    <div class="subpage-hero-simple">
      <p class="eyebrow">Kontakt aufnehmen</p>
      <h1>Kostenloses Angebot –<br><em>am selben Tag.</em></h1>
      <p class="subpage-hero-lead">Schildern Sie uns kurz Ihren Reinigungsbedarf. Wir melden uns am selben Tag mit einem unverbindlichen Angebot.</p>
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="subpage-hero-grid">
      <div>
        <h2 style="font-family:var(--font-body);font-size:1.25rem;font-weight:700;color:var(--color-primary-dark);margin-bottom:24px">So erreichen Sie uns</h2>
        <div style="display:flex;flex-direction:column;gap:12px;margin-bottom:28px">
          <a href="tel:01778740889" style="display:flex;align-items:flex-start;gap:16px;padding:16px 18px;background:var(--color-surface);border:1px solid var(--color-border);border-radius:var(--radius-lg);text-decoration:none;transition:border-color 150ms">
            <div style="width:42px;height:42px;border-radius:var(--radius-md);background:var(--color-primary);display:flex;align-items:center;justify-content:center;flex-shrink:0">{PHONE_SVG.replace('stroke="currentColor"','stroke="white"')}</div>
            <div><div style="font-size:.875rem;font-weight:700;color:var(--color-primary-dark)">Anrufen</div><div style="font-size:1rem;font-weight:700;color:var(--color-primary)">0177 8740889</div><div style="font-size:.8125rem;color:var(--color-text-muted);margin-top:2px">Mo–Sa, 7–20 Uhr</div></div>
          </a>
          <a href="https://wa.me/491778740889?text=Hallo%2C%20ich%20interessiere%20mich%20f%C3%BCr%20Ihren%20Reinigungsservice." style="display:flex;align-items:flex-start;gap:16px;padding:16px 18px;background:var(--color-surface);border:1px solid var(--color-border);border-radius:var(--radius-lg);text-decoration:none;transition:border-color 150ms">
            <div style="width:42px;height:42px;border-radius:var(--radius-md);background:#25d366;display:flex;align-items:center;justify-content:center;flex-shrink:0;color:#fff">{WA_SVG}</div>
            <div><div style="font-size:.875rem;font-weight:700;color:var(--color-primary-dark)">WhatsApp</div><div style="font-size:1rem;font-weight:600;color:#16a34a">Nachricht schreiben</div><div style="font-size:.8125rem;color:var(--color-text-muted);margin-top:2px">Oft Antwort innerhalb einer Stunde</div></div>
          </a>
          <a href="mailto:kurdi.reinigungsservice@gmail.com" style="display:flex;align-items:flex-start;gap:16px;padding:16px 18px;background:var(--color-surface);border:1px solid var(--color-border);border-radius:var(--radius-lg);text-decoration:none;transition:border-color 150ms">
            <div style="width:42px;height:42px;border-radius:var(--radius-md);background:var(--color-primary);display:flex;align-items:center;justify-content:center;flex-shrink:0"><svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="white" stroke-width="2" style="flex-shrink:0"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg></div>
            <div><div style="font-size:.875rem;font-weight:700;color:var(--color-primary-dark)">E-Mail</div><div style="font-size:.9375rem;font-weight:600;color:var(--color-primary);word-break:break-all">kurdi.reinigungsservice@gmail.com</div><div style="font-size:.8125rem;color:var(--color-text-muted);margin-top:2px">Antwort innerhalb von 24 Stunden</div></div>
          </a>
        </div>
        <div style="background:rgba(4,112,186,.06);border:1px solid rgba(4,112,186,.15);border-radius:var(--radius-lg);padding:20px">
          <h3 style="font-size:.9375rem;font-weight:700;color:var(--color-primary-dark);margin-bottom:10px">Einsatzgebiet</h3>
          <div class="region-pills">
            <span class="region-pill">Friedrichshafen</span>
            <span class="region-pill">Lindau</span>
            <span class="region-pill">Ravensburg</span>
            <span class="region-pill">Bodenseekreis</span>
          </div>
          <p style="font-size:.8125rem;color:var(--color-text-muted);margin-top:10px;margin-bottom:0">Kein Büro für Besuche vor Ort. Wir kommen zu Ihnen.</p>
        </div>
      </div>
      <div id="kontaktformular">
        <h2 style="font-family:var(--font-body);font-size:1.25rem;font-weight:700;color:var(--color-primary-dark);margin-bottom:24px">Angebot per Formular anfragen</h2>
        <div class="hero-form-card" style="padding:28px 24px">
          <form action="https://formspree.io/f/xvzgeldw" method="POST">
            <div class="form-group"><label>Name *</label><input type="text" name="name" required placeholder="Ihr vollständiger Name"></div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
              <div class="form-group"><label>Telefon *</label><input type="tel" name="phone" required placeholder="Ihre Telefonnummer"></div>
              <div class="form-group"><label>E-Mail <span style="font-weight:400;color:var(--color-text-muted)">(optional)</span></label><input type="email" name="email" placeholder="ihre@email.de"></div>
            </div>
            <div class="form-group"><label>Welche Leistung benötigen Sie? *</label>
              <select name="service" required style="width:100%;padding:12px 14px;border:1.5px solid var(--color-border);border-radius:var(--radius-md);font-size:.9375rem;color:var(--color-text-primary);background:var(--color-bg);outline:none">
                <option value="">Bitte wählen</option>
                <option>Büroreinigung</option>
                <option>Unterhaltsreinigung</option>
                <option>Gebäudereinigung</option>
                <option>Bauendreinigung</option>
                <option>Grundreinigung</option>
                <option>Praxisreinigung</option>
                <option>Sonstige / Ich bin unsicher</option>
              </select>
            </div>
            <div class="form-group"><label>Ort / Adresse <span style="font-weight:400;color:var(--color-text-muted)">(optional)</span></label><input type="text" name="location" placeholder="z.B. Friedrichshafen, Stadtmitte"></div>
            <div class="form-group"><label>Kurze Beschreibung <span style="font-weight:400;color:var(--color-text-muted)">(optional)</span></label><textarea name="message" rows="4" placeholder="z.B. Bürofläche ca. 200 m², wöchentliche Reinigung, ab Mai"></textarea></div>
            <input type="hidden" name="_subject" value="Neue Kontaktanfrage – kkreinigung.com">
            <button type="submit" class="btn btn-cta" style="width:100%;justify-content:center;margin-top:8px">Anfrage senden</button>
            <p style="font-size:.75rem;color:var(--color-text-muted);text-align:center;margin-top:8px">Unverbindlich. Keine Weitergabe Ihrer Daten. Rückmeldung am selben Tag.</p>
          </form>
        </div>
      </div>
    </div>
  </div>
</section>
</main>'''

def page_faq():
    faqs = [
        ('Was kostet eine Reinigung bei K.K. Reinigung?','Der Preis richtet sich nach Art der Reinigung, Fläche und Häufigkeit. Für ein Büro mit 100 m² und wöchentlicher Reinigung beginnen die Preise ab ca. 120–200 € pro Monat. Wir erstellen ein individuelles Angebot.'),
        ('Wie läuft eine Anfrage ab?','Sie senden uns Ihre Anfrage per Formular, WhatsApp oder Telefon. Wir melden uns zeitnah zurück, klären Fläche, Umfang und Termin und senden Ihnen ein schriftliches Angebot. Nach Ihrer Freigabe wird der Einsatz verbindlich eingeplant.'),
        ('Wie schnell erhalten wir ein Angebot?','In der Regel innerhalb von 24 Stunden. Für einen genauen Preis benötigen wir kurz Informationen zur Fläche und zum gewünschten Umfang.'),
        ('In welchen Orten sind Sie tätig?','Unser Haupteinsatzgebiet ist der Bodenseekreis mit Friedrichshafen, Lindau und Ravensburg. Wir sind auch in Tettnang, Überlingen, Meersburg und umliegenden Gemeinden tätig.'),
        ('Welche Leistungen bieten Sie an?','Büroreinigung, Unterhaltsreinigung, Gebäudereinigung, Bauendreinigung, Grundreinigung, Praxisreinigung, Hotelreinigung, Schulreinigung und Polsterreinigung.'),
        ('Was passiert, wenn wir nicht zufrieden sind?','Wir kommen nochmal und bessern nach – kostenlos. Wenn etwas nicht dem vereinbarten Standard entspricht, wird das ohne weiteren Aufwand für Sie behoben.'),
        ('Müssen wir einen Vertrag unterschreiben?','Beim Ersteinsatz nicht. Sie können uns erst kennenlernen, bevor Sie sich für regelmäßige Zusammenarbeit entscheiden. Für langfristige Intervalle werden die Konditionen klar schriftlich festgehalten.'),
        ('Können Termine regelmäßig vereinbart werden?','Ja. Wöchentlich, zweiwöchentlich oder monatlich. Die Intervalle werden gemeinsam festgelegt und verbindlich eingeplant. Anpassungen sind möglich.'),
        ('Bringen Sie eigene Reinigungsmittel mit?','Ja, wir kommen mit allem Material und Geräten. Auf Wunsch verwenden wir auch umweltfreundliche Reinigungsmittel.'),
        ('Gibt es einen festen Ansprechpartner?','Ja. Khaled Kurdi ist persönlich erreichbar – per Telefon und WhatsApp. Keine Vermittlung an Disponenten oder Callcenter.'),
    ]
    items_html = '\n'.join(f'''    <div class="sp-faq-item">
      <h3 style="font-size:1rem;font-weight:700;color:var(--color-primary-dark);margin-bottom:8px">{q}</h3>
      <p style="font-size:.9375rem;color:var(--color-text-secondary);line-height:1.7;margin:0">{a}</p>
    </div>''' for q,a in faqs)
    return f'''<main>
{bc([('/','Startseite'),(None,'FAQ')])}
<section class="subpage-hero">
  <div class="container">
    <div class="subpage-hero-simple">
      <p class="eyebrow">Häufige Fragen</p>
      <h1>Fragen &amp; Antworten –<br><em>klar und direkt.</em></h1>
      <p class="subpage-hero-lead">Hier finden Sie Antworten auf die häufigsten Fragen zu unseren Leistungen, Preisen und Abläufen. Steht Ihre Frage nicht dabei? Kontaktieren Sie uns direkt.</p>
    </div>
  </div>
</section>
<section class="section">
  <div class="container">
    <div class="sp-faq-list">
{items_html}
    </div>
    <div style="text-align:center;margin-top:36px">
      <p style="font-size:.9375rem;color:var(--color-text-secondary);margin-bottom:16px">Noch eine Frage? Wir antworten direkt.</p>
      <a href="kontakt" class="btn btn-cta btn-lg">Jetzt unverbindlich anfragen</a>
    </div>
  </div>
</section>
{cta_sec('Kontakt aufnehmen','Schildern Sie uns kurz Ihren Bedarf – wir melden uns am selben Tag.')}
</main>'''

def page_datenschutz():
    return '''<main>
<div class="breadcrumb-wrap">
  <div class="container">
    <nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">Startseite</a><span aria-hidden="true">›</span><span>Datenschutz</span></nav>
  </div>
</div>
<section class="section">
  <div class="container">
    <div class="prose">
      <h1 style="font-family:var(--font-body);font-size:clamp(1.5rem,3vw,2rem);font-weight:800;color:var(--color-primary-dark);margin-bottom:32px">Datenschutzerklärung</h1>
      <div style="display:flex;flex-direction:column;gap:28px;color:var(--color-text-secondary);line-height:1.75">
        <div><h2 class="prose h2">1. Verantwortlicher</h2><p><strong>K.K. Gebäudereinigung</strong><br>Inhaber: Khaled Kurdi<br>Heinrich-Heine-Straße 33<br>88045 Friedrichshafen<br>Telefon: 0177 8740889<br>E-Mail: <a href="mailto:kurdi.reinigungsservice@gmail.com" style="color:var(--color-primary)">kurdi.reinigungsservice@gmail.com</a></p></div>
        <div><h2 class="prose h2">2. Erhebung und Speicherung personenbezogener Daten</h2><p>Beim Aufrufen dieser Website werden automatisch Daten durch den Hosting-Anbieter erfasst:</p><ul style="margin-top:10px;padding-left:20px;display:flex;flex-direction:column;gap:4px"><li>IP-Adresse</li><li>Datum und Uhrzeit des Zugriffs</li><li>Browsertyp und Browserversion</li><li>Betriebssystem</li><li>Referrer-URL</li><li>Name des Providers</li></ul><p style="margin-top:12px">Diese Daten sind technisch notwendig, um die Website korrekt anzuzeigen und die Stabilität zu gewährleisten.</p></div>
        <div><h2 class="prose h2">3. Hosting</h2><p>Diese Website wird bei GitHub Pages gehostet.</p></div>
        <div><h2 class="prose h2">4. Cookies &amp; lokaler Speicher</h2><p>Diese Website verwendet <strong>keine Tracking-Cookies</strong>. Ihre Cookie-Einwilligung wird im lokalen Speicher (localStorage) Ihres Browsers gespeichert (Schlüssel: <code>kk-consent</code>). Dieser Eintrag verlässt Ihren Browser nicht.</p><p style="margin-top:10px">Bei Zustimmung zu „Alle akzeptieren" werden Google Fonts dynamisch nachgeladen (Verbindung zu Google-Servern, USA). Sie können Ihre Einwilligung jederzeit widerrufen, indem Sie den Browser-Cache leeren.</p></div>
        <div><h2 class="prose h2">5. Externe Bilder (Unsplash)</h2><p>Auf dieser Website werden Bilder eingebunden, die über das Content Delivery Network (CDN) von <strong>Unsplash, Inc.</strong> (222 Broadway, New York, USA) bereitgestellt werden. Beim Laden dieser Bilder stellt Ihr Browser eine direkte Verbindung zu Servern von Unsplash her. Dabei wird Ihre IP-Adresse an Unsplash übermittelt.</p><p style="margin-top:10px">Die Bilder werden unter der <a href="https://unsplash.com/license" target="_blank" rel="noopener" style="color:var(--color-primary)">Unsplash-Lizenz</a> verwendet, die eine kostenfreie kommerzielle Nutzung erlaubt. Wir haben keinen Einfluss auf die weitere Datenverarbeitung durch Unsplash. Weitere Informationen finden Sie in der <a href="https://unsplash.com/privacy" target="_blank" rel="noopener" style="color:var(--color-primary)">Datenschutzerklärung von Unsplash</a>.</p><p style="margin-top:10px">Die Datenübertragung in die USA erfolgt auf Grundlage der EU-Standardvertragsklauseln gemäß Art. 46 DSGVO.</p></div>
        <div><h2 class="prose h2">6. KI-Chatbot</h2><p>Auf dieser Website ist ein KI-Assistent eingebunden. Ihre Chatnachrichten werden zur Verarbeitung an die API von <strong>OpenAI, LLC</strong> (San Francisco, USA) übertragen. OpenAI verarbeitet diese Daten ausschließlich zur Beantwortung Ihrer Anfrage und verwendet sie gemäß seinen Nutzungsbedingungen nicht zum Training von Modellen (API-Nutzung).</p><p style="margin-top:10px">Die Übertragung in die USA erfolgt auf Grundlage der EU-Standardvertragsklauseln gemäß Art. 46 DSGVO. Chatnachrichten werden nicht dauerhaft gespeichert. Rechtsgrundlage: Art. 6 Abs. 1 lit. b und f DSGVO.</p></div>
        <div><h2 class="prose h2">7. Kontaktaufnahme</h2><p>Wenn Sie uns per Kontaktformular oder E-Mail kontaktieren, werden folgende Daten verarbeitet:</p><ul style="margin-top:10px;padding-left:20px;display:flex;flex-direction:column;gap:4px"><li>Name</li><li>E-Mail-Adresse</li><li>Telefonnummer (optional)</li><li>Inhalt der Nachricht</li></ul></div>
        <div><h2 class="prose h2">8. SSL-/TLS-Verschlüsselung</h2><p>Diese Website nutzt eine SSL-Verschlüsselung zur sicheren Übertragung von Daten.</p></div>
        <div><h2 class="prose h2">9. Rechte der betroffenen Personen</h2><ul style="padding-left:20px;display:flex;flex-direction:column;gap:4px"><li>Auskunft</li><li>Berichtigung</li><li>Löschung</li><li>Einschränkung der Verarbeitung</li><li>Widerspruch</li><li>Datenübertragbarkeit</li></ul></div>
        <div><h2 class="prose h2">10. Aktualität dieser Datenschutzerklärung</h2><p>Stand: April 2026</p></div>
      </div>
    </div>
  </div>
</section>
</main>'''

def page_impressum():
    return '''<main>
<div class="breadcrumb-wrap">
  <div class="container">
    <nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">Startseite</a><span aria-hidden="true">›</span><span>Impressum</span></nav>
  </div>
</div>
<section class="section">
  <div class="container">
    <div class="prose">
      <h1 style="font-family:var(--font-body);font-size:clamp(1.5rem,3vw,2rem);font-weight:800;color:var(--color-primary-dark);margin-bottom:32px">Impressum</h1>
      <div style="display:flex;flex-direction:column;gap:28px;color:var(--color-text-secondary);line-height:1.75">
        <div><h2 class="prose h2">Angaben gemäß § 5 TMG</h2><p><strong>K.K. Gebäudereinigung</strong><br>Inhaber: Khaled Kurdi<br>Heinrich-Heine-Straße 33<br>88045 Friedrichshafen</p></div>
        <div><h2 class="prose h2">Kontakt</h2><p>Telefon: <a href="tel:01778740889" style="color:var(--color-primary)">0177 8740889</a><br>E-Mail: <a href="mailto:kurdi.reinigungsservice@gmail.com" style="color:var(--color-primary)">kurdi.reinigungsservice@gmail.com</a></p></div>
        <div><h2 class="prose h2">Steuerliche Angaben</h2><p>Steuer-ID: 61166/42031</p></div>
        <div><h2 class="prose h2">Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV</h2><p>Khaled Kurdi<br>Heinrich-Heine-Straße 33<br>88045 Friedrichshafen</p></div>
        <div><h2 class="prose h2">EU-Streitschlichtung</h2><p>Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung bereit:</p><p style="margin-top:8px"><a href="https://ec.europa.eu/consumers/odr/" target="_blank" rel="noopener" style="color:var(--color-primary)">https://ec.europa.eu/consumers/odr/</a></p><p style="margin-top:8px">Wir sind nicht verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p></div>
      </div>
    </div>
  </div>
</section>
</main>'''

# ── Page map ──────────────────────────────────────────────────────
PAGES = {
    'bueroreinigung-friedrichshafen.html':   page_bueroreinigung,
    'bauendreinigung-friedrichshafen.html':  page_bauendreinigung,
    'gebaeudereinigung-friedrichshafen.html': page_gebaeudereinigung,
    'grundreinigung-friedrichshafen.html':   page_grundreinigung,
    'hotelreinigung-friedrichshafen.html':   page_hotelreinigung,
    'polsterreinigung-friedrichshafen.html': page_polsterreinigung,
    'praxisreinigung-friedrichshafen.html':  page_praxisreinigung,
    'schulreinigung-friedrichshafen.html':   page_schulreinigung,
    'unterhaltsreinigung-friedrichshafen.html': page_unterhaltsreinigung,
    'leistungen.html':                       page_leistungen,
    'reinigungsfirma-lindau.html':           page_lindau,
    'reinigungsfirma-ravensburg.html':       page_ravensburg,
    'ueber-uns.html':                        page_ueber_uns,
    'kontakt.html':                          page_kontakt,
    'faq.html':                              page_faq,
    'datenschutz.html':                      page_datenschutz,
    'impressum.html':                        page_impressum,
}

# ── Run ───────────────────────────────────────────────────────────
for filename, content_fn in PAGES.items():
    path = os.path.join(REPO, filename)
    if not os.path.exists(path):
        print(f'SKIP (missing): {filename}')
        continue

    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()

    new_main = content_fn()

    # Replace <main>...</main> content
    new_html = re.sub(r'(?s)<main\b[^>]*>.*?</main>', new_main, html, count=1)

    if new_html == html:
        print(f'WARN (no main found): {filename}')
        continue

    with open(path, 'w', encoding='utf-8', newline='') as f:
        f.write(new_html)

    print(f'OK: {filename}')

print('\nAll done. Now run update_pages.py to sync header/footer/widgets.')
