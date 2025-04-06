const express = require('express');
const SpotifyWebApi = require('spotify-web-api-node');
const cors = require('cors');

const app = express();
app.use(express.json());
app.use(cors());

// Replace with your actual Spotify API credentials
const spotifyApi = new SpotifyWebApi({
  clientId: 'YOUR_SPOTIFY_CLIENT_ID',
  clientSecret: 'YOUR_SPOTIFY_CLIENT_SECRET'
});

// Get access token on start
async function refreshToken() {
  const data = await spotifyApi.clientCredentialsGrant();
  spotifyApi.setAccessToken(data.body['access_token']);
  console.log("Spotify access token set");
}
refreshToken();

app.post('/spotify', async (req, res) => {
  const { url } = req.body;
  const playlistIdMatch = url.match(/playlist\/([a-zA-Z0-9]+)/);
  if (!playlistIdMatch) return res.status(400).json({ error: 'Invalid Spotify playlist URL' });

  const playlistId = playlistIdMatch[1];

  try {
    const tracks = [];
    let offset = 0, limit = 100;
    let total = 0;

    do {
      const data = await spotifyApi.getPlaylistTracks(playlistId, { offset, limit });
      data.body.items.forEach(item => {
        const track = item.track;
        if (track) {
          tracks.push(`${track.name} ${track.artists[0].name}`);
        }
      });
      total = data.body.total;
      offset += limit;
    } while (offset < total);

    res.json({ tracks });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: "Failed to fetch playlist" });
  }
});

const PORT = process.env.PORT || 10001;
app.listen(PORT, () => {
  console.log(`Spotify backend running on port ${PORT}`);
});
