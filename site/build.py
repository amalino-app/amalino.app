#!/usr/bin/env python3
"""Builds the static Amalino website.

    python3 site/build.py [--out DIR] [--contact-email ADDR] [--site https://...]
                          [--donate-url https://...] [--check]
    python3 site/build.py --check-fixture FILE [FILE ...]

Sources: translations/<lang>/website.tsv (key, text; English is the source), site/templates/*.html,
site/style.css, site/amalino.svg and site/og-image.png (1200x630).
Output (default site/dist/): {lang}/index.html, {lang}/about/, {lang}/translate/, {lang}/privacy/
for the seven app languages, plus a root index.html and translate/index.html that send the visitor to their
language (the browser's languages, or the one they chose before; a few lines of inline script, no cookies)
and list the languages for browsers without script, assets/ (style, logo, share image) and, with a site
URL, sitemap.xml, robots.txt and the CNAME file GitHub Pages reads. Every page has a language menu in its
header. Links are relative and name index.html, so the build also works from file://.

The contact email and site URL come from --contact-email/--site-url or the environment
(OVK_CONTACT_EMAIL, OVK_SITE_URL), with the app's rules: an email needs an
"@" and no spaces, a site URL must be https://; anything else counts as empty. The donation link comes from
--donate-url or OVK_DONATE_URL (https:// only; website only, never in the app): the about page's "Support
Amalino" section and the footer link. Template blocks {{#email}}...{{/email}}, {{#site}}...{{/site}} and
{{#donate}}...{{/donate}} are left out while the setting is empty; {{v:donate}} is the URL.

--check validates the built site: every page exists with the right lang/dir, no forbidden term
(organisations, untested access methods, open source/GitHub) appears in any page, the free promise is
on home and about, email text appears only when set, the translate page has both cases, and every
relative link resolves, and nothing is loaded from another host (owner decision 31: no web fonts, scripts,
styles or images from elsewhere; only <a href> links may leave the site). It also checks the SEO basics: a unique <title> and meta description per page and language, one h1 with
headings in order, alt on every image, page weight, Open Graph/Twitter tags, the SoftwareApplication JSON-LD on
home, and with a site URL the canonical and hreflang links (7 languages + x-default, reciprocal), og:url/og:image,
sitemap.xml and robots.txt; without one, nothing absolute in a <head> and no sitemap or robots.txt.
It prints the per-language native-review status (web:<key> lines in
translations/<lang>/reviewed.txt for the website, manual:<page> lines for the manual) without blocking; a
translated manual page that isn't listed there shows the draft banner.

Template syntax: {{t:key}} text (HTML-escaped; **bold**; {email} becomes a mailto link isolated as
LTR), {{a:key}} plain text for attributes, {{v:name}} a builder value ({{v:donate}}, {{v:weblate}}, {{v:issues}}, {{v:report_mailto}},
{{v:testers_group}}, {{v:testers_optin}}), {{link:page}} a relative
link to a page in the same language. In strings, {app:key} is the app's own label from
translations/<lang>/app.tsv ({app:key|label}: the part before the first ":"). The manual's Markdown
(manual/<lang>/*.md) uses the same {app:key} for every button, menu and setting it names, so a translated manual
always shows the app's own words.
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
import urllib.parse
from html.parser import HTMLParser

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
TRANSLATIONS = os.path.join(ROOT, 'translations')
TEMPLATES = os.path.join(SRC, 'templates')
STYLE = os.path.join(SRC, 'style.css')
LOGO = os.path.join(SRC, 'amalino.svg')
OG_IMAGE = os.path.join(SRC, 'og-image.png')  # 1200x630
ICONS = os.path.join(SRC, 'icons')  # favicon.ico and PNGs made from the app icon
# Copied into assets/ (favicon.ico goes to the site root, where browsers look for it).
ICON_FILES = ('favicon-16.png', 'favicon-32.png', 'apple-touch-icon.png', 'icon-192.png', 'icon-512.png')
THEME_COLORS = ('#F1F8F3', '#0E1712')  # the page background, light and dark (style.css --bg)
TITLE_MAX, DESCRIPTION_MAX = 60, 155  # what search results show without cutting
DEFAULT_OUT = os.path.join(SRC, 'dist')
# The language a visitor chose in a language menu (localStorage, not a cookie).
LANG_KEY = 'amalino.lang'

LOCALES = ['en', 'da', 'ru', 'uk', 'ar', 'es', 'lt']
RTL = {'ar'}
# Open Graph locales (language_TERRITORY, as Facebook lists them).
# English is written with UK spelling (licence, colour), so its locale is en_GB.
OG_LOCALES = {'en': 'en_GB', 'da': 'da_DK', 'ru': 'ru_RU', 'uk': 'uk_UA', 'ar': 'ar_AR', 'es': 'es_ES', 'lt': 'lt_LT'}
ENDONYMS = {'en': 'English', 'da': 'Dansk', 'ru': 'Русский', 'uk': 'Українська', 'ar': 'العربية', 'es': 'Español', 'lt': 'Lietuvių'}

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
MAX_SITE_BYTES = 700_000  # 600 KB for six languages, raised with the seventh (Lithuanian)
# The manual's HTML pages are counted on their own, per language (they are long text pages; MAX_SITE_BYTES covers
# the website and the shared assets). A manual page may be longer than a website page: Cyrillic and Arabic take two
# bytes a letter, and the longest page (Settings) is about 23 KB in English.
MAX_MANUAL_PAGE_BYTES = 60_000
MAX_MANUAL_HTML_BYTES = 450_000
# The manual's screenshots (manual/<lang>/img/NAME-1x.webp and NAME-2x.webp, published at /<lang>/manual/img/)
# are counted on their own: each file, and all of one language's together (each translated manual has its own
# screenshots in its language, owner 2026-10-20). MAX_SITE_BYTES covers everything else. They are self-hosted
# like everything else (decision 31); full-colour WebP at 1x and 2x (owner 2026-10-20, sharp on Retina screens)
# replaced the 128-colour PNGs and their 150 KB / 3 MB limits.
MAX_IMAGE_BYTES = 250_000
MAX_MANUAL_IMAGE_BYTES = 4_000_000  # per language
MANUAL_IMAGE = re.compile(r'^!\[([^\]]+)\]\((img/[a-z0-9\-]+-1x\.webp)\)$')

# The public repository of the website, manual and translations (owner decision 33, relaxed 2026-10-14). Pages
# link to it with [[link text]] in a string; no other github.com link is allowed.
REPO_URL = 'https://github.com/amalino-app/amalino.app'
# Documents on other hosts a string may link to, by name: [[link text|name]] (the privacy page's website part,
# owner 2026-10-14). Any other link to another host is an error.
OUTSIDE_LINKS = {
    'github-privacy': 'https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement',
    'cloudflare-privacy': 'https://www.cloudflare.com/privacypolicy/',
}
# Hosted Weblate, where volunteers correct the app's screens, the board words and the website (docs/weblate.md):
# the "Help translate" page links to it with {{v:weblate}}. A plain link, followed only when clicked: no widget,
# badge, image or script from Weblate (decision 31).
WEBLATE_URL = 'https://hosted.weblate.org/engage/amalino/'
# "Report a problem" (About, owner 2026-10-21): GitHub's chooser for the repository's issue forms
# (.github/ISSUE_TEMPLATE/, English only). The one outside link to the repository besides REPO_URL itself; the email
# route is a mailto: with a subject and a short checklist in the page's language ({{v:report_mailto}}).
ISSUES_URL = REPO_URL + '/issues/new/choose'
REPORT_CHECKS = ('report.check1', 'report.check2', 'report.check3', 'report.check4')
# "Help test Amalino on Android" (home page, owner 2026-10-23): Google Play's closed test needs at least 12 testers
# opted in for 14 days before production. Testers join the Google Group with the Google account of their Android
# device, then opt in on Google Play's test page. Plain links, followed only when clicked ({{v:testers_group}},
# {{v:testers_optin}}); the only links to Google's sites.
TESTERS_GROUP_URL = 'https://groups.google.com/g/amalino-testers/about'
TESTERS_OPTIN_URL = 'https://play.google.com/apps/testing/app.amalino'
# The user manual: manual/<lang>/index.md and the pages its contents list links to, published at /<lang>/manual/.
# A language without a manual folder links to the English manual.
MANUAL = os.path.join(ROOT, 'manual')
MANUAL_SOURCE = 'en'
# Lithuanian kodas/kodo/kodą… as whole words, so "kodėl" (why) passes.
CODE_ON_GITHUB = (r'(?:\bcode|\bkode|код|código|الكود|الشيفرة|\bkod(?:as|o|ą|ui|e)\b)[^.!?]{0,40}github'
                  r'|github[^.!?]{0,40}(?:\bcode|\bkode|код|código|الكود|الشيفرة|\bkod(?:as|o|ą|ui|e)\b)')

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
    'lt': [r'mokykl', r'mokytoj', r'pedagog', r'terapi', r'terapeut', r'specialist', r'logoped', r'organizacij', r'klinik',
           r'įstaig', r'darželi',
           r'jungikl', r'skenavim', r'galvos judes', r'galvos valdym', r'akių sekim', r'žvilgsn', r'žymekl',
           r'atvir\w* (pradin\w* )?kod', r'pradin\w* kod', r'išeities kod'],
}


# The privacy page names GitHub (github.com) as the host the voice files download from (owner decisions 30 and 33),
# as "GitHub (github.com)" in every language. Since 2026-10-14 GitHub may be named anywhere, but the app's code is
# never presented as being on GitHub or as open source. Lower case; matched on the visible text of the privacy pages only.
# There is no exception for therapists or specialists any more (owner decision 32).
ALLOWED_PRIVACY = {loc: 'github (github.com)' for loc in ('en', 'da', 'ru', 'uk', 'ar', 'es', 'lt')}

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


def load_reviewed(folder=TRANSLATIONS, prefix='web:'):
    """{locale: set(web keys)} from the web:<key> lines of translations/<lang>/reviewed.txt
    (prefix 'manual:': the manual pages a native speaker has checked)."""
    done = {loc: set() for loc in LOCALES}
    for loc in LOCALES:
        path = os.path.join(folder, loc, 'reviewed.txt')
        if not os.path.exists(path):
            continue
        with open(path, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith(prefix):
                    done[loc].add(line[len(prefix):])
    return done


def clean_email(value):
    e = (value or '').strip()
    return e if '@' in e and ' ' not in e else ''


def clean_donate(value):
    """A donation page (Buy Me a Coffee, Ko-fi, ...): https:// with a host, kept as given; else empty."""
    u = (value or '').strip()
    return u if re.match(r'^https://[^/\s"\'<>]+(/[^\s"\'<>]*)?$', u) else ''


def clean_site(value):
    """https://host, or http://localhost[:port] / http://127.0.0.1[:port] for a local preview (so the preview
    has the canonical, hreflang, sitemap and robots.txt too); anything else is empty."""
    u = (value or '').strip().rstrip('/')
    m = re.match(r'^https://([^/\s]+)(/\S*)?$', u) or re.match(r'^http://(localhost|127\.0\.0\.1)(:\d+)?$', u)
    return u if m else ''


def local_site(site):
    """A local preview URL (http://localhost...): no CNAME file for it."""
    return site.startswith('http://')


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
        return typography(self.app_labels(self.strings[key][loc], key, loc), loc)

    def app_labels(self, text, key, loc):
        """{app:key} -> the app's label in this language; {app:key|label} -> its part before the first ':';
        {app:key|name=Sam} fills the app string's {name} placeholder (the manual's example child)."""
        def label(m):
            name, mod = m.group(1), m.group(2)
            if name not in self.app:
                raise BuildError(f'{key}: unknown app string {name!r}')
            value = self.app[name][loc]
            if mod == 'label':
                value = value.split(':')[0]
            elif mod:
                for pair in mod.split('|'):
                    k, _eq, v = pair.partition('=')
                    if not _eq or '{' + k + '}' not in value:
                        raise BuildError(f'{key}: {{app:{name}|{mod}}}: app string {name} has no {{{k}}}')
                    value = value.replace('{' + k + '}', v)
            if '{' in value:
                raise BuildError(f'{key}: app string {name} has a placeholder; use |label or |name=value')
            return value.strip()
        return re.sub(r'\{app:([A-Za-z0-9_.\-]+)(?:\|(label|[a-z]+=[^|{}]+(?:\|[a-z]+=[^|{}]+)*))?\}', label, text)

    def html_text(self, key, loc):
        s = html.escape(self.text(key, loc), quote=False)
        # [[link text|name]] links to OUTSIDE_LINKS[name]; set aside so the RTL step below leaves the name alone.
        outside = []

        def keep(m):
            if m.group(2) not in OUTSIDE_LINKS:
                raise BuildError(f'{key}: unknown link {m.group(2)!r} (known: {", ".join(OUTSIDE_LINKS)})')
            outside.append((m.group(1), OUTSIDE_LINKS[m.group(2)]))
            return f'\x00{len(outside) - 1}\x00'
        # The documents OUTSIDE_LINKS names are in English only: hreflang="en", and on other languages' pages
        # the label "(in English)" in the page's language after the link (string link.inEnglish).
        in_english = ''
        if loc != 'en' and 'link.inEnglish' in self.strings:
            self.used.add('link.inEnglish')
            in_english = ' ' + html.escape(self.strings['link.inEnglish'][loc], quote=False)
        s = re.sub(r'\[\[([^\]|]+?)\|([a-z\-]+)\]\]', keep, s)
        if loc in RTL:
            s = isolate_latin(s)
            outside = [(isolate_latin(t), u) for t, u in outside]
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'\x00(\d+)\x00', lambda m: f'<a href="{outside[int(m.group(1))][1]}" hreflang="en" rel="noopener">'
                   f'{outside[int(m.group(1))][0]}</a>{in_english}', s)
        s = re.sub(r'\[\[(.+?)\]\]', lambda m: f'<a href="{REPO_URL}" rel="noopener">{m.group(1)}</a>', s)
        if '{email}' in s:
            if not self.email:
                raise BuildError(f'{key} needs the email; put it inside {{{{#email}}}}...{{{{/email}}}}')
            e = html.escape(self.email)
            s = s.replace('{email}', f'<bdi dir="ltr"><a href="mailto:{e}">{e}</a></bdi>')
        return s

    def plain(self, key, loc):
        s = re.sub(r'\[\[([^\]|]+?)\|[a-z\-]+\]\]', r'\1', self.text(key, loc))
        s = s.replace('**', '').replace('[[', '').replace(']]', '')
        if '{email}' in s:
            raise BuildError(f'{key} has {{email}} and cannot be used as plain text')
        return html.escape(s, quote=True)

    def report_mailto(self, loc):
        """mailto: the project email with a subject (the app's own, reportSubject) and the checklist as the body,
        each question followed by room for the answer, in the page's language. Spaces as %20, lines as CRLF
        (RFC 6068)."""
        if not self.email:
            raise BuildError('report_mailto needs the email; put it inside {{#email}}...{{/email}}')
        subject = self.app['reportSubject'][loc].strip()
        lines = []
        for key in REPORT_CHECKS:
            text = re.sub(r'\[\[([^\]|]+?)(?:\|[a-z\-]+)?\]\]', r'\1', self.text(key, loc)).replace('**', '')
            lines += [re.sub('[\u00a0\u202f]', ' ', text), '', '']  # plain spaces in an email
        body = '\r\n'.join(lines).rstrip('\r\n') + '\r\n\r\n'
        q = urllib.parse.quote
        return f'mailto:{self.email}?subject={q(subject, safe="")}&body={q(body, safe="")}'

    def sections(self, tpl):
        flags = {'email': bool(self.email), 'site': bool(self.site), 'donate': bool(self.donate)}

        def keep(m):
            return m.group(2) if flags[m.group(1)] else ''
        return re.sub(r'\{\{#(email|site|donate)\}\}(.*?)\{\{/\1\}\}', keep, tpl, flags=re.S)

    def render(self, tpl, loc, values, page=None, root=None):
        """`root` leads back to the site root; without it, it comes from `page` (one of PAGES)."""
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
                return (root if root is not None else rel_root(page)) + f'{loc}/{page_path(name)}'
            if name == 'weblate' and name not in values:
                return html.escape(WEBLATE_URL, quote=True)
            if name == 'issues' and name not in values:
                return html.escape(ISSUES_URL, quote=True)
            if name == 'testers_group' and name not in values:
                return html.escape(TESTERS_GROUP_URL, quote=True)
            if name == 'testers_optin' and name not in values:
                return html.escape(TESTERS_OPTIN_URL, quote=True)
            if name == 'report_mailto' and name not in values:
                return html.escape(self.report_mailto(loc), quote=True)
            if name == 'donate' and name not in values:
                return html.escape(self.donate, quote=True)
            if name not in values:
                raise BuildError(f'unknown value {name!r}')
            return values[name]
        out = re.sub(r'\{\{(t|a|v|link):([A-Za-z0-9_.\-]+)\}\}', sub, tpl)
        if '{{' in out:
            raise BuildError(f'unrendered template tag near {out[out.index("{{"):][:40]!r}')
        return out


# One Latin word in right-to-left text: letters, digits, _ and -, joined by "." or "/" (github.com/amalino-app/voices).
_LATIN_WORD = r'[A-Za-z](?:[A-Za-z0-9_\-]|[./](?=[A-Za-z0-9]))*'


def isolate_latin(s):
    """In right-to-left text, a whole Latin run stays ONE left-to-right unit (localization review T1): words
    joined by spaces, "." or "/", and numbers that follow a Latin word ("iOS 26", "Supertonic 3"), so a URL
    or "iOS 26" doesn't come out reversed, and a trailing "?" keeps its place ("OK?")."""
    return re.sub(r'(?<![{&A-Za-z0-9_])(?!email\})' + _LATIN_WORD +
                  r'(?:\s+(?:' + _LATIN_WORD + r'|\d+(?:[.,]\d+)*(?![\w])))*\??',
                  lambda m: f'<bdi dir="ltr">{m.group(0)}</bdi>', s)


NBSP = '\u00a0'


def typography(s, loc):
    """Non-breaking spaces (localization review T6), so a line never breaks inside "129 MB", "iOS 26" or
    before a dash, nor (Russian, Ukrainian) after a one-letter word, nor inside Lithuanian "t. y."."""
    s = re.sub(r'(\d) (?=(?:MB|GB|KB|МБ|ГБ|КБ|mm|мм|ميغابايت|%)(?!\w))', r'\1' + NBSP, s)
    s = re.sub(r'\b(iOS|Android|Supertonic) (?=\d)', r'\1' + NBSP, s)
    s = re.sub(r' (?=[—–] )', NBSP, s)
    if loc in ('ru', 'uk'):
        s = re.sub(r'(?<![\w\-{])([А-Яа-яЁёІіЇїЄєҐґ]) (?=\S)', r'\1' + NBSP, s)
    if loc == 'lt':
        s = s.replace('t. y.', 't.' + NBSP + 'y.')
    return s


def rtl_lead(text, loc):
    """An Arabic <title> or description that starts with a Latin word ("Amalino: ...") gets a right-to-left mark
    first, so tabs and link previews show it right to left (review T2)."""
    return '\u200f' + text if loc in RTL and re.match(r'[A-Za-z]', text) else text


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


def share_meta(r, site, loc, page, title, desc, url=None, langs=None):
    """Open Graph and Twitter card tags. og:url and the image need absolute URLs, so they come only with a
    site URL; without one the card still has a title, a description and the locales. `url` and `langs` (the
    languages the page exists in) are for pages outside PAGES, such as the manual."""
    own = loc or 'en'
    tags = [('property', 'og:type', 'website'), ('property', 'og:site_name', 'Amalino'),
            ('property', 'og:title', title), ('property', 'og:description', desc),
            ('property', 'og:locale', OG_LOCALES[own])]
    tags += [('property', 'og:locale:alternate', OG_LOCALES[o]) for o in (langs or LOCALES) if o != own]
    tags.append(('name', 'twitter:card', 'summary_large_image' if site else 'summary'))
    if site:
        image = html.escape(f'{site}/assets/og-image.png')
        tags += [('property', 'og:url', html.escape(url or site_url(site, loc, page))), ('property', 'og:image', image),
                 ('property', 'og:image:type', 'image/png'), ('property', 'og:image:width', '1200'),
                 ('property', 'og:image:height', '630'), ('property', 'og:image:alt', r.plain('og.imageAlt', own)),
                 ('name', 'twitter:image', image), ('name', 'twitter:image:alt', r.plain('og.imageAlt', own))]
    tags += [('name', 'twitter:title', title), ('name', 'twitter:description', desc)]
    return ''.join(f'<meta {kind}="{name}" content="{value}">\n' for kind, name, value in tags)


def json_ld(r, site, loc):
    """schema.org SoftwareApplication for a home page. Only what is true today: free, two platforms, seven
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


def org_json_ld(site, email):
    """schema.org Organization, once (the English home page): name, address, logo and the public repository."""
    data = {'@context': 'https://schema.org', '@type': 'Organization', 'name': 'Amalino', 'url': f'{site}/',
            'logo': f'{site}/assets/icon-512.png', 'sameAs': [REPO_URL]}
    if email:
        data['email'] = email
    text = json.dumps(data, ensure_ascii=False, indent=1).replace('</', '<\\/')
    return f'<script type="application/ld+json">\n{text}\n</script>\n'


def icon_links(root):
    """Favicons, the home-screen icon, the web manifest and the browser bar colour (light and dark)."""
    return (f'<link rel="icon" href="{root}favicon.ico" sizes="any">\n'
            f'<link rel="icon" href="{root}assets/amalino.svg" type="image/svg+xml">\n'
            f'<link rel="icon" href="{root}assets/favicon-32.png" type="image/png" sizes="32x32">\n'
            f'<link rel="icon" href="{root}assets/favicon-16.png" type="image/png" sizes="16x16">\n'
            f'<link rel="apple-touch-icon" href="{root}assets/apple-touch-icon.png">\n'
            f'<link rel="manifest" href="{root}site.webmanifest">\n'
            f'<meta name="theme-color" content="{THEME_COLORS[0]}" media="(prefers-color-scheme: light)">\n'
            f'<meta name="theme-color" content="{THEME_COLORS[1]}" media="(prefers-color-scheme: dark)">')


def web_manifest():
    return json.dumps({
        'name': 'Amalino', 'short_name': 'Amalino', 'start_url': './', 'display': 'browser',
        'background_color': THEME_COLORS[0], 'theme_color': THEME_COLORS[0],
        'icons': [{'src': 'assets/icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
                  {'src': 'assets/icon-512.png', 'sizes': '512x512', 'type': 'image/png'}],
    }, indent=1) + '\n'


def not_found_page(site):
    """404.html (GitHub Pages serves it for any missing path): English, not indexed, a link to every language's
    home. Root-relative links, since it answers at any depth."""
    items = ''.join(f'<li><a href="/{loc}/" lang="{loc}" hreflang="{loc}" dir="{"rtl" if loc in RTL else "ltr"}">'
                    f'<strong>{ENDONYMS[loc]}</strong></a></li>' for loc in LOCALES)
    return ('<!doctype html>\n<html lang="en" dir="ltr">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            '<meta name="robots" content="noindex">\n<meta name="color-scheme" content="light dark">\n'
            '<title>Page not found · Amalino</title>\n'
            '<meta name="description" content="This page doesn\'t exist. Choose a language to go to Amalino\'s home page.">\n'
            f'{icon_links("/")}\n<link rel="stylesheet" href="/assets/style.css">\n</head>\n<body class="picker">\n'
            '<main id="main" class="wrap">\n'
            '  <img class="picker-logo" src="/assets/amalino.svg" alt="" width="88" height="88">\n'
            '  <h1>This page doesn\'t exist</h1>\n'
            '  <p class="choose">Choose a language to go to Amalino\'s home page:</p>\n'
            f'  <ul class="picker-list">{items}</ul>\n</main>\n</body>\n</html>\n')


def lastmod():
    """The sitemap date: the last commit of the site, the manual or the translations (today without git)."""
    try:
        out = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', 'site', 'manual', 'translations'],
                             cwd=ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        out = ''
    return out if re.match(r'^\d{4}-\d{2}-\d{2}$', out) else datetime.date.today().isoformat()


def sitemap(site, date, extra=()):
    """sitemap.xml: every language page and both pickers, each with its cluster's xhtml:link alternates, plus
    `extra` [(url, [(hreflang, url)])] (the manual's pages)."""
    entries = [(site_url(site, loc, page), alternates(site, page)) for page in PAGES for loc in LOCALES]
    entries += [(site_url(site, None, p), alternates(site, p)) for p in ('home', 'translate')]
    entries += list(extra)
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for loc, alts in entries:
        lines.append(f'  <url>\n    <loc>{html.escape(loc)}</loc>\n    <lastmod>{date}</lastmod>')
        for lang, url in alts:
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
    # Crawlers stay on the picker (its links are the way in); people are sent on.
    return ('<script>(function(){if(/bot|crawl|spider|slurp|preview|facebookexternalhit/i.test(navigator.userAgent))return;'
            'var L=' + langs + ',p=null;try{p=localStorage.getItem("' + LANG_KEY + '")}catch(e){}'
            'if(L.indexOf(p)<0){p=null;var n=navigator.languages||[navigator.language||""];'
            'for(var i=0;i<n.length&&!p;i++){var c=String(n[i]).toLowerCase().split("-")[0];if(L.indexOf(c)>=0)p=c}}'
            'location.replace("' + root + '"+(p||"en")+"/' + target + '")})();</script>')


# Every language page: a click on a language link (header menu or footer list) remembers that language.
REMEMBER_SCRIPT = ('<script>document.addEventListener("click",function(e){var a=e.target.closest&&'
                   'e.target.closest("a[data-lang]");if(a)try{localStorage.setItem("' + LANG_KEY + '",'
                   'a.getAttribute("data-lang"))}catch(x){}});</script>')


# ---------------------------------------------------------------- the manual

def md_inline(text, link, rtl=False):
    """Inline Markdown: `code`, [text](href) (href through `link`), **bold** and *italic*; HTML escaped. In
    right-to-left text (rtl) every Latin run is one left-to-right isolate (isolate_latin), and code is too."""
    parts = re.split(r'(`[^`]+`)', text)
    out = []
    for part in parts:
        if part.startswith('`') and part.endswith('`') and len(part) > 1:
            code = f'<code>{html.escape(part[1:-1], quote=False)}</code>'
            out.append(f'<bdi dir="ltr">{code}</bdi>' if rtl and re.search(r'[A-Za-z]', part) else code)
            continue
        s = html.escape(part, quote=False)
        # Links are set aside first, so the right-to-left step never touches an href.
        links = []

        def keep(m):
            links.append((m.group(1), link(html.unescape(m.group(2)))))
            return f'\x00{len(links) - 1}\x00'
        s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', keep, s)
        if rtl:
            s = isolate_latin(s)
            links = [(isolate_latin(t), h) for t, h in links]
        s = re.sub(r'\x00(\d+)\x00', lambda m: f'<a href="{html.escape(links[int(m.group(1))][1], quote=True)}">'
                   f'{links[int(m.group(1))][0]}</a>', s)
        s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
        s = re.sub(r'(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])', r'<em>\1</em>', s)
        out.append(s)
    return ''.join(out)


def slugify(text):
    """A heading's id: lower-case letters and digits of any script, joined by "-" (Cyrillic and Arabic headings
    keep their own letters)."""
    return re.sub(r'[\W_]+', '-', re.sub(r'[*`]', '', text).lower()).strip('-')


def md_to_html(md, link, image=None, rtl=False):
    """A small Markdown subset for the manual: # headings, paragraphs, - and 1. lists, > notes, inline marks,
    and a screenshot on a line of its own: ![alt text](img/name-1x.webp), drawn by image(src, alt) (alt is required).
    HTML comments are dropped; the first one may be <!-- description: ... -->. Returns (h1 text, description,
    html). rtl: the page is right to left (see md_inline)."""
    m = re.match(r'\s*<!--\s*description:\s*(.*?)\s*-->', md, flags=re.S)
    description = ' '.join(m.group(1).split()) if m else ''
    md = re.sub(r'<!--.*?-->', '', md, flags=re.S)
    title, out, para, items, kind, quote = '', [], [], [], None, []

    def flush():
        nonlocal para, items, kind, quote
        if para:
            out.append(f'<p>{md_inline(" ".join(para), link, rtl)}</p>')
        if items:
            tag = 'ol' if kind == 'ol' else 'ul'
            out.append(f'<{tag}>' + ''.join(f'<li>{md_inline(i, link, rtl)}</li>' for i in items) + f'</{tag}>')
        if quote:
            out.append(f'<blockquote><p>{md_inline(" ".join(quote), link, rtl)}</p></blockquote>')
        para, items, kind, quote = [], [], None, []

    for line in md.splitlines():
        line = line.rstrip()
        h = re.match(r'^(#{1,4})\s+(.+)$', line)
        li = re.match(r'^(?:(-)|\d+\.)\s+(.+)$', line)
        img = MANUAL_IMAGE.match(line.strip())
        if not line.strip():
            flush()
        elif img:
            flush()
            if image is None:
                raise BuildError(f'a manual image is not allowed here: {line.strip()}')
            out.append(image(img.group(2), ' '.join(img.group(1).split())))
        elif h:
            flush()
            level, text = len(h.group(1)), h.group(2).strip()
            if level == 1:
                if title:
                    raise BuildError('a manual page has more than one # heading')
                title = text
                out.append(f'<h1>{md_inline(text, link, rtl)}</h1>')
            else:
                out.append(f'<h{level} id="{slugify(text)}">{md_inline(text, link, rtl)}</h{level}>')
        elif li:
            new = 'ul' if li.group(1) else 'ol'
            if para or quote or (items and kind != new):
                flush()
            kind = new
            items.append(li.group(2))
        elif line.startswith('>'):
            if para or items:
                flush()
            quote.append(line[1:].strip())
        elif items and line.startswith(('  ', '\t')):
            items[-1] += ' ' + line.strip()
        else:
            if items or quote:
                flush()
            para.append(line.strip())
    flush()
    if not title:
        raise BuildError('a manual page needs a # heading')
    return re.sub(r'[*`]', '', re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', title)), description, '\n'.join(out)


def manual_pages(loc):
    """The manual's page names in a language, in the contents order: 'index', then the pages index.md lists."""
    index = os.path.join(MANUAL, loc, 'index.md')
    if not os.path.isfile(index):
        return []
    names = ['index'] + [n for n in dict.fromkeys(re.findall(r'\]\(([a-z0-9\-]+)\.md\)', read(index))) if n != 'index']
    for n in names:
        if not os.path.isfile(os.path.join(MANUAL, loc, f'{n}.md')):
            raise BuildError(f'manual/{loc}/index.md links to {n}.md, which does not exist')
    return names


def manual_image(loc, name):
    """The screenshot drawer for a manual page: a figure with the 1x picture's size, its 2x twin in srcset,
    lazily loaded. Both NAME-1x.webp and NAME-2x.webp (twice the size) must be in manual/<loc>/img/, or, for a
    translated manual without its own screenshots yet, in the source language's manual/en/img/ (the page then
    shows the English screenshots from /en/manual/img/; the alt text is the translation's)."""
    def draw(src, alt):
        src2 = src[:-len('-1x.webp')] + '-2x.webp'
        own = loc if os.path.isfile(os.path.join(MANUAL, loc, src)) or loc == MANUAL_SOURCE else MANUAL_SOURCE
        size, size2 = (webp_size(os.path.join(MANUAL, own, s)) for s in (src, src2))
        if not size:
            raise BuildError(f'manual/{loc}/{name}.md: {src} is not a WebP in manual/{loc}/img/')
        if size2 != (size[0] * 2, size[1] * 2):
            raise BuildError(f'manual/{loc}/{name}.md: {src2} must be a WebP twice the size of {src}')
        here = '' if name == 'index' else '../'
        if own != loc:
            here += f'../../{own}/manual/'
        return (f'<figure class="shot"><img src="{here}{src}" srcset="{here}{src} 1x, {here}{src2} 2x" '
                f'alt="{html.escape(alt, quote=True)}" width="{size[0]}" height="{size[1]}" loading="lazy" '
                f'decoding="async"></figure>')
    return draw


def manual_langs():
    return [loc for loc in LOCALES if manual_pages(loc)]


def manual_path(name):
    return 'manual/index.html' if name == 'index' else f'manual/{name}/index.html'


def manual_url(site, loc, name):
    return f'{site}/{loc}/manual/' if name == 'index' else f'{site}/{loc}/manual/{name}/'


def manual_alternates(site, name, langs):
    """The manual page's language versions plus x-default (the source language's page)."""
    have = [loc for loc in langs if name in manual_pages(loc)]
    source = MANUAL_SOURCE if MANUAL_SOURCE in have else have[0]
    return [(loc, manual_url(site, loc, name)) for loc in have] + [('x-default', manual_url(site, source, name))]


def manual_link(loc, name, names):
    """Resolves a link written in manual/<loc>/<name>.md to an href on the built page."""
    up = '' if name == 'index' else '../'

    def link(href):
        m = re.fullmatch(r'([a-z0-9\-]+)\.md(#[a-z0-9\-]+)?', href)
        if m:
            if m.group(1) not in names:
                raise BuildError(f'manual/{loc}/{name}.md: link to {href}, which is not in the contents')
            target = 'index.html' if m.group(1) == 'index' else f'{m.group(1)}/index.html'
            return (up + target if name != 'index' or m.group(1) != 'index' else 'index.html') + (m.group(2) or '')
        site_page = re.fullmatch(r'site:([a-z]+)', href)
        if site_page:  # a website page in the same language: [the privacy page](site:privacy)
            if site_page.group(1) not in PAGES:
                raise BuildError(f'manual/{loc}/{name}.md: link {href!r} (known: {", ".join("site:" + p for p in PAGES)})')
            return ('../../' if name == 'index' else '../../../') + f'{loc}/{page_path(site_page.group(1))}'
        if href.startswith('#') or re.match(r'^(https://|mailto:)', href):
            return href
        if href.startswith('../../') and not href.startswith('../../../'):
            return f'{REPO_URL}/blob/main/{href[6:]}'
        raise BuildError(f'manual/{loc}/{name}.md: link {href!r} (use another page\'s .md, site:PAGE, ../../FILE or https://)')
    return link


def build(out, email='', site='', strings=None, quiet=False, donate=''):
    """Builds the site into `out` (replacing it). Returns a summary dict used by --check and tests."""
    strings = strings if strings is not None else load_strings()
    reviewed = load_reviewed()
    reviewed_manual = load_reviewed(prefix='manual:')
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
    for name in ICON_FILES:
        shutil.copyfile(os.path.join(ICONS, name), os.path.join(out, 'assets', name))
    shutil.copyfile(os.path.join(ICONS, 'favicon.ico'), os.path.join(out, 'favicon.ico'))
    write(os.path.join(out, 'site.webmanifest'), web_manifest())

    langs_m = manual_langs()

    def manual_target(loc):
        """(language, label key) of the manual a page in `loc` links to: its own, else the source language's."""
        if loc in langs_m:
            return loc, 'nav.manual'
        return (MANUAL_SOURCE if MANUAL_SOURCE in langs_m else langs_m[0]), 'nav.manualEn'

    def manual_anchor(loc, root, current=False):
        if not langs_m:
            return ''
        target, key = manual_target(loc)
        attrs = '' if target == loc else f' hreflang="{target}"'
        cur = ' aria-current="page"' if current else ''
        return f'<a href="{root}{target}/{manual_path("index")}"{attrs}{cur}>{r.html_text(key, loc)}</a>'

    def site_nav(loc, root, current=None):
        """The header menu; `current` is a page id or 'manual'."""
        items = []
        for p in PAGES:
            cur = ' aria-current="page"' if p == current else ''
            items.append(f'<li><a href="{root}{loc}/{page_path(p)}"{cur}>{r.html_text(PAGES[p][2], loc)}</a></li>')
            if p == 'about' and langs_m:
                items.append(f'<li>{manual_anchor(loc, root, current == "manual")}</li>')
        return ''.join(items)

    status = {}
    for loc in LOCALES:
        checked = len(reviewed[loc] & set(strings))
        status[loc] = 'source' if loc == 'en' else f'{checked}/{len(strings)} checked'
        draft = loc != 'en' and checked < len(strings)
        banner = (f'<div class="draft-banner" role="note"><div class="wrap"><p>{r.html_text("draftBanner", loc)}'
                  f'</p></div></div>') if draft else ''
        for page, (tpl_name, _sub, nav_key, title_key, desc_key) in PAGES.items():
            root = rel_root(page)
            nav = [site_nav(loc, root, page)]
            langs = []
            for other in LOCALES:
                cur = ' aria-current="true"' if other == loc else ''
                d = 'rtl' if other in RTL else 'ltr'
                langs.append(f'<li><a href="{root}{other}/{page_path(page)}" lang="{other}" hreflang="{other}" '
                             f'dir="{d}" data-lang="{other}"{cur}>{ENDONYMS[other]}</a></li>')
            content = r.render(read(os.path.join(TEMPLATES, tpl_name)), loc, {}, page)
            title, desc = rtl_lead(r.plain(title_key, loc), loc), rtl_lead(r.plain(desc_key, loc), loc)
            head = head_links(site, loc, page) + share_meta(r, site, loc, page, title, desc)
            if page == 'home':
                head += json_ld(r, site, loc)
                if loc == 'en' and site:
                    head += org_json_ld(site, email)
            values = {
                'icons': icon_links(root),
                'lang': loc, 'dir': 'rtl' if loc in RTL else 'ltr', 'root': root, 'title': title,
                'description': desc, 'head_links': head.rstrip('\n'),
                'nav': ''.join(nav), 'lang_links': ''.join(langs), 'draft_banner': banner, 'content': content,
                'lang_current': f'<span lang="{loc}" dir="{"rtl" if loc in RTL else "ltr"}">{ENDONYMS[loc]}</span>',
                'remember_script': REMEMBER_SCRIPT, 'manual_footer': manual_anchor(loc, root),
            }
            write(os.path.join(out, loc, page_path(page)), r.render(layout, loc, values, page))

    # The manual: /<lang>/manual/ and /<lang>/manual/<page>/ for each language that has one.
    manual_entries = []
    for loc in langs_m:
        names = manual_pages(loc)
        shots = os.path.join(MANUAL, loc, 'img')
        if os.path.isdir(shots):
            os.makedirs(os.path.join(out, loc, 'manual', 'img'), exist_ok=True)
            for n in sorted(os.listdir(shots)):
                if n.endswith('.webp'):
                    shutil.copyfile(os.path.join(shots, n), os.path.join(out, loc, 'manual', 'img', n))
        pages = []
        for name in names:
            # {app:key} -> the app's own label, then the website's non-breaking spaces.
            source = typography(r.app_labels(read(os.path.join(MANUAL, loc, f'{name}.md')), f'manual/{loc}/{name}.md', loc),
                                loc)
            heading, desc, body = md_to_html(source, manual_link(loc, name, names), manual_image(loc, name), loc in RTL)
            if not desc:
                raise BuildError(f'manual/{loc}/{name}.md needs <!-- description: ... --> on its first line')
            pages.append((name, heading, desc, body))
        for i, (name, heading, desc, body) in enumerate(pages):
            root = '../../' if name == 'index' else '../../../'
            here = '' if name == 'index' else '../'

            def href(n):
                return here + ('index.html' if n == 'index' else f'{n}/index.html')
            steps = []
            back, ahead = ('→', '←') if loc in RTL else ('←', '→')  # arrows point the way the page reads
            if i > 0:
                steps.append(f'<a class="prev" href="{href(pages[i - 1][0])}" rel="prev">{back} {r.html_text("man.prev", loc)}: '
                             f'{html.escape(pages[i - 1][1])}</a>')
            if i + 1 < len(pages):
                steps.append(f'<a class="next" href="{href(pages[i + 1][0])}" rel="next">{r.html_text("man.next", loc)}: '
                             f'{html.escape(pages[i + 1][1])} {ahead}</a>')
            here_mark = ' aria-current="page"'
            toc = ''.join(f'<li><a href="{href(n)}"{here_mark if n == name else ""}>{html.escape(h)}</a></li>'
                          for n, h, _d, _b in pages)
            edit = f'{REPO_URL}/edit/main/manual/{loc}/{name}.md'
            content = (f'<article class="wrap prose manual">\n{body}\n'
                       f'<p class="manual-edit"><a href="{edit}" rel="noopener">{r.html_text("man.edit", loc)}</a></p>\n'
                       + (f'<nav class="manual-steps" aria-label="{r.plain("man.navLabel", loc)}">{"".join(steps)}</nav>\n'
                          if steps else '')
                       + f'<nav class="manual-toc" aria-label="{r.plain("man.navLabel", loc)}">'
                       f'<h2>{r.html_text("man.contents", loc)}</h2><ol>{toc}</ol></nav>\n</article>')
            title = heading if name == 'index' else f'{heading} · {r.plain("man.suffix", loc)}'
            title = html.escape(rtl_lead(title, loc), quote=True)
            desc = html.escape(rtl_lead(desc, loc), quote=True)
            draft = loc != MANUAL_SOURCE and name not in reviewed_manual[loc]
            banner = (f'<div class="draft-banner" role="note"><div class="wrap"><p>{r.html_text("draftBanner", loc)}'
                      f'</p></div></div>') if draft else ''
            alts = manual_alternates(site, name, langs_m) if site else []
            url = manual_url(site, loc, name) if site else None
            head = ''
            if site:
                head = f'<link rel="canonical" href="{html.escape(url)}">\n' + ''.join(
                    f'<link rel="alternate" hreflang="{lang}" href="{html.escape(u)}">\n' for lang, u in alts)
                manual_entries.append((url, alts))
            head += share_meta(r, site, loc, None, title, desc, url=url, langs=[l for l in langs_m if name in manual_pages(l)])
            langs = []
            for other in LOCALES:
                cur = ' aria-current="true"' if other == loc else ''
                d = 'rtl' if other in RTL else 'ltr'
                target = (f'{root}{other}/{manual_path(name)}' if other in langs_m and name in manual_pages(other)
                          else f'{root}{other}/{page_path("home")}')
                langs.append(f'<li><a href="{target}" lang="{other}" hreflang="{other}" '
                             f'dir="{d}" data-lang="{other}"{cur}>{ENDONYMS[other]}</a></li>')
            values = {
                'icons': icon_links(root),
                'lang': loc, 'dir': 'rtl' if loc in RTL else 'ltr', 'root': root, 'title': title,
                'description': desc, 'head_links': head.rstrip('\n'),
                'nav': site_nav(loc, root, 'manual'), 'lang_links': ''.join(langs), 'draft_banner': banner,
                'content': content,
                'lang_current': f'<span lang="{loc}" dir="{"rtl" if loc in RTL else "ltr"}">{ENDONYMS[loc]}</span>',
                'remember_script': REMEMBER_SCRIPT, 'manual_footer': manual_anchor(loc, root),
            }
            write(os.path.join(out, loc, manual_path(name)), r.render(layout, loc, values, root=root))

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
            'icons': icon_links(root),
            'root': root, 'title': title, 'description': desc,
            'head_links': links.rstrip('\n'), 'heading': 'Amalino' if not sub else r.plain('tr.h1', 'en'),
            'choose': choose, 'items': ''.join(items), 'redirect': redirect_script(root, target),
        }
        write(os.path.join(out, target), r.render(picker, 'en', values))

    if site:
        write(os.path.join(out, 'sitemap.xml'), sitemap(site, lastmod(), manual_entries))
        write(os.path.join(out, 'robots.txt'), f'User-agent: *\nAllow: /\n\nSitemap: {site}/sitemap.xml\n')
        # GitHub Pages serves the site at its custom domain from this file (not for a local preview).
        if not local_site(site):
            write(os.path.join(out, 'CNAME'), re.match(r'^https://([^/]+)', site).group(1) + '\n')
        # Root-relative links only work at the domain root, so the 404 page comes with a site URL.
        write(os.path.join(out, '404.html'), not_found_page(site))

    referenced = set(re.findall(r'\{\{[ta]:([A-Za-z0-9_.\-]+)\}\}', ''.join(
        read(os.path.join(TEMPLATES, n)) for n in os.listdir(TEMPLATES) if n.endswith('.html'))))
    unused = sorted(set(strings) - r.used - referenced)
    if not quiet:
        print(f'Built {len(LOCALES)} languages x {len(PAGES)} pages + 2 pickers + the manual '
              f'({", ".join(f"{l} {len(manual_pages(l))} pages" for l in langs_m) or "none"}) into {os.path.relpath(out, ROOT)}'
              f' (email {"set" if email else "empty"}, site {"set" if site else "empty"},'
              f' donation link {"set" if donate else "empty"})')
        print('Native review (web:<key> in translations/<lang>/reviewed.txt): ' +
              ', '.join(f'{loc} {status[loc]}' for loc in LOCALES))
        if any(l != MANUAL_SOURCE for l in langs_m):
            print('Manual native review (manual:<page> in reviewed.txt): ' + ', '.join(
                f'{l} {len(reviewed_manual[l] & set(manual_pages(l)))}/{len(manual_pages(l))} checked'
                for l in langs_m if l != MANUAL_SOURCE))
        if unused:
            print('Unused string keys: ' + ', '.join(unused))
    return {'status': status, 'unused': unused, 'manual': {l: manual_pages(l) for l in langs_m},
            'manual_status': {l: sorted(reviewed_manual[l] & set(manual_pages(l))) for l in langs_m if l != MANUAL_SOURCE}}


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
    langs_m = manual_langs()
    manual_files = {os.path.join(loc, manual_path(n)): (loc, n) for loc in langs_m for n in manual_pages(loc)}
    files += list(manual_files)
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
            expect(ref.startswith(REPO_URL) or ref in OUTSIDE_LINKS.values(), f'{f}: GitHub link {ref} (only {REPO_URL})')
        for ref in re.findall(r'<a\b[^>]*\bhref="(https?://[^"]+)"', page):
            expect(ref.startswith(REPO_URL) or ref in OUTSIDE_LINKS.values() or ref == WEBLATE_URL
                   or ref in (TESTERS_GROUP_URL, TESTERS_OPTIN_URL)
                   or (site and ref.startswith(site + '/'))
                   or (donate and ref == html.escape(donate, quote=True)),
                   f'{f}: link to another site {ref} (add it to OUTSIDE_LINKS if it belongs)')
        if loc:
            expect(f'<p class="footer-repo"><a href="{REPO_URL}"' in page, f'{f}: footer link to the repository missing')
            if langs_m:
                expect('<p class="footer-manual"><a href="' in page, f'{f}: footer link to the manual missing')
        for leftover in ('{{', '{email}', '**', '{app:', '[[', ']]', '\x00'):
            expect(leftover not in page, f'{f}: leftover {leftover!r}')
        # Owner decision 31: no cookies. The language choice is in localStorage only. (The privacy page may say so.)
        scripts = ' '.join(re.findall(r'<script\b[^>]*>(.*?)</script>', page, flags=re.S)).lower()
        expect('cookie' not in scripts, f'{f}: a script uses cookies')
        if f in manual_files:
            m_loc, m_name = manual_files[f]
            expect(f'href="{REPO_URL}/edit/main/manual/{m_loc}/{m_name}.md"' in page, f'{f}: "edit this page" link missing')
            expect('aria-current="page"' in page.split('<nav class="site-nav"')[1].split('</nav>')[0],
                   f'{f}: the header menu should mark the manual')
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
            expect('mailto:' not in page, f'{f}: mailto link while the email is empty')
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
            target = os.path.normpath(os.path.join(os.path.dirname(path), ref.split('#')[0]))
            expect(target.startswith(os.path.abspath(out)) and os.path.isfile(target), f'{f}: broken link {ref}')

    for root, _dirs, names in os.walk(out):
        for n in names:
            if n.endswith('.css'):
                for url in external_refs(read(os.path.join(root, n)), site):
                    errors.append(f'{os.path.relpath(os.path.join(root, n), out)}: external resource {url}')

    manual_alts = {f: [l for l in langs_m if n in manual_pages(l)] for f, (_l, n) in manual_files.items()}
    errors += check_seo(out, files, site, manual_alts)

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
        # "Report a problem" (owner 2026-10-21): every language's About page has the section with the GitHub
        # issue forms, the mailto with a subject and the checklist when the email is set, and every page's footer
        # links to it.
        about = read(os.path.join(out, loc, page_path('about')))
        # "Help test Amalino on Android" (owner 2026-10-23): every language's home page has the section with the
        # testers' group, Google Play's opt-in page and the way to "Report a problem".
        home = read(os.path.join(out, loc, page_path('home')))
        expect('id="test-android"' in home and f'href="{TESTERS_GROUP_URL}"' in home
               and f'href="{TESTERS_OPTIN_URL}"' in home and '#report"' in home,
               f'{loc}: "Help test Amalino on Android" missing on the home page')
        expect('id="report"' in about and f'href="{ISSUES_URL}"' in about, f'{loc}/about: "Report a problem" missing')
        expect(not email or f'href="mailto:{html.escape(email)}?subject=' in about,
               f'{loc}/about: the report email link missing')
        for p in PAGES:
            expect('<p class="footer-report"><a href="' in read(os.path.join(out, loc, page_path(p))),
                   f'{loc}/{page_path(p)}: footer link to "Report a problem" missing')
        if email:
            for p in ('translate', 'privacy', 'about'):
                expect(f'mailto:{email}' in read(os.path.join(out, loc, page_path(p))),
                       f'{loc}/{page_path(p)}: email missing')
    return errors


def check_seo(out, files, site, page_langs=None):
    """Titles, descriptions, hreflang, canonical, share cards, JSON-LD, headings, alt text, page weight and
    (with a site URL) sitemap.xml and robots.txt. Without a site URL nothing absolute may be in a <head>.
    `page_langs` names the languages of pages that don't exist in every language (the manual)."""
    errors = []

    def expect(cond, msg):
        if not cond:
            errors.append(msg)

    pages = {f: seo(read(os.path.join(out, f))) for f in files}
    organizations = {}  # file -> Organization JSON-LD blocks (one, on the English home page, with a site URL)
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
        limit = MAX_MANUAL_PAGE_BYTES if '/manual/' in f'/{f}' else MAX_PAGE_BYTES
        expect(os.path.getsize(os.path.join(out, f)) <= limit, f'{f}: over {limit} bytes')
        for key in ('og:title', 'og:description', 'og:type', 'og:locale', 'twitter:card'):
            expect(len(h.metas(key)) == 1, f'{f}: needs one {key}')
        expect(h.metas('og:locale') == [OG_LOCALES[loc or 'en']], f'{f}: wrong og:locale')
        langs = (page_langs or {}).get(f, LOCALES)
        expect(len(h.metas('og:locale:alternate')) == len(langs) - 1, f'{f}: needs og:locale:alternate for the others')
        expect(len(h.title.strip()) <= TITLE_MAX, f'{f}: <title> is {len(h.title.strip())} characters (max {TITLE_MAX})')
        expect(len((desc or [''])[0]) <= DESCRIPTION_MAX,
               f'{f}: meta description is {len((desc or [""])[0])} characters (max {DESCRIPTION_MAX})')
        expect(len(h.metas('theme-color')) == 2, f'{f}: needs the light and dark theme-color')
        rels = [l.get('rel') for l in h.links]
        expect('apple-touch-icon' in rels and 'manifest' in rels and rels.count('icon') >= 3,
               f'{f}: needs the favicons, apple-touch-icon and manifest links')
        types = []
        for block in h.ld:
            try:
                data = json.loads(block)
                types.append(data.get('@type'))
                if data.get('@type') == 'Organization':
                    expect(data.get('name') == 'Amalino' and data.get('sameAs') == [REPO_URL],
                           f'{f}: Organization JSON-LD is not Amalino')
                else:
                    expect(data.get('@type') == 'SoftwareApplication' and data.get('name') == 'Amalino' and
                           data.get('offers', {}).get('price') == '0', f'{f}: JSON-LD is not the Amalino app')
                expect(not {'aggregateRating', 'review', 'downloadUrl', 'installUrl'} & set(data),
                       f'{f}: JSON-LD claims ratings, reviews or store links')
            except ValueError as e:
                errors.append(f'{f}: JSON-LD does not parse ({e})')
        organizations[f] = types.count('Organization')
        if loc and f == os.path.join(loc, page_path('home')):
            expect(types.count('SoftwareApplication') == 1, f'{f}: needs the SoftwareApplication JSON-LD')
        if site:
            canon = h.canonical()
            expect(len(canon) == 1, f'{f}: needs one canonical link')
            alts = dict(h.alternates())
            expect(sorted(alts) == sorted(list(langs) + ['x-default']), f'{f}: hreflang needs {langs} and x-default')
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

    expect(sum(organizations.values()) == (1 if site else 0) and
           (not site or organizations.get(os.path.join('en', page_path('home'))) == 1),
           f'Organization JSON-LD: needs exactly one, on en/{page_path("home")} (found {sum(organizations.values())})')
    for name in ('favicon.ico', 'site.webmanifest') + tuple(f'assets/{n}' for n in ICON_FILES):
        expect(os.path.isfile(os.path.join(out, name)), f'missing {name}')
    for name, size in (('apple-touch-icon.png', 180), ('icon-192.png', 192), ('icon-512.png', 512),
                       ('favicon-32.png', 32), ('favicon-16.png', 16)):
        path = os.path.join(out, 'assets', name)
        expect(not os.path.isfile(path) or png_size(path) == (size, size), f'assets/{name} is not {size}x{size}')
    try:
        manifest = json.loads(read(os.path.join(out, 'site.webmanifest')))
        for icon in manifest.get('icons', []):
            expect(os.path.isfile(os.path.join(out, icon['src'])), f'site.webmanifest: {icon["src"]} missing')
    except (OSError, ValueError, KeyError) as e:
        errors.append(f'site.webmanifest does not parse ({e})')

    if site:
        nf = os.path.join(out, '404.html')
        expect(os.path.isfile(nf), 'missing 404.html')
        if os.path.isfile(nf):
            page = read(nf)
            expect('<meta name="robots" content="noindex">' in page, '404.html: needs noindex')
            for loc in LOCALES:
                expect(f'href="/{loc}/"' in page, f'404.html: no link to the {loc} home page')
            expect(not external_refs(page, site), '404.html: external resource')
        cname = os.path.join(out, 'CNAME')
        if local_site(site):
            expect(not os.path.exists(cname), 'CNAME for a local preview')
        else:
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
        errors += check_sitemap(out, site, set(by_url), {u: dict(pages[f].alternates()) for u, f in by_url.items()})
    else:
        for name in ('sitemap.xml', 'robots.txt', 'CNAME'):
            expect(not os.path.exists(os.path.join(out, name)), f'{name} without a site URL')

    og = os.path.join(out, 'assets', 'og-image.png')
    expect(os.path.isfile(og), 'missing assets/og-image.png')
    if os.path.isfile(og):
        expect(png_size(og) == (1200, 630), f'assets/og-image.png is not a 1200x630 PNG ({png_size(og)})')
    def shot(d):
        return os.path.basename(d) == 'img' and os.path.basename(os.path.dirname(d)) == 'manual'

    def manual_lang(d):
        """The language of a folder inside <lang>/manual/ (not its screenshots), else None."""
        parts = os.path.relpath(d, out).split(os.sep)
        return parts[0] if len(parts) >= 2 and parts[1] == 'manual' and not shot(d) else None
    total = sum(os.path.getsize(os.path.join(d, n)) for d, _ds, ns in os.walk(out)
                if not shot(d) and not manual_lang(d) for n in ns)
    expect(total <= MAX_SITE_BYTES, f'site is {total} bytes, over {MAX_SITE_BYTES}')
    per_lang = {}
    for d, _ds, ns in os.walk(out):
        if manual_lang(d):
            per_lang[manual_lang(d)] = per_lang.get(manual_lang(d), 0) + sum(os.path.getsize(os.path.join(d, n)) for n in ns)
    for lang, size in per_lang.items():
        expect(size <= MAX_MANUAL_HTML_BYTES, f'{lang}/manual: the pages are {size} bytes, over {MAX_MANUAL_HTML_BYTES}')
    shots = [os.path.join(d, n) for d, _ds, ns in os.walk(out) if shot(d) for n in ns]
    for p in shots:
        expect(p.endswith('.webp') and os.path.getsize(p) <= MAX_IMAGE_BYTES,
               f'{os.path.relpath(p, out)}: a manual image must be a WebP of at most {MAX_IMAGE_BYTES} bytes')
    images = {}
    for p in shots:
        lang = os.path.relpath(p, out).split(os.sep)[0]
        images[lang] = images.get(lang, 0) + os.path.getsize(p)
    for lang, size in sorted(images.items()):
        expect(size <= MAX_MANUAL_IMAGE_BYTES, f'{lang}/manual: the images are {size} bytes, over {MAX_MANUAL_IMAGE_BYTES}')
    return errors


def webp_size(path):
    """(width, height) of a WebP (lossy VP8, lossless VP8L or extended VP8X), or None when the file is missing
    or not a WebP."""
    if not os.path.isfile(path):
        return None
    with open(path, 'rb') as f:
        head = f.read(30)
    if len(head) < 30 or head[:4] != b'RIFF' or head[8:12] != b'WEBP':
        return None
    kind = head[12:16]
    if kind == b'VP8X':
        return int.from_bytes(head[24:27], 'little') + 1, int.from_bytes(head[27:30], 'little') + 1
    if kind == b'VP8 ' and head[23:26] == b'\x9d\x01\x2a':
        return int.from_bytes(head[26:28], 'little') & 0x3FFF, int.from_bytes(head[28:30], 'little') & 0x3FFF
    if kind == b'VP8L' and head[20] == 0x2F:
        bits = int.from_bytes(head[21:25], 'little')
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    return None


def png_size(path):
    """(width, height) from a PNG's IHDR chunk, or None when the file is not a PNG."""
    with open(path, 'rb') as f:
        head = f.read(24)
    if head[:8] != b'\x89PNG\r\n\x1a\n' or head[12:16] != b'IHDR':
        return None
    return int.from_bytes(head[16:20], 'big'), int.from_bytes(head[20:24], 'big')


def check_sitemap(out, site, page_urls, page_alts=None):
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
        want = (page_alts or {}).get(loc)
        if (want is not None and alts != want) or (want is None and sorted(alts) != sorted(LOCALES + ['x-default'])) \
                or loc not in alts.values():
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
        print('warning: --contact-email/OVK_CONTACT_EMAIL is not an email address; left out', file=sys.stderr)
    if args.site_url.strip() and not site:
        print('warning: --site-url/OVK_SITE_URL is not an https:// URL (or http://localhost); left out', file=sys.stderr)
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
