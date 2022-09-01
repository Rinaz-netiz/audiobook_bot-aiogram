import shutil
from back import bot
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from aiofile import Writer, AIOFile
import os
import aiofiles


async def request(url: str, text: str):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8, '
                  'application/signed-exchange;v=b3;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/104.0.0.0 Safari/537.36 '
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, headers=headers) as resp:
            if text == 'text':
                r = await resp.text()
                return r
            elif text == 'read':
                r = await resp.read()
                return r


async def find_audiobooks(name: str):
    url = f'https://archive.org/details/audioboo_ru?query={name.replace(" ", "+").lower()}'

    data = asyncio.create_task(request(url, 'text'))
    text = await data
    soup = BeautifulSoup(text, 'lxml')
    block_div = soup.find('div', class_='results').find_all('div', class_='item-ia')

    audio_dict_list = []
    count = 0
    for i in block_div[1:]:
        audio_title = i.find('div', class_='C234').find('a')['title']
        audio_url = i.find('div', class_='C234').find('a')['href'].split('/')[-1]
        count += 1
        audio_dict_list.append(
            {
                'title': audio_title.strip(),
                'url': '/' + audio_url,
                'number': count
            }
        )

    string = ''
    for item in audio_dict_list:
        string += f'\n{item["number"]}. {item["title"]} \n' \
                  f'download: {item["url"]}\n'

    return string


async def download_file(file_t, part, id_m):
    if not os.path.exists('data/'):
        os.mkdir('data/')

    async with AIOFile(f'data/{part}.mp3', 'wb') as file:
        writer = Writer(file)
        await writer(file_t)

    try:
        async with aiofiles.open(f'data/{part}.mp3', mode='rb') as f:
            contents = await f.read()

        await bot.send_audio(id_m, contents, title=part)
    except PermissionError:
        await asyncio.sleep(1)


async def first_url(address: str, id_m):
    url = 'https://archive.org/details' + address

    data = asyncio.create_task(request(url, 'text'))
    text = await data

    soup = BeautifulSoup(text, 'lxml')
    block = soup.find('div', id="theatre-ia-wrap").find_all('div')

    title_mp3 = []
    for item in block:
        try:
            part = item.find('meta')['content']
            title_mp3.append(part)
            mp3_url = asyncio.create_task(request(item.find_all('link')[-1]['href'], 'read'))
            mp3_content = await mp3_url

            asyncio.create_task(download_file(mp3_content, part, id_m))

        except TypeError:
            break

    return title_mp3


async def delete_folder():
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
    shutil.rmtree(path)
