#!/usr/bin/env python3
"""
The sound test.
"""

import time

import utilities.sound_utilities as sound_util
import utilities.text_utilities as text_util
from tts.google_tts_wrapper import GoogleTTSWrapper
from tts.voicevox_wrapper import VoicevoxWrapper

if __name__ == '__main__':
    voice_host_port = 50021
    voice_host_ip = '192.168.100.211'
    text = 'いろはにほへとちりぬるを！！？わかよたれそつねならむ。\n'  # noqa: RUF001
    text += 'ういのおくやまきょうこえて！\nあさきゆめみしえひもせす。'  # noqa: RUF001
    # NOTE: Japanese sentence, so use Full-width letter.

    is_exit = False
    while not is_exit:
        use_tts = input('\n"voicevox"と"google-tts"のどちらを使用しますか？（終了時は"exit"と入力）\n\n')  # noqa: RUF001
        # NOTE: Japanese sentence, so use Full-width letter.
        if use_tts == 'exit':
            is_exit = True
            break

        init_config = {}
        if use_tts == 'voicevox':
            voice_host_address = f'{voice_host_ip}:{voice_host_port}'
            TTS_client = VoicevoxWrapper(voice_host_address)
            break
        elif use_tts == 'google-tts':
            TTS_client = GoogleTTSWrapper(None)
            break

    voice_config = {}
    if use_tts == 'voicevox':
        voice_config['speaker'] = 46  # sayo
        voice_config['speed'] = 1.2
        voice_config['volume'] = 0.5
    elif use_tts == 'google-tts':
        voice_config['speaker'] = 1  # japanese female
        voice_config['speed'] = 1.2
        voice_config['volume'] = 0.5
        voice_config['language_code'] = 'ja-JP'

    input_text = input('\nどのような文章を読み上げさせますか？（サンプルの文章を使う場合は"def"と入力）\n\n\n')  # noqa: RUF001
    # NOTE: Japanese sentence, so use Full-width letter.
    if input_text != 'def':
        text = input_text

    time_s = time.perf_counter()
    word_marks = text_util.WordMarks()
    texts = word_marks.split_text_for_voice(text)
    sound_controler = sound_util.SoundControler()
    for txt in texts:
        time_g_s = time.perf_counter()
        audio_query = TTS_client.generate_audio_query(txt, voice_config)
        voice_data = TTS_client.generate_voice(audio_query, voice_config)
        time_g_e = time.perf_counter()
        print(f'{txt}')
        print(f'generate speech: {time_g_e - time_g_s} sec')
        file_name = sound_util.generate_temp_wav(voice_data)
        # play voice
        # NOTE: Play audio while generating text with GPT and generating voice with VOICEVOX.
        #       For that purpose, we implemented parallel processing using threading.
        sound_controler.append_thread(sound_util.play_wav, file_name)
        sound_controler.thread_control()

    while not sound_controler.is_finish_all_thread():
        time.sleep(0.1)
        sound_controler.thread_control()

    time_e = time.perf_counter()
    print(f'speech finish: {time_e - time_s} sec')
