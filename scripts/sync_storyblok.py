# -*- coding: utf-8 -*-
"""Fetch published stories from Storyblok and update local HTML files."""
import requests, re, os, sys
sys.stdout.reconfigure(encoding='utf-8')

SB_TOKEN = os.environ.get("SB_TOKEN", "wsfVdB8yECJ4nvAUckQQZgtt")
CDN = "https://api.storyblok.com/v2/cdn/stories"

SLUG_TO_FILE = {
    "home":       "index.html",
    "leistungen": "leistungen.html",
    "kontakt":    "kontakt.html",
    "ueber-uns":  "ueber-uns.html",
    "faq":        "faq.html",
}

def fetch(slug):
    r = requests.get(CDN + "/" + slug,
        params={"token": SB_TOKEN, "version": "published"}, timeout=20)
    r.raise_for_status()
    return r.json()["story"]["content"]

def replace_marker(html, key, value):
    pattern = "<!-- SB:" + key + " -->.*?<!-- /SB:" + key + " -->"
    replacement = "<!-- SB:" + key + " -->" + value + "<!-- /SB:" + key + " -->"
    return re.subn(pattern, replacement, html, flags=re.DOTALL)

changed = []

# Global settings — phone + email across all pages
try:
    g = fetch("global")
    phone         = g.get("phone", "")
    phone_display = g.get("phone_display", phone)
    email         = g.get("email", "")

    for htmlfile in list(SLUG_TO_FILE.values()):
        if not os.path.exists(htmlfile):
            continue
        html = open(htmlfile, encoding="utf-8").read()
        original = html
        html, _ = replace_marker(html, "phone", phone)
        html, _ = replace_marker(html, "phone_display", phone_display)
        html, _ = replace_marker(html, "email", email)
        if html != original:
            open(htmlfile, "w", encoding="utf-8").write(html)
            changed.append(htmlfile + " (global)")
except Exception as e:
    print("WARN global:", e)

# Per-page content
for slug, htmlfile in SLUG_TO_FILE.items():
    if not os.path.exists(htmlfile):
        continue
    try:
        c = fetch(slug)
        html = open(htmlfile, encoding="utf-8").read()
        original = html
        if c.get("hero_title"):
            html, _ = replace_marker(html, "hero_title", c["hero_title"])
        if c.get("hero_subtitle"):
            html, _ = replace_marker(html, "hero_subtitle", c["hero_subtitle"])
        if c.get("cta_label"):
            html, _ = replace_marker(html, "cta_label", c["cta_label"])
        if html != original:
            open(htmlfile, "w", encoding="utf-8").write(html)
            changed.append(htmlfile)
    except Exception as e:
        print("WARN", slug + ":", e)

if changed:
    print("Updated:", ", ".join(changed))
else:
    print("No changes.")
