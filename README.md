# musicGenerationPython
### Purpose: ###
musicGenerationPython allows you to find ringtone on spotify, then give that song to `tensorflow-magenta` for it to try to continue your ringtone

### Usage: ###
```
python3 main.py name\ song\ from\ spotify and\ another\ one
```

Result `.mid` file is in `outputMusicGeneration/` directory.

`tensorflow-magenta` works best with classical music, because of conversion to `.mid`, I highly do not recommend using any music with human speech in it

### How it works: ###
Algorithm works that way:
1. Searches for your query song on spotify(Because spotify has better search than youtube does)
2. Searches that song on youtube
3. Downloads `.mp3` from youtube (Download speeds are very slow because of I guess google somehow blocks network traffic from `youtube_dl`)
4. Converts `.mp3` to `.wav` --- higher quality == better conversion to `.mid`
5. Converts `.wav` to `.mid` (`tensorflow-magenta` works only with `.mid`)
6. Loads pretrained model for `magenta`
7. Continues all the `.mid` files and saves them to `outputMusicGeneration/`
8. Deletes temporary files

### Requirements: ###
1. Make https://github.com/kichiki/WaoN as `waon` in the same folder as `main.py` file
2. `spotipy`
3. `youtude-search`
4. `youtube-dl`
5. `magenta`

### TODO: ###
1. Use jupyter notebook instead of `.py` file
2. Improve codestyle a lot --- had no time to write a decent code
3. Get better pretrained model --- had no time to search for the good one, got the simplest possible `basic_rnn.mag`
4. Change `youtube-dl` to something better to download videos faster than `60kb/s`
