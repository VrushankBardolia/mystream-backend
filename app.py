from flask import Flask, request, jsonify
from flask_cors import CORS
from ytmusicapi import YTMusic
from yt_dlp import YoutubeDL
import browser_cookie3

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
@app.route('/audio_url')
# def get_audio_url():
#     video_id = request.args.get('id')
#     if not video_id:
#         return jsonify({"error":"Missing 'id' in parameter"}), 400
    
#     url = f"https://www.youtube.com/watch?v={video_id}"
#     ydl_opts = {
#         'format': 'bestaudio/best',
#         'quiet': True,
#         'skip_download': True,
#         'forceurl': True,
#     }

#     try:
#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             info_dict = ydl.extract_info(url, download=False)
#             audio_url = info_dict['url']
#             return jsonify({'audio_url': audio_url})
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
    
def get_audio_url(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'cookiefile': None,  # Not using a manual file
        'cookiesfrombrowser': ('chrome',),  # Use Chrome cookies
    }

    # Provide browser cookies (automatically)
    cj = browser_cookie3.chrome()

    with YoutubeDL({**ydl_opts, 'cookiefile': cj}) as ydl:
        info = ydl.extract_info(url, download=False)
        return info['url']

if __name__ == "__main__":
    from os import environ
    port = int(environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)