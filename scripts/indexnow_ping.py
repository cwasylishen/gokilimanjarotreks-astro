"""Submit the site's sitemap URLs to IndexNow (Bing, Yandex, Seznam, Naver).
Run after any deploy that adds or changes pages:
    python scripts/indexnow_ping.py
The key file (public/<KEY>.txt) must already be live on the site.
"""
import json
import re
import urllib.request

HOST = 'gokilimanjarotreks.com'
KEY = '1371ace07c36f821e3e0ebaef1766c33'
SITEMAP = f'https://{HOST}/sitemap-0.xml'
ENDPOINT = 'https://api.indexnow.org/indexnow'


UA = {'User-Agent': 'Mozilla/5.0 (compatible; GKT-IndexNow/1.0; +https://gokilimanjarotreks.com)'}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8')


def main():
    xml = get(SITEMAP)
    urls = re.findall(r'<loc>(.*?)</loc>', xml)
    print(f'sitemap URLs: {len(urls)}')

    # sanity: key file must be live before pinging
    assert get(f'https://{HOST}/{KEY}.txt').strip() == KEY, 'key file mismatch'
    print('key file verified live')

    payload = json.dumps({
        'host': HOST,
        'key': KEY,
        'keyLocation': f'https://{HOST}/{KEY}.txt',
        'urlList': urls,
    }).encode('utf-8')
    headers = dict(UA)
    headers['Content-Type'] = 'application/json; charset=utf-8'
    req = urllib.request.Request(ENDPOINT, data=payload, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f'IndexNow response: HTTP {r.status} (200/202 = accepted)')


if __name__ == '__main__':
    main()
