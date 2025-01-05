from flask import Flask, request, jsonify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Spotify API credentials from environment variables
CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')

# Initialize Spotify Client Credentials Manager
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

@app.route('/get_tracks', methods=['POST'])
def get_tracks():
    """
    Endpoint to retrieve all track names from a specified Spotify playlist.
    Expects a JSON payload with 'playlist_id'.
    """
    data = request.get_json()

    if not data or 'playlist_id' not in data:
        return jsonify({'error': 'Missing playlist_id in request body.'}), 400

    playlist_id = data['playlist_id']

    try:
        # Retrieve playlist details
        playlist = sp.playlist(playlist_id)
        tracks = playlist['tracks']
        track_names = []

        # Fetch all tracks, handling pagination
        while True:
            for item in tracks['items']:
                track = item['track']
                if track:  # Ensure track is not None
                    track_names.append(track['name'])

            if tracks['next']:
                tracks = sp.next(tracks)
            else:
                break

        return jsonify({'tracks': track_names}), 200

    except spotipy.exceptions.SpotifyException as e:
        # Handle Spotify API errors
        return jsonify({'error': f'Spotify API Error: {e.msg}'}), e.http_status
    except Exception as e:
        # Handle other unexpected errors
        return jsonify({'error': f'Unexpected Error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
