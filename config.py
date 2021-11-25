SPOTIFY_CLIENT_ID = "ce09b5342d4f4540a5586f7ae192a467"
SPOTIFY_CLIENT_SECRET = "c1fc4e689873473d910e8bf62d75fad9"

TEMP_DIR_MP3 = 'musicGenerationTemporaryMP3Files/'
TEMP_DIR_WAV = 'musicGenerationTemporaryWAVFiles/'
TEMP_DIR_MOD = 'musicGenerationTemporaryMODFiles/'
INP_DIR_MID = 'musicGenerationTemporaryMIDFiles/'
DIR_RES = 'outputMusicGeneration/'

YT_SEARCH_ATTEMPTS_MAX = 3
YDL_OPTS = {
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '190',
    }],
}

