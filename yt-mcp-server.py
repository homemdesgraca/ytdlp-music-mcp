from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP, Context
from starlette.middleware.cors import CORSMiddleware
from pathlib import Path
import music_manager
import asyncio
import uvicorn

#Gets the script's absolute path and ENV values
load_dotenv()
script_path = Path(__file__).parent.absolute()

#Setting some default values
job_status = {}
is_downloading = False

mcp = FastMCP('YoutubeMCP-Test', json_response=True, host='0.0.0.0')

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
def jobstatus(job_id: str) -> str:
    """
    Use this tool to get the status of an another tool call.
    Args:
        job_id: The job_id of an tool call.
    """

    return job_status.get(job_id, 'Unknown job id.')
    
@mcp.tool()
async def wait(time: int, job_id: str) -> str:
    """
    Tool useful to wait for another tool call to finish.
    Args:
        time: Integer in seconds.
        job_id: Id of the job that you're waiting to finish. Max of 60 seconds.
    """

    time = min(time, 60) #60 is a magic number, but it prevents the LLM from waiting more than a minute at once.

    await asyncio.sleep(time)
    return (f'{time} seconds elapsed. Job {job_id} is {job_status.get(job_id, 'Unknown job id.')}')

@mcp.tool()
def youtubesearch(searchinput: str, nresults: int, isAlbum: bool) -> dict:
    """
    Always use this tool to get IDs before downloading.
    When using this for downloads, prefer searching and, right after getting the id, download.
    Search Youtube Music for an album (or an artist for searching all their albums/songs) and returns a dictionary with the top 5 results of the search, along with the name, artist, year and respective IDs of the projects.

    Args:
        searchinput: The name of an album/songs AND/OR artist (e.g. "Ninajirachi" returns all albums/songs related to the artist "Ninajirachi"; "Imaginal Disk" returns the album "Imaginal Disk" by "Magdalena Bay")
        nresults: Amount of results.
        isAlbum: If the project is an album or not.
    """

    search = music_manager.search_album(searchinput, nresults, isAlbum)
    return search

@mcp.tool()
async def youtubedownload(input: str, ctx: Context) -> str:
    """
    Downloads an album using it's album id or direct link to the user's music library.
    These can take a while, use the check operations tool to see if something is running.
    Perform a download right after getting the id from searching.
    Only return to the user after checking the downloads.

    Args:
        input: Use an album id for albums or just input the direct link sent by the user.
    """
    
    global is_downloading #Not sure about this yet, multiple downloads at the same time seems unstable.

    #Prevents more than one download at once.
    if is_downloading == True:
        return "A download is already running, wait for it to finish."
    
    is_downloading = True
    job_id = ctx.request_id
    job_status[job_id] = "running"
    
    async def run():
        global is_downloading
        try:
            result = await asyncio.to_thread(music_manager.download_album, input)
            job_status[job_id] = f"Done: {result}"
        except Exception as e:
            job_status[job_id] = f"Error: {e}"
        finally:
            is_downloading = False
    
    asyncio.create_task(run())
    return f"Download started with job_id = {job_id}. Use the jobstatus tool to check progress."

@mcp.tool()
def getlibraryalbums():

    """
    Returns a dictionary with the artist names and their respective albums present in the library.
    """

    return music_manager.librarycheck()

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)