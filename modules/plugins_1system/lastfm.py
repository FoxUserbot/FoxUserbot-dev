from pyrogram import Client, filters
from modules.plugins_1system.settings.main_settings import module_list, file_list
from prefix import my_prefix


from xml.dom import minidom
import urllib.request
import time
import threading
import requests
import random
import os
import asyncio


try:
    currentUsername = open("temp/lastfm_username.txt", "r").readline() 
    if len(currentUsername) == 0:
        raise ValueError
except Exception as fff:
    currentUsername = "None"


# Variable
userName = str(currentUsername)
apiKey = "460cda35be2fbf4f28e8ea7a38580730"
currentTrackURL = f'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&nowplaying=true&user={userName}&api_key={apiKey}'
runCheck = True
waitTime = 15
noSongPlaying = "Nothing Currently Playing"
killprocess = False

proxylist = []
workproxy = []


def get_proxy():
    if len(proxylist) > 0:
        prx = []
        for i in workproxy:
            prx.append(i)
            
        for i in proxylist:
            prx.append(i)
            
        return prx
    else:
        try:
            url = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&protocol=http&proxy_format=ipport&format=text&timeout=3000"
            response = requests.get(url, timeout=2)
            proxies_text = response.text

        except:
            url = "http://rootjazz.com/proxies/proxies.txt"
            response = requests.get(url, timeout=4)
            proxies_text = response.text

        # Разделение ответа на строки для каждого прокси-сервера и удаление символа \r
        proxies_list = [x.strip() for x in proxies_text.split("\n") if x.strip()]
        proxies_list = proxies_list[:200]

        # Вывод списка прокси-серверов без символа \r
        for i in proxies_list:
            proxylist.append(i)

        return proxies_list


# Функция, которая добавляет прокси и отправляет HTTP запрос
def send_request(url):
    try:
        try:
            # Отправляем запрос без использования прокси
            with urllib.request.urlopen(url, timeout=1) as response:
                return response.read()
        except:
            proxies = get_proxy()
            proxy_host = proxies[0]
            proxy_support = urllib.request.ProxyHandler({'http': proxy_host})
            opener = urllib.request.build_opener(proxy_support)
            
            # Добавляем заголовок Cache-Control: no-cache
            req = urllib.request.Request(url, headers={'Cache-Control': 'no-cache'})

            with opener.open(req, timeout=5) as response:
                result = response.read()
                if proxy_host in workproxy:
                    pass
                else:
                    workproxy.append(proxy_host)
                return result
    except Exception as fff:
        try:
            workproxy.remove(proxy_host)
        except:
            pass
        proxylist.remove(proxy_host)
        return None


# Функция checkForNewSong
def checkForNewSong():
    global runCheck
    global waitTime
    global currentTrackURL

    if userName != "None":
        while runCheck:
            try:
                currentTrackXML = None
                while currentTrackXML == None:
                    currentTrackXML = send_request(currentTrackURL)

                currentTrack = minidom.parseString(currentTrackXML)
                songName = (currentTrack.getElementsByTagName('name'))
                songArtist = (currentTrack.getElementsByTagName('artist'))
                songInfo = f"{songName[0].firstChild.nodeValue} — {songArtist[0].firstChild.nodeValue}"
                
                # Fixer
                if os.name == 'nt':
                    songInfo = songInfo.encode('cp1251', errors='ignore').decode('cp1251')
                else:
                    songInfo = songInfo.encode('utf-8', errors='ignore').decode('utf-8')
                
                
                try:
                    currentSongFile = open("temp/lastfm_current_song.txt", "r").readline()
                except:
                    currentSongFile = "Nothing Currently Playing"

                if currentSongFile != songInfo:
                    
                    currentSongFile = open("temp/lastfm_current_song.txt", "w")
                    currentSongFile.write(songInfo)
                    currentSongFile.close()

                time.sleep(waitTime)

            except Exception as fff:
                print(fff)
    else:
        print("Sleep...")



# Асинх поток
try:
    try:
        currentUsername = open("temp/lastfm_username.txt", "r").readline() 
        if len(currentUsername) == 0:
            raise ValueError
    except Exception as fff:
        currentUsername = "None"
        
    if currentUsername == "None":
        pass
    else:    
        newSongThread = threading.Thread(target=checkForNewSong)
        newSongThread.daemon = True  
        newSongThread.start()
except KeyboardInterrupt:
    raise ValueError


@Client.on_message(filters.command("nowplayed", prefixes=my_prefix()) & filters.me)
async def nowplayed(client, message):
    currentSong = open("temp/lastfm_current_song.txt", "r").readline() 
    await message.edit(f"[🎶] Now playing: `{currentSong}`")


@Client.on_message(filters.command("lastfm_config", prefixes=my_prefix()) & filters.me)
async def lastfm_config(client, message):
    username = message.text.split()[1]
    
    usernameF = open("temp/lastfm_username.txt", "w")
    usernameF.write(username)
    usernameF.close()
    
    channel_telegram = message.text.split()[2]
    
    channel_telegramF = open("temp/lastfm_channel.txt", "w")
    channel_telegramF.write(channel_telegram)
    channel_telegramF.close()
    
    id_in_channel_telegram = message.text.split()[3]
    
    id_in_channel_telegramF = open("temp/lastfm_id_in_channel_telegram.txt", "w")
    id_in_channel_telegramF.write(id_in_channel_telegram)
    id_in_channel_telegramF.close()
    
    autostart = message.text.split()[4]
    
    if autostart == "True":
        autostartF = open("temp/lastfm_autostart.txt", "w")
        autostartF.write(autostart)
        autostartF.close()
    else:
        autostart = "False"
        try:
            os.remove("temp/lastfm_autostart.txt")
        except:
            pass
    
    await message.edit(f"LastFM: {username}\nChannel: {channel_telegram}\nID: {id_in_channel_telegram}\nAutostart: {autostart}")


@Client.on_message((filters.command("autoplayed", prefixes=my_prefix()) & filters.me) | (filters.command("last_fm_trigger_start", prefixes="") & filters.me & filters.chat("me")))
async def autoplayed(client, message):
    await message.edit("STARTED!")
    
    while True:
        channel = open("temp/lastfm_channel.txt", "r").readline() 
        try:
            channel = int(channel)
        except:
            channel = str(channel)

        id_in_channel_telegram = int(open("temp/lastfm_id_in_channel_telegram.txt", "r").readline())

        currentSong = open("temp/lastfm_current_song.txt", "r").readline() 
        
        text = f"Now playing: `{currentSong}`"
        try:
            cache = open("temp/lastfm_cache.txt", "r").readline() 
        except:
            cache = "None"
        
        if str(cache) == str(text):
            pass
        else:
            try:
                await client.edit_message_text(
                    chat_id=channel,
                    message_id=id_in_channel_telegram,
                    text=F"[🎶] {text}",
                )
                # Cache
                cache = open("temp/lastfm_cache.txt", "w")
                cache.write(text)
                cache.close()
            except Exception as ff:
                print(ff)
        
        await asyncio.sleep(5)


module_list['LastFM'] = f'{my_prefix()}nowplayed | {my_prefix()}autoplayed | {my_prefix()}lastfm_config [LastFM Nickname] [Username/ID Channel] [ID Message] [Autostart: True/False]'
file_list['LastFM'] = 'lastfm.py'
