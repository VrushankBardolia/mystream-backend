from flask import Flask, request, jsonify
from flask_cors import CORS
from ytmusicapi import YTMusic
import yt_dlp
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
def get_audio_url():
    video_id = request.args.get('id')
    url = f"https://www.youtube.com/watch?v={video_id}"

    # Get cookies from Brave browser
    cj = browser_cookie3.brave()

    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'noplaylist': True,
        'cookiefile': None,
        'cookiejar': cj  # Pass the cookie jar directly
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info['url']
    

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)