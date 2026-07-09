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


def main():
    with urllib.request.urlopen(SITEMAP, timeout=30) as r:
        xml = r.read().decode('utf-8')
    urls = re.findall(r'<loc>(.*?)</loc>', xml)
    print(f'sitemap URLs: {len(urls)}')

    # sanity: key file must be live before pinging
    with urllib.request.urlopen(f'https://{HOST}/{KEY}.txt', timeout=30) as r:
        assert r.read().decode('ascii').strip() == KEY, 'key file mismatch'
    print('key file verified live')

    payload = json.dumps({
        'host': HOST,
        'key': KEY,
        'keyLocation': f'https://{HOST}/{KEY}.txt',
        'urlList': urls,
    }).encode('utf-8')
    req = urllib.request.Request(ENDPOINT, data=payload,
                                 headers={'Content-Type': 'application/json; charset=utf-8'})
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f'IndexNow response: HTTP {r.status} (200/202 = accepted)')


if __name__ == '__main__':
    main()
