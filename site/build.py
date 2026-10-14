#!/usr/bin/env python3
"""Builds the static Amalino website.

    python3 site/build.py [--out DIR] [--contact-email ADDR] [--site https://...]
                          [--donate-url https://...] [--check]
    python3 site/build.py --check-fixture FILE [FILE ...]

Sources: translations/<lang>/website.tsv (key, text; English is the source), site/templates/*.html,
site/style.css, site/amalino.svg and site/og-image.png (1200x630).
Output (default site/dist/): {lang}/index.html, {lang}/about/, {lang}/translate/, {lang}/privacy/
for the six app languages, plus a root index.html and translate/index.html that send the visitor to their
language (the browser's languages, or the one they chose before; a few lines of inline script, no cookies)
and list the languages for browsers without script, assets/ (style, logo, share image) and, with a site
URL, sitemap.xml, robots.txt and the CNAME file GitHub Pages reads. Every page has a language menu in its
header. Links are relative and name index.html, so the build also works from file://.

The contact e-mail and site URL come from --contact-email/--site-url or the environment
(OVK_CONTACT_EMAIL, OVK_SITE_URL), with the app's rules: an e-mail needs an
"@" and no spaces, a site URL must be https://; anything else counts as empty. The donation link comes from
--donate-url or OVK_DONATE_URL (https:// only; website only, never in the app): the about page's "Support
Amalino" section and the footer link. Template blocks {{#email}}...{{/email}}, {{#site}}...{{/site}} and
{{#donate}}...{{/donate}} are left out while the setting is empty; {{v:donate}} is the URL.

--check validates the built site: every page exists with the right lang/dir, no forbidden term
(organisations, untested access methods, open source/GitHub) appears in any page, the free promise is
on home and about, e-mail text appears only when set, the translate page has both cases, and every
relative link resolves, and nothing is loaded from another host (owner decision 31: no web fonts, scripts,
styles or images from elsewhere; only <a href> links may leave the site). It also checks the SEO basics: a unique <title> and meta description per page and language, one h1 with
headings in order, alt on every image, page weight, Open Graph/Twitter tags, the SoftwareApplication JSON-LD on
home, and with a site URL the canonical and hreflang links (6 languages + x-default, reciprocal), og:url/og:image,
sitemap.xml and robots.txt; without one, nothing absolute in a <head> and no sitemap or robots.txt.
It prints the per-language native-review status (web:<key> lines in
translations/<lang>/reviewed.txt) without blocking.

Template syntax: {{t:key}} text (HTML-escaped; **bold**; {email} becomes a mailto link isolated as
LTR), {{a:key}} plain text for attributes, {{v:name}} a builder value, {{link:page}} a relative
link to a page in the same language. In strings, {app:key} is the app's own label from
translations/<lang>/app.tsv ({app:key|label}: the part before the first ":").
"""
import argparse
import datetime
import html
import json
import os
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
TRANSLATIONS = os.path.join(ROOT, 'translations')
TEMPLATES = os.path.join(SRC, 'templates')
STYLE = os.path.join(SRC, 'style.css')
LOGO = os.path.join(SRC, 'amalino.svg')
OG_IMAGE = os.path.join(SRC, 'og-image.png')  # 1200x630
DEFAULT_OUT = os.path.join(SRC, 'dist')
# The language a visitor chose in a language menu (localStorage, not a cookie).
LANG_KEY = 'amalino.lang'

LOCALES = ['en', 'da', 'ru', 'uk', 'ar', 'es']
RTL = {'ar'}
# Open Graph locales (language_TERRITORY, as Facebook lists them).
OG_LOCALES = {'en': 'en_US', 'da': 'da_DK', 'ru': 'ru_RU', 'uk': 'uk_UA', 'ar': 'ar_AR', 'es': 'es_ES'}
ENDONYMS = {'en': 'English', 'da': 'Dansk', 'ru': 'Русский', 'uk': 'Українська', 'ar': 'العربية', 'es': 'Español'}

# page id -> (template, path below the language folder, nav label key, title key, description key)
PAGES = {
    'home': ('home.html', '', 'nav.home', 'home.title', 'home.meta'),
    'about': ('about.html', 'about', 'nav.about', 'about.title', 'about.meta'),
    'translate': ('translate.html', 'translate', 'nav.translate', 'tr.title', 'tr.meta'),
    'privacy': ('privacy.html', 'privacy', 'nav.privacy', 'pr.title', 'pr.meta'),
}

# The two static language pickers: (folder, label key per language). They are the x-default of the home
# and translate pages; about and privacy have no picker, so their x-default is the English page.
PICKERS = (('', 'home.h1'), ('translate', 'nav.translate'))

# Page weight (decision 31 keeps everything self-hosted; this keeps it small): per HTML page and the whole site.
MAX_PAGE_BYTES = 40_000
MAX_SITE_BYTES = 600_000

# The public repository of the website, manual and translations (owner decision 33, relaxed 2026-10-14). Pages
# link to it with [[link text]] in a string; no other github.com link is allowed.
REPO_URL = 'https://github.com/amalino-app/amalino.app'
CODE_ON_GITHUB = (r'(?:\bcode|\bkode|код|código|الكود|الشيفرة)[^.!?]{0,40}github'
                  r'|github[^.!?]{0,40}(?:\bcode|\bkode|код|código|الكود|الشيفرة)')

# Forbidden on every public page (owner decisions 4 and 8; plan DEC-010, DEC-011, DEC-017,
# INTEGRATION-019). Case-insensitive regular expressions matched on the visible text (tags stripped,
# plus <title>, meta description and alt text). Access methods are matched as phrases, so "switch on"
# or "switch languages" pass; organisations as word stems. ALL applies to every language.
FORBIDDEN = {
    # GitHub may be named and linked (decision 33, relaxed 2026-10-14: the website, manual and translations are
    # there); the app's code is never presented as being on GitHub or open.
    'ALL': [r'open[\s-]?source', r'source code', CODE_ON_GITHUB],
    'en': [r'school', r'teacher', r'therap', r'specialist', r'organi[sz]ation', r'clinic', r'institution', r'kindergarten',
           r'switch access', r'switch scanning', r'switch control', r'accessibility switch', r'external switch',
           r'head movement', r'head tracking', r'head mouse', r'eye gaze', r'eye[\s-]tracking', r'eye tracker',
           r'external pointer', r'pointer'],
    'da': [r'skole', r'lærere', r'læreren', r'lærerne', r'terapeut', r'terapi', r'specialist', r'fagfolk', r'fagperson', r'organisation', r'klinik',
           r'institution', r'pædagog', r'børnehave',
           r'kontaktstyring', r'kontaktbetjening', r'kontakt-?scanning', r'scanning', r'hovedbevægelse',
           r'hovedstyring', r'øjenstyring', r'blikstyring', r'øjenbevægelse', r'pointer', r'musemarkør',
           r'åben kildekode', r'kildekode'],
    'ru': [r'школ', r'учител', r'педагог', r'терапи', r'терапевт', r'специалист', r'логопед', r'организац', r'клиник',
           r'учрежден', r'детск\w* сад',
           r'переключател', r'сканировани', r'движени\w* голов', r'взгляд', r'отслеживани\w* глаз',
           r'указател', r'открыт\w* (исходн\w* )?код', r'исходн\w* код'],
    'uk': [r'школ', r'вчител', r'учител', r'педагог', r'терапі', r'терапевт', r'фахів', r'спеціаліст', r'логопед', r'організаці',
           r'клінік', r'дитяч\w* садок',
           r'перемикач', r'сканування', r'рух\w* голов', r'погляд', r'відстежен\w* оч', r'вказівник',
           r'відкрит\w* (вихідн\w* )?код', r'вихідн\w* код'],
    'ar': [r'مدرس', r'معلم', r'مدارس', r'معالج', r'أخصائي', r'اختصاصي', r'منظمة', r'منظمات', r'مؤسسة', r'مؤسسات', r'عيادة', r'روضة',
           r'مفتاح التبديل', r'مفاتيح التبديل', r'المفاتيح الخارجية', r'حركة الرأس', r'حركات الرأس', r'تتبع العين',
           r'تتبع النظر', r'نظرة العين', r'بالنظر', r'المؤشر الخارجي', r'مؤشر خارجي',
           r'مفتوح المصدر', r'المصدر المفتوح', r'الشيفرة المصدرية', r'الكود المصدري'],
    'es': [r'escuela', r'colegio', r'maestr', r'profesor', r'docente', r'terapeut', r'terapia', r'especialista', r'logoped',
           r'organizaci', r'clínica', r'institución', r'guardería',
           r'pulsador', r'barrido', r'conmutador', r'movimiento\w* de (la )?cabeza', r'mirada',
           r'seguimiento ocular', r'puntero', r'código abierto', r'código fuente'],
}


# The privacy page names GitHub (github.com) as the host the voice files download from, in exactly this phrase
# per language (owner decisions 30 and 33). Since 2026-10-14 GitHub may be named anywhere, but the app's code is
# never presented as being on GitHub or as open source. Lower case; matched on the visible text of the privacy pages only.
# There is no exception for therapists or specialists any more (owner decision 32).
ALLOWED_PRIVACY = {
    'en': 'github (github.com), where the voice files are kept',
    'da': 'github (github.com), hvor stemmefilerne ligger',
    'ru': 'github (github.com), где хранятся файлы голосов',
    'uk': 'github (github.com), де зберігаються файли голосів',
    'ar': 'github (github.com)، حيث تُحفظ ملفات الأصوات',
    'es': 'github (github.com), donde se guardan los archivos de voz',
}

# Self-hosted only (owner decision 31): no fonts, scripts, styles, images or frames from other hosts.
# Only <a href> may point elsewhere (mailto and the configured site), plus canonical/hreflang <link>s
# to the configured site URL.
EXTERNAL_TAG = re.compile(r'<(link|script|img|source|iframe|embed|object|video|audio)\b[^>]*?'
                          r'\b(?:href|src|data|srcset)\s*=\s*["\']?\s*((?:https?:)?//[^"\'\s>]+)', re.I)
EXTERNAL_CSS = re.compile(r'(@import\s+(?:url\()?\s*["\']?\s*(?:https?:)?//[^"\')\s;]+|'
                          r'url\(\s*["\']?\s*(?:https?:)?//[^"\')\s]+)', re.I)


class BuildError(Exception):
    pass


# ---------------------------------------------------------------- inputs

def load_table(path):
    """[(line number, key, text)] of a translations file (key<TAB>text, # comments)."""
    out = []
    with open(path, encoding='utf-8') as f:
        for n, line in enumerate(f, 1):
            line = line.rstrip('\n')
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) != 2:
                raise BuildError(f'{path}:{n}: expected key<TAB>text, got {len(parts)} columns')
            out.append((n, parts[0], parts[1]))
    return out


def load_strings(folder=TRANSLATIONS, name='website.tsv'):
    """{key: {locale: text}} from translations/<lang>/website.tsv. Every English key needs text in every
    language, and no language may have a key English doesn't have."""
    rows = {}
    for loc in LOCALES:
        path = os.path.join(folder, loc, name)
        seen = set()
        for n, key, text in load_table(path):
            if key in seen:
                raise BuildError(f'{path}:{n}: duplicate key {key}')
            seen.add(key)
            if loc != 'en' and key not in rows:
                raise BuildError(f'{path}:{n}: {key} is not in the English file')
            if not text.strip():
                raise BuildError(f'{path}:{n}: {key} has no text')
            rows.setdefault(key, {})[loc] = text
    for key, texts in rows.items():
        missing = [loc for loc in LOCALES if loc not in texts]
        if missing:
            raise BuildError(f'{key} has no text for {", ".join(missing)}')
    return rows


def load_app_strings(folder=TRANSLATIONS):
    """The app's UI strings, for {app:key} feature labels ({key: {locale: text}})."""
    rows = {}
    for loc in LOCALES:
        path = os.path.join(folder, loc, 'app.tsv')
        if os.path.exists(path):
            for _n, key, text in load_table(path):
                rows.setdefault(key, {})[loc] = text
    return {k: v for k, v in rows.items() if len(v) == len(LOCALES)}


def load_reviewed(folder=TRANSLATIONS):
    """{locale: set(web keys)} from the web:<key> lines of translations/<lang>/reviewed.txt."""
    done = {loc: set() for loc in LOCALES}
    for loc in LOCALES:
        path = os.path.join(folder, loc, 'reviewed.txt')
        if not os.path.exists(path):
            continue
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('web:'):
                    done[loc].add(line[4:])
    return done


def clean_email(value):
    e = (value or '').strip()
    return e if '@' in e and ' ' not in e else ''


def clean_donate(value):
    """A donation page (Buy Me a Coffee, Ko-fi, ...): https:// with a host, kept as given; else empty."""
    u = (value or '').strip()
    return u if re.match(r'^https://[^/\s"\'<>]+(/[^\s"\'<>]*)?$', u) else ''


def clean_site(value):
    u = (value or '').strip().rstrip('/')
    m = re.match(r'^https://([^/\s]+)(/\S*)?$', u)
    return u if m else ''


# ---------------------------------------------------------------- rendering

def page_path(page):
    sub = PAGES[page][1]
    return f'{sub}/index.html' if sub else 'index.html'


def rel_root(page):
    """Relative prefix from a language page back to the site root."""
    return '../../' if PAGES[page][1] else '../'


class Renderer:
    def __init__(self, strings, email, site, app=None, donate=''):
        self.strings = strings
        self.app = app if app is not None else load_app_strings()
        self.email = email
        self.site = site
        self.donate = donate
        self.used = set()

    def text(self, key, loc):
        if key not in self.strings:
            raise BuildError(f'unknown string key {key!r}')
        self.used.add(key)
        return self.app_labels(self.strings[key][loc], key, loc)

    def app_labels(self, text, key, loc):
        """{app:key} -> the app's label in this language; {app:key|label} -> its part before the first ':'."""
        def label(m):
            name, mod = m.group(1), m.group(2)
            if name not in self.app:
                raise BuildError(f'{key}: unknown app string {name!r}')
            value = self.app[name][loc]
            if mod == 'label':
                value = value.split(':')[0]
            if '{' in value:
                raise BuildError(f'{key}: app string {name} has a placeholder; use |label')
            return value.strip()
        return re.sub(r'\{app:([A-Za-z0-9_.\-]+)(?:\|(label))?\}', label, text)

    def html_text(self, key, loc):
        s = html.escape(self.text(key, loc), quote=False)
        if loc in RTL:
            # Latin runs (names, "OK?") stay one left-to-right unit, so a trailing "?" or "." keeps its place.
            s = re.sub(r'(?<![{A-Za-z0-9_])(?!email\})[A-Za-z](?:[A-Za-z0-9_\-]|\.(?=[A-Za-z0-9]))*'
                       r'(?:\s+[A-Za-z](?:[A-Za-z0-9_\-]|\.(?=[A-Za-z0-9]))*)*\??',
                       lambda m: f'<bdi dir="ltr">{m.group(0)}</bdi>', s)
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'\[\[(.+?)\]\]', lambda m: f'<a href="{REPO_URL}" rel="noopener">{m.group(1)}</a>', s)
        if '{email}' in s:
            if not self.email:
                raise BuildError(f'{key} needs the e-mail; put it inside {{{{#email}}}}...{{{{/email}}}}')
            e = html.escape(self.email)
            s = s.replace('{email}', f'<bdi dir="ltr"><a href="mailto:{e}">{e}</a></bdi>')
        return s

    def plain(self, key, loc):
        s = self.text(key, loc).replace('**', '').replace('[[', '').replace(']]', '')
        if '{email}' in s:
            raise BuildError(f'{key} has {{email}} and cannot be used as plain text')
        return html.escape(s, quote=True)

    def sections(self, tpl):
        flags = {'email': bool(self.email), 'site': bool(self.site), 'donate': bool(self.donate)}

        def keep(m):
            return m.group(2) if flags[m.group(1)] else ''
        return re.sub(r'\{\{#(email|site|donate)\}\}(.*?)\{\{/\1\}\}', keep, tpl, flags=re.S)

    def render(self, tpl, loc, values, page=None):
        tpl = self.sections(tpl)

        def sub(m):
            kind, name = m.group(1), m.group(2)
            if kind == 't':
                return self.html_text(name, loc)
            if kind == 'a':
                return self.plain(name, loc)
            if kind == 'link':
                if name not in PAGES:
                    raise BuildError(f'unknown page {name!r}')
                return rel_root(page) + f'{loc}/{page_path(name)}'
            if name == 'donate' and name not in values:
                return html.escape(self.donate, quote=True)
            if name not in values:
                raise BuildError(f'unknown value {name!r}')
            return values[name]
        out = re.sub(r'\{\{(t|a|v|link):([A-Za-z0-9_.\-]+)\}\}', sub, tpl)
        if '{{' in out:
            raise BuildError(f'unrendered template tag near {out[out.index("{{"):][:40]!r}')
        return out


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def site_url(site, loc, page):
    """Absolute URL of a page; loc None is the page's language picker (home and translate only)."""
    sub = PAGES[page][1]
    tail = f'{sub}/' if sub else ''
    return f'{site}/{tail}' if loc is None else f'{site}/{loc}/{tail}'


def x_default(site, page):
    """The x-default of a page's language cluster: its picker, or the English page when it has none."""
    return site_url(site, None if page in ('home', 'translate') else 'en', page)


def alternates(site, page):
    """[(hreflang, url)] of a page in every language plus x-default (the same list on every member)."""
    return [(loc, site_url(site, loc, page)) for loc in LOCALES] + [('x-default', x_default(site, page))]


def head_links(site, loc, page):
    """Canonical and hreflang links (only with a site URL: they must be absolute). loc None = the picker."""
    if not site:
        return ''
    lines = [f'<link rel="canonical" href="{html.escape(site_url(site, loc, page))}">']
    for lang, url in alternates(site, page):
        lines.append(f'<link rel="alternate" hreflang="{lang}" href="{html.escape(url)}">')
    return '\n'.join(lines) + '\n'


def share_meta(r, site, loc, page, title, desc):
    """Open Graph and Twitter card tags. og:url and the image need absolute URLs, so they come only with a
    site URL; without one the card still has a title, a description and the locales."""
    own = loc or 'en'
    tags = [('property', 'og:type', 'website'), ('property', 'og:site_name', 'Amalino'),
            ('property', 'og:title', title), ('property', 'og:description', desc),
            ('property', 'og:locale', OG_LOCALES[own])]
    tags += [('property', 'og:locale:alternate', OG_LOCALES[o]) for o in LOCALES if o != own]
    tags.append(('name', 'twitter:card', 'summary_large_image' if site else 'summary'))
    if site:
        image = html.escape(f'{site}/assets/og-image.png')
        tags += [('property', 'og:url', html.escape(site_url(site, loc, page))), ('property', 'og:image', image),
                 ('property', 'og:image:type', 'image/png'), ('property', 'og:image:width', '1200'),
                 ('property', 'og:image:height', '630'), ('property', 'og:image:alt', r.plain('og.imageAlt', own)),
                 ('name', 'twitter:image', image), ('name', 'twitter:image:alt', r.plain('og.imageAlt', own))]
    tags += [('name', 'twitter:title', title), ('name', 'twitter:description', desc)]
    return ''.join(f'<meta {kind}="{name}" content="{value}">\n' for kind, name, value in tags)


def json_ld(r, site, loc):
    """schema.org SoftwareApplication for a home page. Only what is true today: free, two platforms, six
    languages. No rating, no review, no store link and no download URL until they exist; no author name
    (the site tells the story in the first person without one)."""
    data = {
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        'name': 'Amalino',
        'description': r.text('home.meta', loc),
        'operatingSystem': 'iOS, Android',
        'applicationCategory': 'EducationalApplication',
        'applicationSubCategory': 'AAC',
        'isAccessibleForFree': True,
        'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'},
        'inLanguage': list(LOCALES),
    }
    if site:
        data['url'] = site_url(site, loc, 'home')
        data['image'] = f'{site}/assets/og-image.png'
    text = json.dumps(data, ensure_ascii=False, indent=1).replace('</', '<\\/')
    return f'<script type="application/ld+json">\n{text}\n</script>\n'


def lastmod():
    """The sitemap date: the last commit of the site or the translations (today without git)."""
    try:
        out = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', 'site', 'translations'],
                             cwd=ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        out = ''
    return out if re.match(r'^\d{4}-\d{2}-\d{2}$', out) else datetime.date.today().isoformat()


def sitemap(site, date):
    """sitemap.xml: every language page and both pickers, each with its cluster's xhtml:link alternates."""
    entries = [(loc, page) for page in PAGES for loc in LOCALES] + [(None, p) for p in ('home', 'translate')]
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for loc, page in entries:
        lines.append(f'  <url>\n    <loc>{html.escape(site_url(site, loc, page))}</loc>\n    <lastmod>{date}</lastmod>')
        for lang, url in alternates(site, page):
            lines.append(f'    <xhtml:link rel="alternate" hreflang="{lang}" href="{html.escape(url)}"/>')
        lines.append('  </url>')
    lines.append('</urlset>')
    return '\n'.join(lines) + '\n'


def redirect_script(root, target):
    """The picker pages' redirect: the language chosen before (localStorage), else the first of the
    browser's languages the site has (region ignored: pt-BR -> pt), else English. `root` leads from the
    picker back to the site root, `target` is the page's path below a language folder; the picker list
    stays for browsers without script."""
    langs = json.dumps(LOCALES)
    return ('<script>(function(){var L=' + langs + ',p=null;try{p=localStorage.getItem("' + LANG_KEY + '")}catch(e){}'
            'if(L.indexOf(p)<0){p=null;var n=navigator.languages||[navigator.language||""];'
            'for(var i=0;i<n.length&&!p;i++){var c=String(n[i]).toLowerCase().split("-")[0];if(L.indexOf(c)>=0)p=c}}'
            'location.replace("' + root + '"+(p||"en")+"/' + target + '")})();</script>')


# Every language page: a click on a language link (header menu or footer list) remembers that language.
REMEMBER_SCRIPT = ('<script>document.addEventListener("click",function(e){var a=e.target.closest&&'
                   'e.target.closest("a[data-lang]");if(a)try{localStorage.setItem("' + LANG_KEY + '",'
                   'a.getAttribute("data-lang"))}catch(x){}});</script>')


def build(out, email='', site='', strings=None, quiet=False, donate=''):
    """Builds the site into `out` (replacing it). Returns a summary dict used by --check and tests."""
    strings = strings if strings is not None else load_strings()
    reviewed = load_reviewed()
    r = Renderer(strings, email, site, donate=donate)
    r.used.add('og.imageAlt')  # the share image's alt text; on the pages only with a site URL (og:image is absolute)
    layout = read(os.path.join(TEMPLATES, 'layout.html'))
    picker = read(os.path.join(TEMPLATES, 'picker.html'))

    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, 'assets'))
    shutil.copyfile(STYLE, os.path.join(out, 'assets', 'style.css'))
    shutil.copyfile(LOGO, os.path.join(out, 'assets', 'amalino.svg'))
    shutil.copyfile(OG_IMAGE, os.path.join(out, 'assets', 'og-image.png'))

    status = {}
    for loc in LOCALES:
        checked = len(reviewed[loc] & set(strings))
        status[loc] = 'source' if loc == 'en' else f'{checked}/{len(strings)} checked'
        draft = loc != 'en' and checked < len(strings)
        banner = (f'<div class="draft-banner" role="note"><div class="wrap"><p>{r.html_text("draftBanner", loc)}'
                  f'</p></div></div>') if draft else ''
        for page, (tpl_name, _sub, nav_key, title_key, desc_key) in PAGES.items():
            root = rel_root(page)
            nav = []
            for p in PAGES:
                cur = ' aria-current="page"' if p == page else ''
                nav.append(f'<li><a href="{root}{loc}/{page_path(p)}"{cur}>{r.html_text(PAGES[p][2], loc)}</a></li>')
            langs = []
            for other in LOCALES:
                cur = ' aria-current="true"' if other == loc else ''
                d = 'rtl' if other in RTL else 'ltr'
                langs.append(f'<li><a href="{root}{other}/{page_path(page)}" lang="{other}" hreflang="{other}" '
                             f'dir="{d}" data-lang="{other}"{cur}>{ENDONYMS[other]}</a></li>')
            content = r.render(read(os.path.join(TEMPLATES, tpl_name)), loc, {}, page)
            title, desc = r.plain(title_key, loc), r.plain(desc_key, loc)
            head = head_links(site, loc, page) + share_meta(r, site, loc, page, title, desc)
            if page == 'home':
                head += json_ld(r, site, loc)
            values = {
                'lang': loc, 'dir': 'rtl' if loc in RTL else 'ltr', 'root': root, 'title': title,
                'description': desc, 'head_links': head.rstrip('\n'),
                'nav': ''.join(nav), 'lang_links': ''.join(langs), 'draft_banner': banner, 'content': content,
                'lang_current': f'<span lang="{loc}" dir="{"rtl" if loc in RTL else "ltr"}">{ENDONYMS[loc]}</span>',
                'remember_script': REMEMBER_SCRIPT,
            }
            write(os.path.join(out, loc, page_path(page)), r.render(layout, loc, values, page))

    # Static language pickers: / and /translate/ (the app links {site}/{lang}/translate/).
    for sub, label_key in PICKERS:
        root = '../' if sub else ''
        target = 'translate/index.html' if sub else 'index.html'
        items = []
        for loc in LOCALES:
            d = 'rtl' if loc in RTL else 'ltr'
            items.append(f'<li><a href="{root}{loc}/{target}" lang="{loc}" hreflang="{loc}" dir="{d}">'
                         f'<strong>{ENDONYMS[loc]}</strong><span>{r.plain(label_key, loc)}</span></a></li>')
        choose = ' · '.join(f'<span lang="{loc}" dir="{"rtl" if loc in RTL else "ltr"}">{r.plain("pick.choose", loc)}'
                            f'</span>' for loc in LOCALES)
        page = 'translate' if sub else 'home'
        title = r.plain('pick.trTitle' if sub else 'pick.title', 'en')
        desc = r.plain('pick.trMeta' if sub else 'pick.meta', 'en')
        links = head_links(site, None, page) + share_meta(r, site, None, page, title, desc)
        values = {
            'root': root, 'title': title, 'description': desc,
            'head_links': links.rstrip('\n'), 'heading': 'Amalino' if not sub else r.plain('tr.h1', 'en'),
            'choose': choose, 'items': ''.join(items), 'redirect': redirect_script(root, target),
        }
        write(os.path.join(out, target), r.render(picker, 'en', values))

    if site:
        write(os.path.join(out, 'sitemap.xml'), sitemap(site, lastmod()))
        write(os.path.join(out, 'robots.txt'), f'User-agent: *\nAllow: /\n\nSitemap: {site}/sitemap.xml\n')
        # GitHub Pages serves the site at its custom domain from this file.
        write(os.path.join(out, 'CNAME'), re.match(r'^https://([^/]+)', site).group(1) + '\n')

    referenced = set(re.findall(r'\{\{[ta]:([A-Za-z0-9_.\-]+)\}\}', ''.join(
        read(os.path.join(TEMPLATES, n)) for n in os.listdir(TEMPLATES) if n.endswith('.html'))))
    unused = sorted(set(strings) - r.used - referenced)
    if not quiet:
        print(f'Built {len(LOCALES)} languages x {len(PAGES)} pages + 2 pickers into {os.path.relpath(out, ROOT)}'
              f' (e-mail {"set" if email else "empty"}, site {"set" if site else "empty"},'
              f' donation link {"set" if donate else "empty"})')
        print('Native review (web:<key> in translations/<lang>/reviewed.txt): ' +
              ', '.join(f'{loc} {status[loc]}' for loc in LOCALES))
        if unused:
            print('Unused string keys: ' + ', '.join(unused))
    return {'status': status, 'unused': unused}


# ---------------------------------------------------------------- checks

# Meta tags whose content is text people read (search results, share cards); the guard checks them too.
SHARE_TEXT = {'description', 'og:title', 'og:description', 'og:image:alt', 'twitter:title', 'twitter:description',
              'twitter:image:alt'}


class _Head(HTMLParser):
    """The SEO view of a page: <title>, meta tags, <link>s, JSON-LD blocks, headings in order and <img>s."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.meta, self.links, self.ld, self.headings, self.imgs = '', [], [], [], [], []
        self._in = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'title':
            self._in = 'title'
        elif tag == 'meta':
            self.meta.append(a)
        elif tag == 'link':
            self.links.append(a)
        elif tag == 'script' and a.get('type') == 'application/ld+json':
            self._in = 'ld'
            self.ld.append('')
        elif re.fullmatch(r'h[1-6]', tag):
            self.headings.append(int(tag[1]))
        elif tag == 'img':
            self.imgs.append(a)

    def handle_endtag(self, tag):
        if tag in ('title', 'script'):
            self._in = None

    def handle_data(self, data):
        if self._in == 'title':
            self.title += data
        elif self._in == 'ld':
            self.ld[-1] += data

    def metas(self, key):
        return [m.get('content') or '' for m in self.meta if key in (m.get('name'), m.get('property'))]

    def alternates(self):
        return [(l.get('hreflang'), l.get('href')) for l in self.links
                if (l.get('rel') or '').lower() == 'alternate' and l.get('hreflang')]

    def canonical(self):
        return [l.get('href') for l in self.links if (l.get('rel') or '').lower() == 'canonical']


def seo(page_html):
    p = _Head()
    p.feed(page_html)
    return p


class _Text(HTMLParser):
    """Collects the visible text of a page plus <title>, meta description and alt text."""

    INLINE = {'a', 'bdi', 'strong', 'em', 'b', 'i', 'span', 'abbr', 'code', 'small'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag not in self.INLINE:
            self.parts.append(' ')
        if tag in ('script', 'style'):
            self.skip += 1
        if tag == 'meta' and (a.get('name') or a.get('property') or '') in SHARE_TEXT:
            self.parts.append(' ' + (a.get('content') or '') + ' ')
        if a.get('alt'):
            self.parts.append(' ' + a['alt'] + ' ')

    def handle_endtag(self, tag):
        if tag not in self.INLINE:
            self.parts.append(' ')
        if tag in ('script', 'style') and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def visible_text(page_html):
    p = _Text()
    p.feed(page_html)
    return ' '.join(''.join(p.parts).split())


def page_lang(page_html):
    m = re.search(r'<html[^>]*\blang="([^"]+)"', page_html)
    return m.group(1) if m else 'en'


def forbidden_found(page_html, lang=None, page=None):
    """Forbidden phrases in a page: those of ALL, English, and the page's own language. Only a privacy page
    (page='privacy') keeps the voice file host line of ALLOWED_PRIVACY out of the check."""
    text = visible_text(page_html).lower()
    lang = lang or page_lang(page_html)
    langs = ['ALL', 'en'] + ([lang] if lang in FORBIDDEN and lang != 'en' else [])
    if lang not in FORBIDDEN:  # pickers and mixed pages: every language
        langs = list(FORBIDDEN)
    if page == 'privacy' and lang in ALLOWED_PRIVACY:
        text = text.replace(ALLOWED_PRIVACY[lang], ' ')
    found = []
    for lg in langs:
        for pat in FORBIDDEN[lg]:
            m = re.search(pat, text, flags=re.I)
            if m:
                found.append(m.group(0))
    return found


def external_refs(text, site=''):
    """URLs of resources loaded from other hosts (HTML tags, CSS @import/url()). Canonical and hreflang
    <link>s to the configured site are allowed; <a href> links are not resources and are not checked."""
    found = []
    for m in EXTERNAL_TAG.finditer(text):
        tag, url = m.group(1).lower(), m.group(2)
        rel = re.search(r'\brel\s*=\s*["\']?(canonical|alternate)\b', m.group(0), re.I)
        if tag == 'link' and rel and site and url.startswith(site + '/'):
            continue
        found.append(url)
    found += [m.group(0) for m in EXTERNAL_CSS.finditer(text)]
    return found


def main_part(page_html):
    m = re.search(r'<main[^>]*>(.*)</main>', page_html, flags=re.S)
    return m.group(1) if m else page_html


def check(out, strings, email, site='', donate=''):
    errors = []

    def expect(cond, msg):
        if not cond:
            errors.append(msg)

    files = [os.path.join(loc, page_path(p)) for loc in LOCALES for p in PAGES] + ['index.html', 'translate/index.html']
    for f in files + ['assets/style.css', 'assets/amalino.svg']:
        expect(os.path.isfile(os.path.join(out, f)), f'missing {f}')
    if errors:
        return errors

    for f in files:
        path = os.path.join(out, f)
        page = read(path)
        loc = f.split('/')[0] if f.split('/')[0] in LOCALES else None
        if loc:
            want = 'rtl' if loc in RTL else 'ltr'
            expect(re.search(rf'<html lang="{loc}" dir="{want}">', page), f'{f}: needs <html lang="{loc}" dir="{want}">')
        kind = next((p for p in PAGES if loc and f == os.path.join(loc, page_path(p))), None)
        for term in forbidden_found(page, loc or 'mixed', kind):
            errors.append(f'{f}: forbidden term "{term}"')
        for url in external_refs(page, site):
            errors.append(f'{f}: external resource {url} (self-hosted only)')
        for ref in re.findall(r'href="([^"]*github\.com[^"]*)"', page):
            expect(ref.startswith(REPO_URL), f'{f}: GitHub link {ref} (only {REPO_URL})')
        if loc:
            expect(f'<p class="footer-repo"><a href="{REPO_URL}"' in page, f'{f}: footer link to the repository missing')
        for leftover in ('{{', '{email}', '**', '{app:', '[[', ']]'):
            expect(leftover not in page, f'{f}: leftover {leftover!r}')
        # Owner decision 31: no cookies. The language choice is in localStorage only.
        expect('cookie' not in page.lower(), f'{f}: mentions cookies in its markup or script')
        if loc:
            menu = re.search(r'<details class="lang-menu">(.*?)</details>', page, flags=re.S)
            expect(menu, f'{f}: needs the header language menu')
            if menu:
                for other in LOCALES:
                    expect(f'data-lang="{other}"' in menu.group(1), f'{f}: language menu misses {other}')
            expect(REMEMBER_SCRIPT in page, f'{f}: language links must remember the choice')
        else:
            expect('location.replace(' in page and LANG_KEY in page, f'{f}: the picker needs its language redirect')
        if not email:
            expect('mailto:' not in page, f'{f}: mailto link while the e-mail is empty')
        if loc and donate:
            link = f'<a href="{html.escape(donate, quote=True)}" rel="noopener">'
            expect(f'<p class="footer-support">{link}' in page, f'{f}: footer support link missing')
            if kind == 'about':
                expect('id="support"' in page and f'class="button" href="{html.escape(donate, quote=True)}" rel="noopener"'
                       in page, f'{f}: support section missing')
        elif not donate:
            expect('footer-support' not in page and 'id="support"' not in page,
                   f'{f}: donation link while the setting is empty')
        # Relative links and assets must resolve inside the built site.
        for ref in re.findall(r'(?:href|src)="([^"]+)"', page):
            if re.match(r'^(https?:|mailto:|#)', ref):
                continue
            target = os.path.normpath(os.path.join(os.path.dirname(path), ref))
            expect(target.startswith(os.path.abspath(out)) and os.path.isfile(target), f'{f}: broken link {ref}')

    for root, _dirs, names in os.walk(out):
        for n in names:
            if n.endswith('.css'):
                for url in external_refs(read(os.path.join(root, n)), site):
                    errors.append(f'{os.path.relpath(os.path.join(root, n), out)}: external resource {url}')

    errors += check_seo(out, files, site)

    for loc in LOCALES:
        promise = strings['freeTitle'][loc]
        expect(strings['free'][loc].startswith(promise), f'strings: free ({loc}) must start with freeTitle')
        for p in ('home', 'about'):
            body = main_part(read(os.path.join(out, loc, page_path(p))))
            expect(promise in visible_text(body), f'{loc}/{page_path(p)}: free promise missing')
        tr = read(os.path.join(out, loc, page_path('translate')))
        tr_text = visible_text(tr)
        expect('id="improve"' in tr and 'id="add"' in tr, f'{loc}/translate: needs both cases (#improve, #add)')
        for key in ('tr.improveTitle', 'tr.improve2', 'tr.addTitle', 'tr.add1', 'tr.addHonest'):
            expect(visible_text(Renderer(strings, email or 'x@y', '').html_text(key, loc)) in tr_text,
                   f'{loc}/translate: missing {key}')
        if email:
            for p in ('translate', 'privacy', 'about'):
                expect(f'mailto:{email}' in read(os.path.join(out, loc, page_path(p))),
                       f'{loc}/{page_path(p)}: e-mail missing')
    return errors


def check_seo(out, files, site):
    """Titles, descriptions, hreflang, canonical, share cards, JSON-LD, headings, alt text, page weight and
    (with a site URL) sitemap.xml and robots.txt. Without a site URL nothing absolute may be in a <head>."""
    errors = []

    def expect(cond, msg):
        if not cond:
            errors.append(msg)

    pages = {f: seo(read(os.path.join(out, f))) for f in files}
    seen = {}  # (language, 'title'|'description', text) -> file
    for f, h in pages.items():
        loc = f.split('/')[0] if f.split('/')[0] in LOCALES else None
        desc = h.metas('description')
        expect(h.title.strip() and len(desc) == 1 and desc[0].strip(), f'{f}: needs a <title> and one meta description')
        for kind, text in (('title', h.title.strip()), ('description', (desc or [''])[0])):
            key = (loc or 'picker', kind, text)
            expect(key not in seen, f'{f}: same {kind} as {seen.get(key)}')
            seen[key] = f
        expect(h.headings.count(1) == 1 and h.headings[:1] == [1], f'{f}: needs exactly one h1, first')
        for a, b in zip(h.headings, h.headings[1:]):
            expect(b <= a + 1, f'{f}: heading h{a} is followed by h{b}')
        for img in h.imgs:
            expect('alt' in img, f'{f}: <img src="{img.get("src")}"> has no alt')
        expect(os.path.getsize(os.path.join(out, f)) <= MAX_PAGE_BYTES, f'{f}: over {MAX_PAGE_BYTES} bytes')
        for key in ('og:title', 'og:description', 'og:type', 'og:locale', 'twitter:card'):
            expect(len(h.metas(key)) == 1, f'{f}: needs one {key}')
        expect(h.metas('og:locale') == [OG_LOCALES[loc or 'en']], f'{f}: wrong og:locale')
        expect(len(h.metas('og:locale:alternate')) == len(LOCALES) - 1, f'{f}: needs og:locale:alternate for the others')
        for block in h.ld:
            try:
                data = json.loads(block)
                expect(data.get('@type') == 'SoftwareApplication' and data.get('name') == 'Amalino' and
                       data.get('offers', {}).get('price') == '0', f'{f}: JSON-LD is not the Amalino app')
                expect(not {'aggregateRating', 'review', 'downloadUrl', 'installUrl'} & set(data),
                       f'{f}: JSON-LD claims ratings, reviews or store links')
            except ValueError as e:
                errors.append(f'{f}: JSON-LD does not parse ({e})')
        if loc and f == os.path.join(loc, page_path('home')):
            expect(len(h.ld) == 1, f'{f}: needs the SoftwareApplication JSON-LD')
        if site:
            canon = h.canonical()
            expect(len(canon) == 1, f'{f}: needs one canonical link')
            alts = dict(h.alternates())
            expect(sorted(alts) == sorted(LOCALES + ['x-default']), f'{f}: hreflang needs {LOCALES} and x-default')
            expect(canon and canon[0] in alts.values(), f'{f}: canonical is not one of its alternates')
            for key in ('og:url', 'og:image'):
                expect(len(h.metas(key)) == 1, f'{f}: needs {key}')
            expect(h.metas('og:url') == canon[:1], f'{f}: og:url differs from canonical')
            expect(h.metas('og:image') == [f'{site}/assets/og-image.png'], f'{f}: og:image')
        else:
            head = read(os.path.join(out, f)).split('</head>')[0]
            expect(not h.canonical() and not h.alternates(), f'{f}: canonical/hreflang without a site URL')
            expect(not h.metas('og:url') and not h.metas('og:image'), f'{f}: og:url/og:image without a site URL')
            leftover = [u for u in re.findall(r'https?://[^"\s<>]+', head) if u != 'https://schema.org']
            expect(not leftover, f'{f}: absolute URL without a site URL: {leftover[:3]}')

    if site:
        cname = os.path.join(out, 'CNAME')
        expect(os.path.isfile(cname) and read(cname).strip() == re.match(r'^https://([^/]+)', site).group(1),
               'CNAME missing or not the site host')
        # Reciprocity: every page a page names as an alternate exists, names it back, and has that language.
        by_url = {}
        for f, h in pages.items():
            if h.canonical():
                by_url[h.canonical()[0]] = f
        for f, h in pages.items():
            mine = h.canonical()[:1]
            for lang, url in h.alternates():
                other = by_url.get(url)
                expect(other, f'{f}: hreflang {lang} -> {url} is not a built page')
                if not other:
                    continue
                expect(mine and mine[0] in dict(pages[other].alternates()).values(),
                       f'{f}: {other} does not link back')
                if lang != 'x-default':
                    expect(page_lang(read(os.path.join(out, other))) == lang, f'{f}: {url} is not in {lang}')
        errors += check_sitemap(out, site, set(by_url))
    else:
        for name in ('sitemap.xml', 'robots.txt', 'CNAME'):
            expect(not os.path.exists(os.path.join(out, name)), f'{name} without a site URL')

    og = os.path.join(out, 'assets', 'og-image.png')
    expect(os.path.isfile(og), 'missing assets/og-image.png')
    if os.path.isfile(og):
        expect(png_size(og) == (1200, 630), f'assets/og-image.png is not a 1200x630 PNG ({png_size(og)})')
    total = sum(os.path.getsize(os.path.join(d, n)) for d, _ds, ns in os.walk(out) for n in ns)
    expect(total <= MAX_SITE_BYTES, f'site is {total} bytes, over {MAX_SITE_BYTES}')
    return errors


def png_size(path):
    """(width, height) from a PNG's IHDR chunk, or None when the file is not a PNG."""
    with open(path, 'rb') as f:
        head = f.read(24)
    if head[:8] != b'\x89PNG\r\n\x1a\n' or head[12:16] != b'IHDR':
        return None
    return int.from_bytes(head[16:20], 'big'), int.from_bytes(head[20:24], 'big')


def check_sitemap(out, site, page_urls):
    """sitemap.xml parses, lists exactly the built pages with lastmod and their alternates; robots.txt names it."""
    import xml.etree.ElementTree as ET
    errors = []
    path = os.path.join(out, 'sitemap.xml')
    if not os.path.isfile(path):
        return ['missing sitemap.xml']
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as e:
        return [f'sitemap.xml does not parse ({e})']
    ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9', 'x': 'http://www.w3.org/1999/xhtml'}
    locs = []
    for url in root.findall('s:url', ns):
        loc = url.findtext('s:loc', '', ns)
        locs.append(loc)
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', url.findtext('s:lastmod', '', ns)):
            errors.append(f'sitemap.xml: {loc} has no lastmod')
        alts = {l.get('hreflang'): l.get('href') for l in url.findall('x:link', ns)}
        if sorted(alts) != sorted(LOCALES + ['x-default']) or loc not in alts.values():
            errors.append(f'sitemap.xml: {loc} alternates incomplete')
    if sorted(locs) != sorted(page_urls):
        errors.append(f'sitemap.xml: lists {len(locs)} pages, the site has {len(page_urls)}')
    robots = os.path.join(out, 'robots.txt')
    if not os.path.isfile(robots) or f'Sitemap: {site}/sitemap.xml' not in read(robots):
        errors.append('robots.txt missing or does not name the sitemap')
    return errors


# ---------------------------------------------------------------- CLI

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--out', default=DEFAULT_OUT)
    ap.add_argument('--contact-email', default=os.environ.get('OVK_CONTACT_EMAIL', ''))
    ap.add_argument('--site', '--site-url', dest='site_url', default=os.environ.get('OVK_SITE_URL', ''))
    ap.add_argument('--donate-url', default=os.environ.get('OVK_DONATE_URL', ''))
    ap.add_argument('--check', action='store_true', help='validate the built site')
    ap.add_argument('--check-fixture', nargs='+', metavar='FILE', help='only run the forbidden-term guard on files')
    args = ap.parse_args(argv)

    if args.check_fixture:
        bad = 0
        for f in args.check_fixture:
            found = forbidden_found(read(f))
            for term in found:
                print(f'{f}: forbidden term "{term}"')
            for url in external_refs(read(f)):
                print(f'{f}: external resource {url}')
                bad += 1
            bad += len(found)
        if not bad:
            print('no forbidden terms')
        return 1 if bad else 0

    email, site, donate = clean_email(args.contact_email), clean_site(args.site_url), clean_donate(args.donate_url)
    if args.donate_url.strip() and not donate:
        print('warning: --donate-url/OVK_DONATE_URL is not an https:// URL; left out', file=sys.stderr)
    if args.contact_email.strip() and not email:
        print('warning: --contact-email/OVK_CONTACT_EMAIL is not an e-mail address; left out', file=sys.stderr)
    if args.site_url.strip() and not site:
        print('warning: --site-url/OVK_SITE_URL is not an https:// URL; left out', file=sys.stderr)
    try:
        strings = load_strings()
        build(args.out, email, site, strings, donate=donate)
        if args.check:
            errors = check(args.out, strings, email, site, donate)
            for e in errors:
                print('error: ' + e, file=sys.stderr)
            if errors:
                return 1
            print('check: ok')
    except BuildError as e:
        print('error: ' + str(e), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
