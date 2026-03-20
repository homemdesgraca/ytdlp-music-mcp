from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
from starlette.middleware.cors import CORSMiddleware
from pathlib import Path
import music_manager
import asyncio
import uvicorn
from typing import Union

#Gets the script's absolute path and ENV values
load_dotenv()
script_path = Path(__file__).parent.absolute()
port = 8000 #Port which the MCP server will run

job_status = {}
job_id = 0
download_lock = asyncio.Lock()

mcp = FastMCP('ytdlp-music-mcp', json_response=True, host='0.0.0.0')

#CORS Proxy (Optional)
app = CORSMiddleware(
    app=mcp.streamable_http_app(),
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    expose_headers=["Mcp-Session-Id"],
)

@mcp.tool()
def jobstatus(job_id: Union[str, int]) -> str:
    """
    Use this tool to check the status of another tool call.
    Args:
        job_id: The job_id of an tool call.
    """

    job_id = int(job_id)
    job_result = job_status.get(job_id, 'Unknown job id.')

    return f"The job {job_id} is {job_result}. Inform the user."

@mcp.tool()
def youtubesearch(searchinput: Union[int, str], nresults: Union[int, str] = 5, isAlbum: Union[bool, str] = True) -> dict:
    """
    Always use this tool to get IDs before downloading.
    When using this for downloads, prefer searching and, right after getting the id, download.
    Search Youtube Music for an album (or an artist for searching all their albums/songs) and returns a dictionary with the top 5 results of the search, along with the name, artist, year and respective IDs of the projects.
    If unspecified, always prefer searching for albums first.
    When you have problems finding an album, try searching with isAlbum = "false" for songs.
    
    Args:
        searchinput: The name of an album/songs AND/OR artist (e.g. "Ninajirachi" returns all albums/songs related to the artist "Ninajirachi"; "Imaginal Disk" returns the album "Imaginal Disk" by "Magdalena Bay")
        nresults: Amount of results.
        isAlbum: If "true", searches for albums. If "false", searches for individual songs. When you have problems finding an album, try searching with isAlbum = "false" for songs.
    """

    searchinput = str(searchinput)
    nresults = int(nresults)
    isAlbum = str(isAlbum).lower() == "true"
    
    search = music_manager.search_album(searchinput, nresults, isAlbum)
    return search

@mcp.tool()
async def youtubedownload(input: Union[str, int]) -> str:
    """
    Downloads an album using it's album id or direct link to the user's music library.
    Perform a download right after getting the id from searching.
    If you need to download multiple albums, check adding it to the queue.

    Args:
        input: Use an album id for albums or just input the direct link sent by the user.
    """

    global job_id

    job_id += 1
    current_job_id = job_id
    job_status[current_job_id] = {
        'input_value': str(input),
        'status': 'queue'
    }

    asyncio.create_task(process_download(current_job_id))

    return f"Download queued with job_id = {current_job_id}."

async def process_download(job_id_to_run: int):
    async with download_lock:
        entry = job_status[job_id_to_run]
        entry['status'] = 'running'
        try:
            result = await asyncio.to_thread(
                music_manager.download_album,
                entry['input_value']
            )
            entry['status'] = f"done: {result}"
        except Exception as e:
            entry['status'] = f"error: {e}"

@mcp.tool()
def getlibraryalbums():

    """
    Returns a dictionary with the artist names and their respective albums present in the library.
    """

    return music_manager.librarycheck()

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=port)