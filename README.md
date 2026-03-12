# ytdlp-music-mcp: manually ripping songs is boring asf

a _very_ simple and basic MCP server built around [mcp-python-sdk](https://github.com/modelcontextprotocol/python-sdk), [ytmusicapi](https://github.com/sigma67/ytmusicapi), [beets](https://github.com/beetbox/beets), and, _obviously_, [yt-dlp](https://github.com/yt-dlp/yt-dlp).

## Features
* Provides tools to a LLM using a MCP server, allowing for: searching and downloading albums/songs off Youtube, aswell as checking your library.
* Uses [beets](https://github.com/beetbox/beets) to tag and organize your song library.
  * You **_CAN_** disable beets on your .env file, but it's very recommended not to, as the project as built around it's usage. 

* Music related tools
  * youtubesearch: searches YTMusic for albums or songs; used mainly for obtaining ids
    * Inputs: query (str), nresults (int; number of results) and isAlbum (bool)
    * Output: dict of search results with name, artist, id and year
  * youtubedownload: downloads an album or song using it's id
    * Input: id (str)
    * Output: status of job and it's job_id.
  * getlibraryalbums: looks up your local music library
    * Output: dict of user's music library with artists and their albums

* Utility tools
  * wait: _waits_ for some amount of seconds and return the status of a job_id; useful for waiting for downloads
    * Input: seconds (int) and job_id (str)
    * Outputs: status of provided job_id
  * jobstatus: checks the status of provided job_id
    * Input: job_id (str)
    * Output: status of provided job_id


## Requirements
Python (>=3.10 works fine)
mcp-python-sdk
ytmusicapi
yt-dlp

## Installation
* Install uv if you don't have it:
  ```bash
  # Mac/Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  
  # Windows
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

* Setup
  
  ```bash
  git clone https://github.com/homemdesgraca/ytdlp-music-mcp
  cd ytdlp-music-mcp
  uv sync
  cp .env.example .env        # Mac/Linux
  copy .env.example .env      # Windows
  ```

  *Edit your .env file based on the table below (or check your .env file and check the annotations):*

  | Variable | Required | Description |
  |----------|----------|-------------|
  | `LIBRARYPATH` | Required | Absolute path to your music library (e.g. `/mnt/hdd/Music`) |
  | `FIREFOX_PROFILE_PATH` | Optional | Firefox profile name, needed* for explicit songs ; Check below for more info |
  | `USE_BEETS` | Required | `True` recommended, `False` to disable beets |


* Cookies
  * This is **needed** (_sometimes not?_) for downloading explicit songs.
  * It's strongly recommended that you use Firefox for using cookies, as Chrome seems very limiting, but you can change it on "music_manager.py" (you will need to do some manual work).

  - Step 1: Open Firefox and open "about:profiles"
  - Step 2: Create a new profile and name it whatever you want (e.g. YT-MCP)
  - Step 3: Launch the profile on a new browser.
  - Step 4: Go to Youtube and log into an, _preferably_, throwaway account.
  - Step 5: Go back to the main Firefox instance and copy

