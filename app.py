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
    if not video_id:
        return "Missing video ID", 400

    url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio[ext=mp3]/bestaudio',
        'cookiefile': 'cookies.txt',  # Only use this if needed
        'quiet': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            stream_url = info.get('url')
            ext = info.get('ext')
            content_type = {
                'm4a': 'audio/mp4',
                'mp3': 'audio/mpeg',
                'webm': 'audio/webm'
            }.get(ext, 'audio/mp4')

    except Exception as e:
        return f"yt-dlp error: {str(e)}", 500

    if not stream_url:
        return "Unable to get stream URL", 500

    def generate():
        with requests.get(stream_url, stream=True) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=4096):
                if chunk:
                    yield chunk

    return Response(generate(), content_type=content_type)
    
if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)