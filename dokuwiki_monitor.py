# import requests
import asyncio
from aiohttp import ClientSession

lock = asyncio.Lock()

dokuwiki_status = []

async def main():
    with open('urls.txt', 'r', encoding='utf-8') as f:
        urls = f.readlines()

    task_list = []
    for url in urls:
        url = url.strip()
        task = asyncio.create_task(check_dokuwiki(url))
        task_list.append(task)
        print('checking:', url)
    done, pending = await asyncio.wait(task_list)
    # print(dokuwiki_status)
    dokuwiki_status.sort(key=lambda x: x[1])

    with open('dokuwiki_status.txt', 'w', encoding='utf-8') as f:
        f.write('url, status , r.status, dokuwiki_status\n')
        for line in dokuwiki_status:
            f.write(str(line)+"\n")

async def check_dokuwiki(url):
    try:
        async with ClientSession(cookies=None) as session:
            async with session.get(url, timeout=30) as r:
                doku_cookies = r.cookies.get('DokuWiki')
                if doku_cookies is None:
                    text = await r.text(errors='ignore')
                    if 'dokuwiki' in text.lower():
                        async with lock:
                            dokuwiki_status.append([url, 1 , r.status, 'Cookie Not Found, HTML Contains DokuWiki'])
                    else:
                        async with lock:
                            dokuwiki_status.append([url, -1 ,r.status, 'Cookie Not Found, HTML Not Contains DokuWiki'])
                else:
                    async with lock:
                        dokuwiki_status.append([url, 2 , r.status, 'Cookie Found'])

    except Exception as e:
        async with lock:
            dokuwiki_status.append([url, -2, str(e)])

asyncio.run(main())