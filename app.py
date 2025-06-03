from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from ytmusicapi import YTMusic
import yt_dlp
import requests

app = Flask(__name__)
CORS(app)

ytmusic = YTMusic()

@app.route('/')
def home():
    return jsonify({"message": "YTMusic API is running on backend"})

# ============================================== Get search results
@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Missing 'q' in parameter"}), 400
    
    results = ytmusic.search(query,filter='songs')
    return jsonify(results)

# ============================================== Get youtube video link from the video id
# @app.route('/audio_url')
# def get_audio_url():
#     video_id = request.args.get('id')
#     url = f"https://www.youtube.com/watch?v={video_id}"

#     ydl_opts = {
#         'format': 'bestaudio/best',
#         'quiet': True,
#         'noplaylist': True,
#         'cookiefile': 'cookies.txt',  # Use your cookies.txt file here
#     }

#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         info = ydl.extract_info(url, download=False)
#         return jsonify({"audio_url": info['url']})
@app.route('/stream')
def stream_audio():
    video_id = request.args.get('id')
    url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        'format': 'bestaudio[ext=webm]/bestaudio/best',
        'cookies_from_browser': ('brave',),
        'quiet': True,
        'noplaylist': True,
        'cookiefile': 'cookies.txt',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        stream_url = info['url']

    # Now proxy the stream from YouTube
    def generate():
        with requests.get(stream_url, stream=True) as r:
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    yield chunk

    return Response(generate(), content_type='audio/webm')
    
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)