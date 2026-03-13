import yt_dlp
import ytmusicapi
import os
import shutil
import subprocess
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
script_path = Path(__file__).parent.absolute()

YOUTUBE_ID_LENGTH = 11

#Set your variables on .env
use_beets = os.getenv('USE_BEETS', 'True').lower() == 'true'
firefoxprofile = os.getenv('FIREFOX_PROFILE_PATH')
library_path = os.getenv('LIBRARYPATH')

#Album Searcher
def search_album(nameinput: str, nsearch: int, isAlbum: bool):
    ytm = ytmusicapi.YTMusic()
    
    if isAlbum:
        results = {}
        search = ytm.search(nameinput, filter='albums')
        for index in range(min(nsearch, len(search))):
            title = search[index]['title']
            artist = search[index]['artists'][0]['name']
            year = search[index]['year']
            ID = search[index]['playlistId']
            results[title] = {
                "artist": artist,
                "id": ID,
                "year": year
            }
        return results
    else:
        results = {}
        search = ytm.search(nameinput, filter='songs')
        for index in range(min(nsearch, len(search))):
            title = search[index]['title']
            artist = search[index]['artists'][0]['name']
            ID = search[index]['videoId']
            results[title] = {
                "artist": artist,
                "id": ID
            }
        return results


#Album Downloader
def download_album(downloadinput):

    #Direct link handling
    if downloadinput.startswith('http'):
        link = True
        url = downloadinput
        innerpath = 'Standalone'

    link = False
    innerpath = downloadinput
    tempfolder = f'{script_path}/temp/{innerpath}/'

    #Parameters
    ytparams = {
        'retries': 10,
        'fragment_retries': 20,
        'extractor_args': {
        'youtube': {
            'player_client': ['web', 'android_vr']
                }
            },
        'format': 'bestaudio[ext=m4a]/bestaudio',
        'outtmpl': tempfolder + '%(artist)s - %(title)s.%(ext)s',
        'postprocessors': [
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True, 
            }
        ]
    }

    #Add cookies if FIREFOX_PROFILE_PATH has content.
    if firefoxprofile:
        ytparams['cookiesfrombrowser'] = ('firefox', firefoxprofile)

    #Handling album and songs links.
    if not link:
        if len(downloadinput) > YOUTUBE_ID_LENGTH:
            url = f'https://music.youtube.com/playlist?list={downloadinput}'
        else:
            url = f'https://music.youtube.com/watch?v={downloadinput}'

    try:
        with yt_dlp.YoutubeDL(ytparams) as ydl:
            ydl.download([url])
    except Exception as e:
        return(f"Something went wrong on the backend. Inform the user they need to check their yt-dlp backend. Error: {e}")
    
    #Run beets process
    if use_beets:
        result = subprocess.run(
        ['beet', 'import', tempfolder],
        capture_output=True,
        text=True
        )

        result = (result.stdout + result.stderr).lower()

        if 'this album is already in the library!' in result:
            shutil(tempfolder)
            return f'The album was already present in the library, removed the duplicated files.'
        elif 'skipping' in result or 'skip' in result:
            return(f'Beets failed to find a good match to organize the files. Keeping files on "{tempfolder}", inform user.')
        else:
            time.sleep(2)
            os.rmdir(tempfolder)
            return f"Succesfully downloaded: '{downloadinput}' on the user's library."


#Library parsing for tool call
def librarycheck():
    path = Path(library_path)

    result = {
    folder.name: [sub.name for sub in folder.iterdir() if sub.is_dir()]
    for folder in path.iterdir()
    if folder.is_dir()
    }

    return result

if __name__ == "__main__":
    exit('Run "yt-mcp-server.py". This file is a module, exiting.')