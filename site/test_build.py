"""Tests for build.py (the guards, the owner's text rules, SEO basics, the language redirect and menu).
Run from the repository root: python3 -m unittest discover -s site -p 'test_*.py'"""
import html
import io
import os
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(__file__))
import build as bs  # noqa: E402

EMAIL = 'hello@example.org'
FIXTURE = os.path.join(os.path.dirname(__file__), 'test_fixtures', 'guard.html')


def read(*parts):
    with open(os.path.join(*parts), encoding='utf-8') as f:
        return f.read()


class BuiltSite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.strings = bs.load_strings()
        cls.with_email = os.path.join(cls.tmp.name, 'with')
        cls.without = os.path.join(cls.tmp.name, 'without')
        with redirect_stdout(io.StringIO()):
            bs.build(cls.with_email, EMAIL, 'https://example.org', cls.strings)
            bs.build(cls.without, '', '', cls.strings)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_t100_pages_lang_dir_and_check(self):
        for out, email, site in ((self.with_email, EMAIL, 'https://example.org'), (self.without, '', '')):
            self.assertEqual(bs.check(out, self.strings, email, site), [])
            for loc in bs.LOCALES:
                for page in bs.PAGES:
                    html = read(out, loc, bs.page_path(page))
                    want = 'rtl' if loc == 'ar' else 'ltr'
                    self.assertIn(f'<html lang="{loc}" dir="{want}">', html)
            self.assertTrue(os.path.isfile(os.path.join(out, 'index.html')))
        self.assertIn('<html lang="ar" dir="rtl">', read(self.without, 'ar', 'index.html'))

    def test_t101_no_forbidden_terms_anywhere(self):
        for root, _dirs, files in os.walk(self.with_email):
            for f in files:
                if f.endswith('.html'):
                    rel = os.path.relpath(os.path.join(root, f), self.with_email)
                    loc = rel.split(os.sep)[0]
                    page = 'privacy' if os.sep + 'privacy' + os.sep in os.sep + rel else None
                    self.assertEqual(bs.forbidden_found(read(root, f), loc if loc in bs.LOCALES else 'mixed', page), [], rel)

    def test_t101_guard_catches_a_forbidden_term_in_a_built_page(self):
        bad = dict(self.strings)
        bad['home.lead'] = dict(bad['home.lead'], ru='Подходит для школы и логопеда.')
        out = os.path.join(self.tmp.name, 'bad')
        with redirect_stdout(io.StringIO()):
            bs.build(out, '', '', bad)
        errors = bs.check(out, bad, '')
        self.assertTrue(any('ru/index.html' in e and 'школ' in e for e in errors), errors)

    def test_t101b_fixture(self):
        found = [t.lower() for t in bs.forbidden_found(read(FIXTURE))]
        self.assertIn('switch access', found)
        self.assertIn('eye gaze', found)
        self.assertIn('code is on github', found)
        self.assertFalse(any(t.startswith('switch on') or t == 'switch' for t in found))
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = bs.main(['--check-fixture', FIXTURE])
        self.assertEqual(code, 1)
        self.assertIn('"switch access"', buf.getvalue())
        self.assertIn('external resource https://fonts.googleapis.com', buf.getvalue())
        self.assertNotIn('switch on', buf.getvalue().lower())

    def test_t102_free_promise_on_home_and_about(self):
        for loc in bs.LOCALES:
            for page in ('home', 'about'):
                main = bs.visible_text(bs.main_part(read(self.without, loc, bs.page_path(page))))
                self.assertIn(self.strings['freeTitle'][loc], main, f'{loc} {page}')

    def test_t103_email_only_when_set(self):
        for root, _dirs, files in os.walk(self.without):
            for f in files:
                if f.endswith('.html'):
                    html = read(root, f)
                    self.assertNotIn('mailto:', html)
                    self.assertNotIn('{email}', html)
                    self.assertNotIn(EMAIL, html)
        for loc in bs.LOCALES:
            for page in ('translate', 'privacy'):
                html = read(self.with_email, loc, bs.page_path(page))
                self.assertIn(f'href="mailto:{EMAIL}"', html)
                self.assertIn(f'<bdi dir="ltr"><a href="mailto:{EMAIL}">', html)

    def test_t104_translate_page_has_both_cases(self):
        for loc in bs.LOCALES:
            for out in (self.with_email, self.without):
                html = read(out, loc, 'translate', 'index.html')
                text = bs.visible_text(html)
                for key in ('tr.improveTitle', 'tr.addTitle', 'tr.improve1', 'tr.improve3', 'tr.add1', 'tr.add3'):
                    self.assertIn(bs.visible_text(self.strings[key][loc]), text, f'{loc} {key}')
                self.assertEqual(len(re.findall(r'<ol class="steps">', html)), 2)
            self.assertIn(EMAIL, read(self.with_email, loc, 'translate', 'index.html'))

    def test_t106_translate_page_for_every_app_language(self):
        for loc in bs.LOCALES:
            self.assertTrue(os.path.isfile(os.path.join(self.without, loc, 'translate', 'index.html')))
        picker = read(self.without, 'translate', 'index.html')
        self.assertIn(bs.redirect_script('../', 'translate/index.html'), picker)
        for loc in bs.LOCALES:
            self.assertIn(f'href="../{loc}/translate/index.html"', picker)

    # ------------------------------------------------------------ language: redirect and menu

    def test_root_pages_redirect_with_a_list_for_browsers_without_script(self):
        for sub, root, target in (('', '', 'index.html'), ('translate', '../', 'translate/index.html')):
            page = read(self.without, sub, 'index.html') if sub else read(self.without, 'index.html')
            script = bs.redirect_script(root, target)
            self.assertIn(script, page.split('</head>')[0], sub)
            self.assertIn(f'location.replace("{root}"+(p||"en")+"/{target}")', script)
            self.assertIn(bs.LANG_KEY, script)
            for loc in bs.LOCALES:
                self.assertIn(f'href="{root}{loc}/{target}"', page)
            self.assertNotIn('cookie', page.lower())

    def test_every_page_has_the_header_language_menu(self):
        for loc in bs.LOCALES:
            for page in bs.PAGES:
                html = read(self.without, loc, bs.page_path(page))
                header = html.split('</header>')[0]
                menu = re.search(r'<details class="lang-menu">(.*?)</details>', header, flags=re.S)
                self.assertTrue(menu, (loc, page))
                for other in bs.LOCALES:
                    self.assertIn(f'href="{bs.rel_root(page)}{other}/{bs.page_path(page)}"', menu.group(1), (loc, page, other))
                    self.assertIn(f'data-lang="{other}"', menu.group(1))
                self.assertIn(f'<summary aria-label="{bs.Renderer(self.strings, "", "").plain("lang.label", loc)}">', menu.group(1))
                self.assertIn(f'>{bs.ENDONYMS[loc]}</span>', menu.group(1).split('</summary>')[0])
                self.assertIn('aria-current="true"', menu.group(1))
                self.assertIn(bs.REMEMBER_SCRIPT, html)

    def test_cname_only_with_a_site_url(self):
        self.assertEqual(read(self.with_email, 'CNAME'), 'example.org\n')
        self.assertFalse(os.path.exists(os.path.join(self.without, 'CNAME')))

    def test_site_url_adds_canonical_links_only_when_set(self):
        self.assertIn('<link rel="canonical" href="https://example.org/da/translate/">',
                      read(self.with_email, 'da', 'translate', 'index.html'))
        self.assertNotIn('rel="canonical"', read(self.without, 'da', 'translate', 'index.html'))

    # ------------------------------------------------------------ SEO basics

    def all_pages(self, out):
        return [os.path.join(loc, bs.page_path(p)) for loc in bs.LOCALES for p in bs.PAGES] + \
            ['index.html', os.path.join('translate', 'index.html')] + self.manual_files()

    def manual_files(self):
        return [os.path.join(loc, bs.manual_path(n)) for loc in bs.manual_langs() for n in bs.manual_pages(loc)]

    def test_seo_hreflang_complete_and_reciprocal(self):
        site = 'https://example.org'
        heads = {f: bs.seo(read(self.with_email, f)) for f in self.all_pages(self.with_email)}
        by_url = {h.canonical()[0]: f for f, h in heads.items()}
        self.assertEqual(len(by_url), len(heads))
        manual = set(self.manual_files())
        for f, h in heads.items():
            alts = dict(h.alternates())
            langs = bs.manual_langs() if f in manual else bs.LOCALES
            self.assertEqual(sorted(alts), sorted(langs + ['x-default']), f)
            self.assertIn(h.canonical()[0], alts.values(), f)
            for lang, url in alts.items():
                self.assertTrue(url.startswith(site + '/'), (f, url))
                other = by_url[url]
                self.assertEqual(dict(heads[other].alternates()), alts, (f, other))
                if lang != 'x-default':
                    self.assertEqual(bs.page_lang(read(self.with_email, other)), lang)
        self.assertEqual(dict(heads['en/index.html'].alternates())['x-default'], site + '/')
        self.assertEqual(dict(heads['da/translate/index.html'].alternates())['x-default'], site + '/translate/')
        self.assertEqual(dict(heads['ar/about/index.html'].alternates())['x-default'], site + '/en/about/')

    def test_seo_sitemap_and_robots(self):
        import xml.etree.ElementTree as ET
        root = ET.parse(os.path.join(self.with_email, 'sitemap.xml')).getroot()
        ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9', 'x': 'http://www.w3.org/1999/xhtml'}
        urls = root.findall('s:url', ns)
        locs = {u.findtext('s:loc', '', ns) for u in urls}
        want = {bs.seo(read(self.with_email, f)).canonical()[0] for f in self.all_pages(self.with_email)}
        self.assertEqual(locs, want)
        self.assertEqual(len(urls), len(bs.LOCALES) * len(bs.PAGES) + 2 + len(self.manual_files()))
        for u in urls:
            self.assertRegex(u.findtext('s:lastmod', '', ns), r'^\d{4}-\d{2}-\d{2}$')
            # A manual page lists only the languages it exists in (plus x-default).
            langs = len(bs.manual_langs()) if '/manual/' in u.findtext('s:loc', '', ns) else len(bs.LOCALES)
            self.assertEqual(len(u.findall('x:link', ns)), langs + 1)
        self.assertIn('Sitemap: https://example.org/sitemap.xml', read(self.with_email, 'robots.txt'))
        errors = bs.check_sitemap(self.with_email, 'https://example.org', want | {'https://example.org/extra/'})
        self.assertTrue(any('lists' in e for e in errors), errors)

    def test_seo_unique_titles_and_descriptions_per_language(self):
        for loc in bs.LOCALES:
            titles, descs = set(), set()
            for page, (_t, _s, _n, title_key, desc_key) in bs.PAGES.items():
                h = bs.seo(read(self.without, loc, bs.page_path(page)))
                self.assertEqual(h.title, bs.html.unescape(bs.Renderer(self.strings, '', '').plain(title_key, loc)))
                titles.add(h.title)
                descs.add(h.metas('description')[0])
                self.assertIn('Amalino', h.title, (loc, page))
            self.assertEqual(len(titles), len(bs.PAGES), loc)
            self.assertEqual(len(descs), len(bs.PAGES), loc)
        for key in ('home.title', 'about.title', 'tr.title', 'pr.title', 'pick.title', 'pick.trTitle'):
            self.assertLessEqual(len(self.strings[key]['en']), 65, key)
        for key in ('home.meta', 'about.meta', 'tr.meta', 'pr.meta', 'pick.meta', 'pick.trMeta'):
            self.assertLessEqual(len(self.strings[key]['en']), 170, key)
        # The guard reports a duplicate.
        dup = dict(self.strings)
        dup['pr.title'] = dict(dup['pr.title'], da=dup['tr.title']['da'])
        out = os.path.join(self.tmp.name, 'dup')
        with redirect_stdout(io.StringIO()):
            bs.build(out, '', '', dup)
        self.assertTrue(any('da/privacy' in e and 'same title' in e for e in bs.check(out, dup, '')))

    def test_seo_keywords_and_free_promise_in_meta(self):
        self.assertIn('AAC app', self.strings['home.title']['en'])
        for lang in ('English', 'Danish', 'Russian', 'Ukrainian', 'Arabic', 'Spanish'):
            self.assertIn(lang, self.strings['home.meta']['en'])
        for loc in bs.LOCALES:
            self.assertIn(self.strings['freeTitle'][loc], self.strings['about.meta'][loc], loc)

    def test_seo_icons_manifest_404_and_limits(self):
        import json
        for out, site in ((self.with_email, 'https://example.org'), (self.without, '')):
            self.assertTrue(os.path.isfile(os.path.join(out, 'favicon.ico')))
            manifest = json.loads(read(out, 'site.webmanifest'))
            self.assertEqual(manifest['name'], 'Amalino')
            for icon in manifest['icons']:
                self.assertTrue(os.path.isfile(os.path.join(out, icon['src'])), icon['src'])
            self.assertEqual(bs.png_size(os.path.join(out, 'assets', 'apple-touch-icon.png')), (180, 180))
            for loc in bs.LOCALES:
                for page in bs.PAGES:
                    page_html = read(out, loc, bs.page_path(page))
                    h = bs.seo(page_html)
                    self.assertLessEqual(len(h.title.strip()), bs.TITLE_MAX, f'{loc}/{page}')
                    self.assertLessEqual(len(h.metas('description')[0]), bs.DESCRIPTION_MAX, f'{loc}/{page}')
                    self.assertEqual(len(h.metas('theme-color')), 2)
                    self.assertIn('rel="apple-touch-icon"', page_html)
                    self.assertIn('rel="manifest"', page_html)
            nf = os.path.join(out, '404.html')
            if site:
                page_html = read(out, '404.html')
                self.assertIn('<meta name="robots" content="noindex">', page_html)
                for loc in bs.LOCALES:
                    self.assertIn(f'href="/{loc}/"', page_html)
            else:
                self.assertFalse(os.path.exists(nf), '404 needs the site root')

    def test_picker_redirect_skips_crawlers(self):
        # Crawlers stay on the picker and follow its links; there's no meta refresh.
        for target in ('index.html', os.path.join('translate', 'index.html')):
            page_html = read(self.with_email, target)
            self.assertIn('navigator.userAgent', page_html)
            self.assertNotIn('http-equiv="refresh"', page_html.lower())
            for loc in bs.LOCALES:
                self.assertIn(f'hreflang="{loc}"', page_html)

    def test_seo_json_ld_on_home(self):
        import json
        for out, site in ((self.with_email, 'https://example.org'), (self.without, '')):
            for loc in bs.LOCALES:
                h = bs.seo(read(out, loc, 'index.html'))
                blocks = [json.loads(b) for b in h.ld]
                apps = [b for b in blocks if b['@type'] == 'SoftwareApplication']
                orgs = [b for b in blocks if b['@type'] == 'Organization']
                self.assertEqual(len(apps), 1)
                # The Organization once: the English home page, only with a site URL.
                self.assertEqual(len(orgs), 1 if (site and loc == 'en') else 0, loc)
                if orgs:
                    self.assertEqual(orgs[0]['url'], f'{site}/')
                    self.assertEqual(orgs[0]['sameAs'], [bs.REPO_URL])
                    self.assertNotIn('aggregateRating', orgs[0])
                data = apps[0]
                self.assertEqual(data['@type'], 'SoftwareApplication')
                self.assertEqual(data['name'], 'Amalino')
                self.assertEqual(data['operatingSystem'], 'iOS, Android')
                self.assertEqual(data['offers'], {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'})
                self.assertEqual(data['inLanguage'], bs.LOCALES)
                self.assertEqual(data['description'], self.strings['home.meta'][loc])
                for claim in ('aggregateRating', 'review', 'downloadUrl', 'installUrl', 'author'):
                    self.assertNotIn(claim, data)
                if site:
                    self.assertEqual(data['url'], f'{site}/{loc}/')
                else:
                    self.assertNotIn('url', data)
                for page in ('about', 'translate', 'privacy'):
                    self.assertEqual(bs.seo(read(out, loc, bs.page_path(page))).ld, [])

    def test_seo_open_graph_and_image(self):
        self.assertEqual(bs.png_size(os.path.join(self.with_email, 'assets', 'og-image.png')), (1200, 630))
        self.assertEqual(bs.png_size(bs.OG_IMAGE), (1200, 630))
        h = bs.seo(read(self.with_email, 'ar', 'about', 'index.html'))
        self.assertEqual(h.metas('og:locale'), ['ar_AR'])
        self.assertEqual(sorted(h.metas('og:locale:alternate')),
                         sorted(v for k, v in bs.OG_LOCALES.items() if k != 'ar'))
        self.assertEqual(h.metas('og:url'), ['https://example.org/ar/about/'])
        self.assertEqual(h.metas('og:image'), ['https://example.org/assets/og-image.png'])
        self.assertEqual(h.metas('twitter:card'), ['summary_large_image'])
        self.assertEqual(h.metas('og:title'), [h.title])
        self.assertEqual(h.metas('og:type'), ['website'])

    def test_seo_nothing_absolute_without_a_site_url(self):
        self.assertFalse(os.path.exists(os.path.join(self.without, 'sitemap.xml')))
        self.assertFalse(os.path.exists(os.path.join(self.without, 'robots.txt')))
        for f in self.all_pages(self.without):
            page = read(self.without, f)
            head = page.split('</head>')[0]
            self.assertEqual([u for u in re.findall(r'https?://[^"\s<>]+', head) if u != 'https://schema.org'], [], f)
            h = bs.seo(page)
            self.assertEqual((h.canonical(), h.alternates(), h.metas('og:url'), h.metas('og:image')), ([], [], [], []))
            self.assertEqual(h.metas('twitter:card'), ['summary'])
            self.assertTrue(h.metas('og:title'))

    def test_seo_headings_alt_and_weight(self):
        for out in (self.with_email, self.without):
            for f in self.all_pages(out):
                h = bs.seo(read(out, f))
                self.assertEqual(h.headings.count(1), 1, f)
                self.assertEqual(h.headings[0], 1, f)
                self.assertTrue(all(b <= a + 1 for a, b in zip(h.headings, h.headings[1:])), (f, h.headings))
                self.assertTrue(all('alt' in i for i in h.imgs), f)
                self.assertLessEqual(os.path.getsize(os.path.join(out, f)), bs.MAX_PAGE_BYTES, f)
        errors = self.seo_errors('<html lang="en"><title>x</title><h1>a</h1><h3>b</h3><img src="a.png">')
        self.assertTrue(any('heading h1 is followed by h3' in e for e in errors), errors)
        self.assertTrue(any('has no alt' in e for e in errors), errors)

    def seo_errors(self, body):
        out = os.path.join(self.tmp.name, 'seo')
        os.makedirs(os.path.join(out, 'assets'), exist_ok=True)
        with open(os.path.join(out, 'p.html'), 'w', encoding='utf-8') as f:
            f.write(body)
        return bs.check_seo(out, ['p.html'], '')

    def test_seo_guard_reads_share_text(self):
        page = '<meta property="og:description" content="Works with eye gaze.">'
        self.assertTrue(bs.forbidden_found(page, 'en'))

    # ------------------------------------------------------------ donation link (OVK_DONATE_URL)

    def test_donate_hidden_while_empty(self):
        for out in (self.with_email, self.without):
            for f in self.all_pages(out):
                page = read(out, f)
                self.assertNotIn('footer-support', page, f)
                self.assertNotIn('id="support"', page, f)
                self.assertNotIn(self.strings['support.title']['en'], page, f)
        self.assertEqual(bs.clean_donate('http://ko-fi.com/x'), '')
        self.assertEqual(bs.clean_donate('ko-fi.com/x'), '')
        self.assertEqual(bs.clean_donate('https://ko-fi.com/x" onclick="y'), '')
        self.assertEqual(bs.clean_donate(' https://ko-fi.com/amalino '), 'https://ko-fi.com/amalino')

    def test_donate_shown_when_set(self):
        donate = 'https://ko-fi.com/example'
        out = os.path.join(self.tmp.name, 'donate')
        with redirect_stdout(io.StringIO()):
            bs.build(out, '', 'https://example.org', self.strings, donate=donate)
        self.assertEqual(bs.check(out, self.strings, '', 'https://example.org', donate), [])
        link = f'<a href="{donate}" rel="noopener">'
        for loc in bs.LOCALES:
            for page in bs.PAGES:
                html = read(out, loc, bs.page_path(page))
                self.assertIn(f'<p class="footer-support">{link}', html, (loc, page))
                self.assertEqual('id="support"' in html, page == 'about', (loc, page))
            about = bs.visible_text(read(out, loc, 'about', 'index.html'))
            for key in ('support.title', 'support.body', 'support.link'):
                self.assertIn(bs.visible_text(self.strings[key][loc]), about, (loc, key))
            self.assertIn(self.strings['freeTitle'][loc].split()[0].lower(), self.strings['support.body'][loc].lower())
        for root, _dirs, files in os.walk(out):
            for f in files:
                if f.endswith('.html'):
                    self.assertEqual(bs.external_refs(read(root, f), 'https://example.org'), [], f)
                    self.assertNotIn('<script src', read(root, f))
        # The check notices a missing footer link.
        os.remove(os.path.join(out, 'da', 'privacy', 'index.html'))
        with open(os.path.join(out, 'da', 'privacy', 'index.html'), 'w', encoding='utf-8') as f:
            f.write(read(self.without, 'da', 'privacy', 'index.html'))
        self.assertTrue(any('da/privacy' in e and 'footer support' in e
                            for e in bs.check(out, self.strings, '', '', donate)))

    def test_draft_banner_on_unreviewed_languages_only(self):
        self.assertNotIn('draft-banner', read(self.without, 'en', 'index.html'))
        for loc in ('da', 'ru', 'uk', 'ar', 'es', 'lt'):
            self.assertIn('draft-banner', read(self.without, loc, 'index.html'))

    def test_privacy_page_is_a_draft_with_the_ml_kit_line(self):
        html = read(self.without, 'en', 'privacy', 'index.html')
        self.assertIn(self.strings['pr.draft']['en'], html)
        self.assertIn('ML Kit sends Google anonymous performance and usage metrics', html)
        self.assertNotIn('For schools', html)

    def test_decision31_nothing_loaded_from_other_hosts(self):
        for out, site in ((self.with_email, 'https://example.org'), (self.without, '')):
            for root, _dirs, files in os.walk(out):
                for f in files:
                    if f.endswith(('.html', '.css')):
                        self.assertEqual(bs.external_refs(read(root, f), site), [], os.path.join(root, f))
        self.assertNotIn('fonts.googleapis', read(bs.STYLE))

    def test_decision31_guard_catches_external_resources_but_not_links(self):
        found = bs.external_refs(read(FIXTURE))
        self.assertIn('https://fonts.googleapis.com/css2?family=Inter', found)
        self.assertIn('//cdn.example.com/app.js', found)
        self.assertTrue(any('fonts.example.com' in u for u in found), found)
        self.assertTrue(any('example.com/bg.png' in u for u in found), found)
        self.assertFalse(any('arasaac.org' in u for u in found), found)
        page = '<link rel="canonical" href="https://example.org/en/"><link rel="stylesheet" href="https://example.org/x.css">'
        self.assertEqual(bs.external_refs(page, 'https://example.org'), ['https://example.org/x.css'])

    def test_decision27_story_on_about_and_short_form_on_home(self):
        for loc in bs.LOCALES:
            about = bs.visible_text(bs.main_part(read(self.without, loc, 'about', 'index.html')))
            for key in ('about.story', 'about.p1', 'about.p2', 'about.p3', 'about.p4'):
                self.assertIn(bs.visible_text(self.strings[key][loc]), about)
            home = bs.visible_text(bs.main_part(read(self.without, loc, 'index.html')))
            self.assertIn(bs.visible_text(self.strings['home.story'][loc]), home)
        self.assertTrue(self.strings['about.story']['en'].startswith("I've always believed that technology is at its best"))
        self.assertTrue(self.strings['about.p4']['en'].endswith("If your child uses Amalino, I'd really love to hear from you."))

    def test_decision32_no_therapist_exception(self):
        self.assertIn("That's why I'm building Amalino. A free, offline communication app", self.strings['about.p3']['en'])
        for html_text, lang in (('<p>Amalino: free, offline, and built with families and therapists.</p>', 'en'),
                                ('<p>Ask your therapist.</p>', 'en'),
                                ('<p>Built with families and specialists.</p>', 'en'),
                                ('<p>bygget sammen med familier og terapeuter</p>', 'da'),
                                ('<p>созданное вместе с семьями и специалистами</p>', 'ru'),
                                ('<p>створений разом із родинами й фахівцями</p>', 'uk'),
                                ('<p>بالتعاون مع العائلات والمعالجين</p>', 'ar'),
                                ('<p>creado junto con familias y terapeutas</p>', 'es'),
                                ('<p>sukurta kartu su šeimomis ir specialistais</p>', 'lt')):
            for page in (None, 'about', 'privacy'):
                self.assertTrue(bs.forbidden_found(html_text, lang, page), (html_text, page))

    def test_decision33_github_named_and_linked_but_never_the_apps_code(self):
        # Relaxed 2026-10-14: the website, manual and translations are on GitHub; the voice host line stays.
        for loc in bs.LOCALES:
            phrase = bs.ALLOWED_PRIVACY[loc]
            self.assertIn(phrase, bs.visible_text(read(self.without, loc, 'privacy', 'index.html')).lower(), loc)
            for page in (None, 'home', 'about', 'translate', 'privacy'):
                self.assertEqual(bs.forbidden_found(f'<p>{phrase}.</p>', loc, page), [], (loc, page))
            # Every page links to the repository in its footer; the translate page in both cases.
            for page in ('home', 'about', 'translate', 'privacy'):
                self.assertIn(f'<p class="footer-repo"><a href="{bs.REPO_URL}"', read(self.without, loc, *bs.page_path(page).split('/')), (loc, page))
            tr = read(self.without, loc, 'translate', 'index.html')
            self.assertEqual(tr.count(f'<p class="repo">'), 2, loc)
        for text in ('Website, manual and translations on GitHub.', 'Fix a translation on GitHub.'):
            self.assertEqual(bs.forbidden_found(f'<p>{text}</p>', 'en', 'translate'), [], text)
        for text, lang in (('Our code is on GitHub.', 'en'), ('The source code is on GitHub too.', 'en'), ('Amalino is open source.', 'en'),
                           ('GitHub has all the code.', 'en'), ('Код приложения лежит на GitHub.', 'ru'), ('El código está en GitHub.', 'es'),
                           ('Koden ligger på GitHub.', 'da'), ('الكود على GitHub.', 'ar'),
                           ('Programėlės kodas yra GitHub.', 'lt'), ('Amalino turi atvirąjį kodą.', 'lt')):
            self.assertTrue(bs.forbidden_found(f'<p>{text}</p>', lang, 'about'), text)
        for text in ('Kodėl GitHub?', 'Klauskite, kodėl vertimai yra GitHub.'):
            self.assertEqual(bs.forbidden_found(f'<p>{text}</p>', 'lt', 'about'), [], text)
        for text, lang in ():
            self.assertTrue(bs.forbidden_found(f'<p>{text}</p>', lang, 'about'), text)

    def test_decision33_only_the_repository_link_on_github(self):
        out = os.path.join(self.tmp.name, 'otherlink')
        bad = dict(self.strings)
        with redirect_stdout(io.StringIO()):
            bs.build(out, '', '', bad)
        page = os.path.join(out, 'en', 'index.html')
        with open(page, encoding='utf-8') as f:
            html_text = f.read()
        with open(page, 'w', encoding='utf-8') as f:
            f.write(html_text.replace('</main>', '<a href="https://github.com/someone/else">x</a></main>'))
        errors = bs.check(out, bad, '')
        self.assertTrue(any('GitHub link https://github.com/someone/else' in e for e in errors), errors)

    def test_decision30_privacy_names_hosts_and_app_labels(self):
        app = bs.load_app_strings()
        for loc in bs.LOCALES:
            text = bs.visible_text(read(self.without, loc, 'privacy', 'index.html'))
            for host in ('arasaac.org', 'globalsymbols.com', 'github.com'):
                self.assertIn(host, text, loc)
            for key in ('arasaacFull', 'moreSymbolSets', 'aiListen', 'aiContext', 'suggestHotspots', 'exportBackup'):
                self.assertIn(app[key][loc], text, f'{loc} {key}')
            self.assertIn(app['naturalVoicesHeading'][loc], text, loc)
            self.assertIn(bs.visible_text(self.strings['pr.draft'][loc]), text)
            self.assertNotIn('{app:', read(self.without, loc, 'privacy', 'index.html'))
        # No cookies (decision 31): no script sets one; the privacy page says so in words.
        page = read(self.without, 'en', 'privacy', 'index.html')
        self.assertNotIn('cookie', ' '.join(re.findall(r'<script\b[^>]*>(.*?)</script>', page, flags=re.S)).lower())
        self.assertIn(self.strings['pr.webNoCookies']['en'], bs.visible_text(page))

    def test_arabic_latin_runs_are_isolated(self):
        html = read(self.without, 'ar', 'translate', 'index.html')
        self.assertIn('<bdi dir="ltr">OK?</bdi>', html)


class Inputs(unittest.TestCase):
    def tables(self, texts):
        """A translations folder with one key per language ({loc: text or None for a missing file row})."""
        tmp = tempfile.TemporaryDirectory()
        for loc in bs.LOCALES:
            os.makedirs(os.path.join(tmp.name, loc))
            with open(os.path.join(tmp.name, loc, 'website.tsv'), 'w', encoding='utf-8') as f:
                f.write('# key\ttext\n')
                for key, text in texts.get(loc, {'k': loc}).items():
                    f.write(f'{key}\t{text}\n')
        return tmp

    def test_missing_translation_fails(self):
        with self.tables({'ru': {}}) as folder:
            with self.assertRaisesRegex(bs.BuildError, 'k has no text for ru'):
                bs.load_strings(folder)

    def test_empty_or_unknown_key_fails(self):
        with self.tables({'da': {'k': ' '}}) as folder:
            with self.assertRaisesRegex(bs.BuildError, 'k has no text'):
                bs.load_strings(folder)
        with self.tables({'es': {'k': 'es', 'extra': 'x'}}) as folder:
            with self.assertRaisesRegex(bs.BuildError, 'extra is not in the English file'):
                bs.load_strings(folder)

    def test_contact_rules_match_the_app(self):
        self.assertEqual(bs.clean_email(' a@b.org '), 'a@b.org')
        self.assertEqual(bs.clean_email('not an address'), '')
        self.assertEqual(bs.clean_site('https://amalino.app/'), 'https://amalino.app')
        self.assertEqual(bs.clean_site('http://amalino.app'), '')


class Manual(unittest.TestCase):
    """The user manual (manual/<lang>/*.md) on the site, and the privacy page's website part."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.strings = bs.load_strings()
        cls.out = os.path.join(cls.tmp.name, 'site')
        cls.plain = os.path.join(cls.tmp.name, 'plain')
        with redirect_stdout(io.StringIO()):
            cls.summary = bs.build(cls.out, EMAIL, 'https://example.org', cls.strings)
            bs.build(cls.plain, '', '', cls.strings)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_english_manual_is_built_in_contents_order(self):
        names = bs.manual_pages('en')
        self.assertEqual(names[0], 'index')
        self.assertGreaterEqual(len(names), 13)
        self.assertEqual(self.summary['manual'], {'en': names})
        for n in names:
            self.assertTrue(os.path.isfile(os.path.join(self.out, 'en', bs.manual_path(n))), n)
        self.assertEqual(bs.check(self.out, self.strings, EMAIL, 'https://example.org'), [])
        self.assertEqual(bs.check(self.plain, self.strings, '', ''), [])

    def test_manual_page_has_edit_link_steps_contents_and_marked_menu(self):
        names = bs.manual_pages('en')
        page = read(self.out, 'en', bs.manual_path('scenes'))
        self.assertIn(f'href="{bs.REPO_URL}/edit/main/manual/en/scenes.md"', page)
        i = names.index('scenes')
        self.assertIn(f'href="../{names[i - 1]}/index.html" rel="prev"', page)
        self.assertIn(f'href="../{names[i + 1]}/index.html" rel="next"', page)
        toc = re.search(r'<nav class="manual-toc".*?</nav>', page, flags=re.S).group(0)
        self.assertEqual(toc.count('<li>'), len(names))
        menu = re.search(r'<nav class="site-nav".*?</nav>', page, flags=re.S).group(0)
        self.assertIn('manual/index.html" aria-current="page"', menu)
        self.assertIn('<title>Scenes · Amalino manual</title>', page)
        self.assertNotIn('rel="prev"', read(self.out, 'en', bs.manual_path('index')))

    def test_manual_links_resolve_and_contributing_goes_to_the_repository(self):
        index = read(self.out, 'en', bs.manual_path('index'))
        self.assertIn('href="getting-started/index.html"', index)
        self.assertIn(f'href="{bs.REPO_URL}/blob/main/CONTRIBUTING.md"', index)
        board = read(self.out, 'en', bs.manual_path('the-board'))
        self.assertIn('href="../quick-phrases/index.html"', board)
        self.assertNotIn('.md"', board.replace(f'{bs.REPO_URL}/edit/main/manual/en/the-board.md"', ''))
        self.assertNotIn('screenshot:', board, 'HTML comments are not published')

    def test_other_languages_link_to_the_english_manual(self):
        for loc in bs.LOCALES:
            page = read(self.out, loc, 'index.html')
            label = self.strings['nav.manual' if loc == 'en' else 'nav.manualEn'][loc]
            want = '../en/manual/index.html"' + ('' if loc == 'en' else ' hreflang="en"')
            self.assertIn(want, page, loc)
            self.assertIn(label, page, loc)
            self.assertIn('<p class="footer-manual"><a href="../en/manual/index.html"', page, loc)
        # The manual page's own language menu: languages without a manual go to their home page.
        page = read(self.out, 'en', bs.manual_path('voices'))
        self.assertIn('href="../../../da/index.html" lang="da"', page)

    def test_manual_seo_only_its_own_languages(self):
        h = bs.seo(read(self.out, 'en', bs.manual_path('keyboard')))
        self.assertEqual(h.canonical(), ['https://example.org/en/manual/keyboard/'])
        self.assertEqual(dict(h.alternates()), {'en': 'https://example.org/en/manual/keyboard/',
                                                'x-default': 'https://example.org/en/manual/keyboard/'})
        self.assertEqual(h.metas('og:locale:alternate'), [])
        self.assertLessEqual(len(h.metas('description')[0]), bs.DESCRIPTION_MAX)
        self.assertIn('https://example.org/en/manual/keyboard/', read(self.out, 'sitemap.xml'))

    def test_manual_text_follows_the_public_text_rules(self):
        for n in bs.manual_pages('en'):
            self.assertEqual(bs.forbidden_found(read(self.out, 'en', bs.manual_path(n)), 'en'), [], n)

    def test_markdown_subset(self):
        md = ('<!-- description: A page. -->\n# Title with **bold**\n\nText with *it*, `code` and a [link](b.md).\n'
              '<!-- screenshot: x -->\n\n## Part two\n\n- one\n- two\n  continued\n\n1. first\n2. second\n\n'
              '> **Tip:** wait.\n')
        title, desc, body = bs.md_to_html(md, lambda h: 'B/' if h == 'b.md' else h)
        self.assertEqual((title, desc), ('Title with bold', 'A page.'))
        self.assertIn('<h1>Title with <strong>bold</strong></h1>', body)
        self.assertIn('<p>Text with <em>it</em>, <code>code</code> and a <a href="B/">link</a>.</p>', body)
        self.assertIn('<h2 id="part-two">Part two</h2>', body)
        self.assertIn('<ul><li>one</li><li>two continued</li></ul>', body)
        self.assertIn('<ol><li>first</li><li>second</li></ol>', body)
        self.assertIn('<blockquote><p><strong>Tip:</strong> wait.</p></blockquote>', body)
        self.assertNotIn('screenshot', body)
        self.assertIn('&lt;b&gt;', bs.md_to_html('# T\n\n<b>x</b>\n', str)[2])
        with self.assertRaises(bs.BuildError):
            bs.md_to_html('no heading\n', str)

    def test_markdown_screenshots(self):
        md = '# T\n\nText.\n![The board, with "I want"](img/board-phone.png)\nMore.\n'
        body = bs.md_to_html(md, str, lambda src, alt: f'<IMG {src} | {alt}>')[2]
        self.assertIn('<p>Text.</p>\n<IMG img/board-phone.png | The board, with "I want">\n<p>More.</p>', body)
        with self.assertRaises(bs.BuildError):
            bs.md_to_html(md, str)  # no image drawer: images are only for manual pages
        self.assertNotIn('<IMG', bs.md_to_html('# T\n\n![](img/x.png)\n', str, lambda s, a: '<IMG>')[2], 'alt is required')

    def test_manual_screenshots_are_built_with_size_and_alt(self):
        folder = os.path.join(bs.MANUAL, 'en')
        for n in sorted(os.listdir(folder)):
            if not n.endswith('.md'):
                continue
            name = n[:-3]
            for alt, src in re.findall(r'^!\[([^\]]+)\]\((img/[^)]+)\)$', read(folder, n), flags=re.M):
                page = read(self.out, 'en', bs.manual_path(name))
                w, h = bs.png_size(os.path.join(folder, src))
                prefix = '' if name == 'index' else '../'
                self.assertIn(f'<img src="{prefix}{src}" alt="{html.escape(alt, quote=True)}" width="{w}" height="{h}"', page)
                self.assertTrue(os.path.isfile(os.path.join(self.out, 'en', 'manual', src)), src)

    def test_manual_rejects_unknown_links(self):
        link = bs.manual_link('en', 'scenes', ['index', 'scenes', 'editing'])
        self.assertEqual(link('editing.md'), '../editing/index.html')
        self.assertEqual(link('index.md'), '../index.html')
        self.assertEqual(link('editing.md#undo'), '../editing/index.html#undo')
        for bad in ('missing.md', '../other.md', 'file.txt', '../../../x.md'):
            with self.assertRaises(bs.BuildError, msg=bad):
                link(bad)

    def test_privacy_page_website_part(self):
        for loc in bs.LOCALES:
            page = read(self.out, loc, 'privacy', 'index.html')
            for url in bs.OUTSIDE_LINKS.values():
                self.assertIn(f'href="{url}"', page, loc)
            text = bs.visible_text(page)
            self.assertIn('GitHub Pages', text, loc)
            self.assertIn('Cloudflare', text, loc)
        self.assertNotIn('Email Routing', bs.visible_text(read(self.plain, 'en', 'privacy', 'index.html')))
        self.assertIn('Email Routing', bs.visible_text(read(self.out, 'en', 'privacy', 'index.html')))

    def test_outside_link_must_be_known(self):
        strings = dict(self.strings)
        strings['pr.webHosts'] = dict(strings['pr.webHosts'], en='See [[this|somewhere]].')
        with self.assertRaisesRegex(bs.BuildError, "unknown link 'somewhere'"):
            bs.Renderer(strings, EMAIL, '').html_text('pr.webHosts', 'en')
        self.assertNotIn('[[', bs.Renderer(self.strings, EMAIL, '').plain('pr.webHosts', 'en'))


if __name__ == '__main__':
    unittest.main()
