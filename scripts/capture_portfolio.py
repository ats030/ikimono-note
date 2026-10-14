"""Capture actual local-profile UI using labelled fixtures and zero external requests."""
from io import BytesIO
import json
import mimetypes
from pathlib import Path
import tempfile

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / 'docs/media'
ORIGIN = 'http://portfolio.invalid'
SETTINGS = {
    'provider': 'gemini', 'public_mode': True, 'browser_photos': False,
    'native_transport': False, 'browser_gemini': False, 'local_in_browser': True,
    'models': {'gemini': 'gemini-3.5-flash-lite', 'local': 'gemma4:12b'},
    'available_models': {'gemini': [{'id': 'gemini-3.5-flash-lite', 'label': 'Gemini 3.5 Flash-Lite'}],
                         'local': [], 'openai': [], 'anthropic': []},
    'api_key_configured': {'gemini': False, 'openai': False, 'anthropic': False, 'plantnet': False},
    'google_client_id': '', 'local_llm': {'url': ''}, 'incompatible_local_models': [],
    'affiliate': {'enabled': False, 'product_enabled': False, 'url': '', 'title': '',
                  'partner_tag': '', 'metrics': {'impressions': 0, 'clicks': 0}},
}
RESULT = {
    'category': '植物', 'summary': 'タンポポの仲間が候補です。花の裏側を撮り足すと、比較できます。',
    'strict_mode': True, 'taxonomy_checked': True, 'plantnet_used': False,
    'model': 'gemini-3.5-flash-lite', 'candidates': [{
        'common_name_ja': 'セイヨウタンポポ', 'scientific_name': 'Taraxacum officinale',
        'taxon_rank': 'species', 'confidence': 40, 'evidence_status': 'uncertain',
        'taxonomy_status': 'verified', 'taxonomy_url': 'https://www.inaturalist.org/taxa/47602',
        'traits': ['黄色い花', '地面近くに広がる葉'],
        'distinguishing_features': [], 'contradictions': [],
        'evidence_gaps': ['花の裏側が見えず、似た種との識別点を確認できません。'],
        'uncertainty': '総苞外片が反り返っているか、花の裏側で確かめてください。',
        'sex': '対象外',
    }],
}


def sample_image():
    """An original geometric test illustration, not a biological photograph."""
    image = Image.new('RGB', (960, 640), '#e6eedb')
    draw = ImageDraw.Draw(image)
    for x in range(0, 960, 45):
        draw.line([(x, 640), (x + 70, 420)], fill='#cad8ba', width=3)
    draw.line([(480, 490), (480, 250)], fill='#5e8643', width=12)
    for x, y, direction in [(470, 435, -1), (485, 415, 1), (470, 475, -1), (485, 470, 1)]:
        draw.polygon([(x, y), (x + direction * 160, y - 70), (x + direction * 125, y - 15),
                      (x + direction * 180, y + 20), (x, y + 15)], fill='#5d873e')
    for dx, dy in [(-65, -35), (0, -65), (65, -35), (65, 35), (0, 65), (-65, 35)]:
        draw.ellipse((440 + dx, 210 + dy, 520 + dx, 290 + dy), fill='#efc945')
    draw.ellipse((440, 210, 520, 290), fill='#d59b27')
    buf = BytesIO()
    image.save(buf, 'JPEG', quality=90)
    return buf.getvalue()


def main():
    MEDIA.mkdir(parents=True, exist_ok=True)
    raw = MEDIA / 'raw'
    raw.mkdir(exist_ok=True)
    requests, errors, snapshots = [], [], []
    label = '展示用：固定の識別応答と合成図／実AIの精度や本番動作を示すものではありません'
    with sync_playwright() as playwright, tempfile.TemporaryDirectory(prefix='portfolio-video-') as video_dir:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1100, 'height': 820},
                                      locale='ja-JP', color_scheme='light',
                                      record_video_dir=video_dir, record_video_size={'width': 1100, 'height': 820})

        def route_request(route):
            from urllib.parse import urlparse
            request = route.request
            url = urlparse(request.url)
            requests.append({'method': request.method, 'path': url.path})
            if f'{url.scheme}://{url.netloc}' != ORIGIN:
                errors.append('Unexpected external request: ' + url.netloc)
                route.abort()
                return
            if url.path == '/api/settings' and request.method == 'GET':
                route.fulfill(json=SETTINGS)
                return
            if url.path == '/api/me' and request.method == 'GET':
                route.fulfill(json={'available': False, 'signed_in': False})
                return
            if url.path == '/api/photo-metadata' and request.method == 'POST':
                route.fulfill(json={})
                return
            if url.path == '/identify' and request.method == 'POST':
                route.fulfill(json=RESULT)
                return
            if request.method != 'GET':
                errors.append('Unexpected write: ' + url.path)
                route.abort()
                return
            name = {'/': 'index.html', '/settings': 'settings.html', '/history': 'history.html'}.get(url.path, url.path.lstrip('/'))
            path = (ROOT / 'static' / name).resolve()
            if not path.is_relative_to(ROOT / 'static') or not path.is_file():
                errors.append('Missing asset: ' + url.path)
                route.fulfill(status=404, body='')
                return
            body = path.read_bytes()
            content_type = 'text/javascript' if path.suffix in {'.js', '.mjs'} else mimetypes.guess_type(path)[0] or 'application/octet-stream'
            if path.suffix == '.html':
                body = body.decode().replace('<body', '<body data-app-mode="public" data-show-local="1" data-browser-photos="0"')
                body = body.replace('</head>', '<style>body{padding-top:42px}.portfolio-label{position:fixed;top:0;left:0;right:0;z-index:10000;background:#20382b;color:#fff;padding:10px 16px;font:13px sans-serif;text-align:center}</style></head>')
                body = body.replace('<main', '<div class="portfolio-label">' + label + '</div><main', 1)
            route.fulfill(body=body, content_type=content_type)

        context.route('**/*', route_request)
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))

        def shot(name):
            page.wait_for_timeout(1400)
            page.screenshot(path=str(MEDIA / name), full_page=True)
            frame = raw / f'{len(snapshots):02}.png'
            page.screenshot(path=str(frame))
            snapshots.append(frame)

        page.goto(ORIGIN)
        page.locator('#setupWelcome').wait_for(state='visible')
        shot('01-welcome.png')
        page.locator('#startSetup').click()
        page.locator('#quickSetup').wait_for(state='visible')
        page.locator('#quickGeminiKey').fill('synthetic-key-not-a-real-credential')
        page.locator('#quickKeepKey').uncheck()
        shot('02-settings.png')
        page.get_by_role('button', name='保存して写真を選ぶ').click()
        page.wait_for_url('**/?setup=done')
        page.locator('#library').set_input_files({'name': 'synthetic-flower.jpg', 'mimeType': 'image/jpeg', 'buffer': sample_image()})
        page.locator('#identify').wait_for(state='visible')
        page.wait_for_function('!captureLocationPicker?.isBusy')
        shot('03-photo.png')
        page.locator('#identify').click()
        page.locator('#results').get_by_text('セイヨウタンポポ', exact=False).first.wait_for()
        page.wait_for_function('lastSavedRecordId !== ""')
        page.locator('#results').scroll_into_view_if_needed()
        shot('04-result.png')
        page.goto(ORIGIN + '/history')
        page.locator('.entry').wait_for()
        assert page.locator('.entry').count() == 1
        assert '決め手なし' in page.locator('.entry').inner_text()
        shot('05-history.png')
        page.reload()
        page.locator('.entry').wait_for()
        assert page.locator('.entry').count() == 1, 'Record did not survive reload'
        page.locator('.entry details').first.locator('summary').click()
        shot('06-detail.png')
        context.close()
        page.video.save_as(str(MEDIA / 'walkthrough.webm'))
        browser.close()
        assert not errors, errors
    frames = [Image.open(path).convert('RGB') for path in snapshots]
    frames[0].save(MEDIA / 'walkthrough.gif', save_all=True, append_images=frames[1:], duration=1800, loop=0)
    report = {'profile': 'actual local frontend; routed fixtures; no AI or account calls',
              'viewport': {'width': 1100, 'height': 820}, 'screenshots': len(snapshots),
              'assertions': ['first-use setup', 'photo selection', 'uncertain candidate rendering',
                             'IndexedDB record creation', 'record persistence after reload', 'no external requests', 'no page errors'],
              'requests': requests, 'errors': errors}
    (MEDIA / 'capture-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print('PASS: captured labelled walkthrough, real UI and record persistence; no external requests')


if __name__ == '__main__':
    main()
