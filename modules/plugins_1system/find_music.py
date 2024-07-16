from pyrogram import Client, filters
from modules.plugins_1system.settings.main_settings import module_list, file_list
from prefix import my_prefix

import json
import os
import requests
from lyricsgenius import Genius

api_token = '9JiBRxKAEgfssIWg3Yw8uxKyDO0HZr1IQS5qVYQiKMLwJ4d_9tEMxxYlm3w_mIML' # genius api key

l = Genius(api_token)
@Client.on_message(filters.command(["l", "lyrics"], prefixes=my_prefix()) & filters.me)
async def send_music(client, message):
    if len(message.text.split()) >= 2:
        await client.edit_message_text(message.chat.id, message.id, 'Searching text...')
        url = {"Authorization": f"Bearer {api_token}"}
        song_name = ' '.join(message.text.split()[1:])
        text = song_name.lower().replace(' ', '%20')
        q = requests.get(f'https://api.genius.com/search?q={text}', headers=url).text
        data_dict = json.loads(q)
        try:
            url_song = data_dict['response']['hits'][0]['result']['url']
            lyrics = l.lyrics(song_url=url_song).replace('Embed','')
            with open('song_text.txt','w+',encoding='utf-8') as file:
                file.write(lyrics)
            await client.send_document(message.chat.id, 'song_text.txt', caption='Keep the lyrics this song!')
            os.remove('song_text.txt')
        except Exception as e:
            await client.edit_message_text(message.chat.id, message.id, "I can't find text!")
    else:
        await client.edit_message_text(message.chat.id, message.id, 'Give me a name song!')
module_list['FindMusic'] = f'{my_prefix()}lyrics [Title on music]'
file_list['FindMusic'] = 'find_music.py'
