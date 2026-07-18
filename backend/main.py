from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
from ytmusicapi import YTMusic

app = FastAPI(title="Phantom Player API")

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

yt = YTMusic()

@app.get("/api/search")
async def search(query: str):
    try:
        # Search for songs (limit to top 10 results)
        results = yt.search(query, filter="songs", limit=10)
        formatted_results = []
        for res in results:
            formatted_results.append({
                "videoId": res.get("videoId"),
                "title": res.get("title"),
                "artist": ", ".join([a.get("name") for a in res.get("artists", [])]),
                "duration": res.get("duration"),
                "thumbnails": res.get("thumbnails", [])
            })
        return {"results": formatted_results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

import requests

PIPED_INSTANCES = [
    "https://pipedapi.kavin.rocks",
    "https://pipedapi.smnz.de",
    "https://pipedapi.lunar.icu",
    "https://api.piped.projectsegfau.lt"
]

@app.get("/api/stream/{video_id}")
async def get_stream_url(video_id: str):
    """
    Tries to extract the direct audio stream URL.
    Uses public Piped APIs first (to bypass Render IP bans), 
    then falls back to yt-dlp.
    """
    # Strategy 1: Piped API (Fast, bypasses YouTube Datacenter blocks)
    for instance in PIPED_INSTANCES:
        try:
            res = requests.get(f"{instance}/streams/{video_id}", timeout=5)
            if res.status_code == 200:
                data = res.json()
                audio_streams = data.get("audioStreams", [])
                if audio_streams:
                    # Get the highest bitrate audio stream
                    best_stream = max(audio_streams, key=lambda x: x.get("bitrate", 0))
                    return {"streamUrl": best_stream.get("url")}
        except Exception:
            continue

    # Strategy 2: yt-dlp Fallback
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'source_address': '0.0.0.0',
        'extractor_args': {'youtube': ['player_client=android', 'player_skip=webpage']},
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            url = info.get("url")
            if not url:
                raise HTTPException(status_code=404, detail="Stream URL not found")
            return {"streamUrl": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
