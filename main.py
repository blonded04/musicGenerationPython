import youtube_dl
from sys import argv

from magenta.scripts.convert_dir_to_note_sequences import convert_midi

from config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, YT_SEARCH_ATTEMPTS_MAX, YDL_OPTS, TEMP_DIR_WAV, \
    INP_DIR_MID, TEMP_DIR_MP3, DIR_RES, TEMP_DIR_MOD
from youtube_search import YoutubeSearch
from os import walk, makedirs, system, path


def download_song(url):
    with youtube_dl.YoutubeDL(YDL_OPTS) as ydl:
        ydl.download([url])


def find_songs_yt(songs):
    for track in songs:
        url = None
        for attempt in range(1, YT_SEARCH_ATTEMPTS_MAX + 1):
            try:
                results_list = YoutubeSearch(track, max_results=1).to_dict()
                url = "https://www.youtube.com{}".format(results_list[0]['url_suffix'])
                break
            except IndexError:
                if attempt != YT_SEARCH_ATTEMPTS_MAX:
                    print("No valid URLs found for {}, trying again. {} attempt(s) remaining.".format(
                        track, YT_SEARCH_ATTEMPTS_MAX - attempt))
        if url is None:
            print("No valid URLs found for {}, skipping track.".format(track))
            continue
        print("Initiating download for {}.".format(track))
        download_song(url)


def find_songs_sp(spotify_queries, songs):
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))
    print("Searching for songs on spotify...")
    for idx, query in enumerate(spotify_queries):
        result = sp.search(q=query, limit=1)
        if len(result) == 0:
            print("!No song found!")
            continue
        track = result['tracks']['items'][0]
        song_title = track['name'] + " by "
        print("[spotify] Song #" + str(idx + 1) + ' — ', end='')
        for artist in track['artists']:
            song_title += artist['name']
            if track['artists'][-1]['name'] != artist['name']:
                song_title += ', '
        print(song_title, '—', track['external_urls']['spotify'])
        songs.append(song_title)


def process_to_wav():
    import audiofile
    fnames = [tpl for tpl in walk(TEMP_DIR_MP3)][0]
    if len(fnames) == 0:
        return
    if not path.exists(fnames[0] + '../' + TEMP_DIR_WAV):
        makedirs(fnames[0] + '../' + TEMP_DIR_WAV)
    for fname_cur in fnames[2]:
        fname_old = fnames[0] + fname_cur
        fname_new = fnames[0] + '../' + TEMP_DIR_WAV + fname_cur.split('.')[0] + '.wav'
        print('Converting \".mp3\" to \".wav\"...')
        print('[audiofile] \'' + fname_old + '\' -> \'' + fname_new + '\'')
        signal, sampling_rate = audiofile.read(fname_old)
        audiofile.write(fname_new, signal, sampling_rate)


def resize_wavs():
    import wave
    from pydub import AudioSegment
    fnames = [tpl for tpl in walk(TEMP_DIR_WAV)][0]
    if len(fnames) == 0:
        return
    if not path.exists(fnames[0] + '../' + TEMP_DIR_MOD):
        makedirs(fnames[0] + '../' + TEMP_DIR_MOD)
    for fname_cur in fnames[2]:
        fname_old = fnames[0] + fname_cur
        fname_new = fnames[0] + '../' + TEMP_DIR_MOD + fname_cur.split('.')[0] + '.wav'
        with wave.open(fname_old) as mywav:
            duration_seconds = mywav.getnframes() / mywav.getframerate()
        t1 = (duration_seconds / 2 - 8) * 1000  # Works in milliseconds
        t2 = (duration_seconds / 2) * 1000
        newAudio = AudioSegment.from_wav(fname_old)
        newAudio = newAudio[t1:t2]
        newAudio.export(fname_new, format="wav")


def process_to_midi():
    fnames = [tpl for tpl in walk(TEMP_DIR_MOD)][0]
    if len(fnames) == 0:
        return
    if not path.exists(fnames[0] + '../' + INP_DIR_MID):
        makedirs(fnames[0] + '../' + INP_DIR_MID)
    for fname_cur in fnames[2]:
        fname_old = fnames[0] + fname_cur
        fname_new = fnames[0] + '../' + INP_DIR_MID + fname_cur.split('.')[0] + '.mid'
        print('Converting \".wav\" to \".mid\"...')
        print('[waon] \'' + fname_old + '\' -> \'' + fname_new + '\'')
        print('[waon] ./waon -i ' + fname_old + ' -o ' + fname_new)
        system('./waon -i ' + fname_old + ' -o ' + fname_new)  # Not safe at all
        system('sudo chmod +r ' + fname_new)  # Not safe at all


def midis_continue():
    import magenta
    import note_seq
    import tensorflow
    from note_seq.protobuf import music_pb2
    from magenta.models.melody_rnn import melody_rnn_sequence_generator
    from magenta.models.shared import sequence_generator_bundle
    from note_seq.protobuf import generator_pb2
    from note_seq.protobuf import music_pb2
    # Prepare model
    bundle = sequence_generator_bundle.read_bundle_file('content/basic_rnn.mag')
    generator_map = melody_rnn_sequence_generator.get_generator_map()
    melody_rnn = generator_map['basic_rnn'](checkpoint=None, bundle=bundle)
    melody_rnn.initialize()
    # Start processing
    fnames = [tpl for tpl in walk(INP_DIR_MID)][0]
    if len(fnames) == 0:
        return
    if not path.exists(fnames[0] + '../' + DIR_RES):
        makedirs(fnames[0] + '../' + DIR_RES)
    for fname_cur in fnames[2]:
        fname_old = fnames[0] + fname_cur
        fname_new = fnames[0] + '../' + DIR_RES + fname_cur.split('.')[0] + '.mid'
        input_sequence = convert_midi("", INP_DIR_MID, fname_old)
        # Model options. Change these to get different generated sequences!
        num_steps = 128  # change this for shorter or longer sequences
        temperature = 1.0  # the higher the temperature the more random the sequence.
        # Set the start time to begin on the next step after the last note ends.
        last_end_time = (max(n.end_time for n in input_sequence.notes)
                         if input_sequence.notes else 0)
        qpm = input_sequence.tempos[0].qpm
        seconds_per_step = 60.0 / qpm / melody_rnn.steps_per_quarter
        total_seconds = num_steps * seconds_per_step
        generator_options = generator_pb2.GeneratorOptions()
        generator_options.args['temperature'].float_value = temperature
        generate_section = generator_options.generate_sections.add(
            start_time=last_end_time + seconds_per_step,
            end_time=total_seconds)
        # Ask the model to continue the sequence.
        sequence = melody_rnn.generate(input_sequence, generator_options)
        # Save file
        note_seq.sequence_proto_to_midi_file(sequence, fname_new)
        system('sudo chmod +r ' + fname_new)  # Not safe at all


if __name__ == "__main__":
    queries = argv[1:]
    melodies = []
    find_songs_sp(queries, melodies)
    find_songs_yt(melodies)
    process_to_wav()
    resize_wavs()
    process_to_midi()
    midis_continue()
    import shutil
    shutil.rmtree(TEMP_DIR_MP3)  # Not safe at all
    shutil.rmtree(TEMP_DIR_WAV)  # Not safe at all
    shutil.rmtree(TEMP_DIR_MOD)  # Not safe at all
