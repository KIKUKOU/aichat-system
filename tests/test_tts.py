if __name__ == '__main__':
    SPEAKER_ID = 1
    TEXT = 'いろはにほへとちりぬるを、わかよたれそつねならむ。ういのおくやまきょうこえて、あさきゆめみしえひもせす。'

    TTS_client = GoogleTTSWrapper(None)
    voice_config = {}
    voice_config['speaker'] = SPEAKER_ID
    audio_query = TTS_client.generate_audio_query(TEXT, voice_config)
    voice_data = TTS_client.generate_voice(audio_query, voice_config)


if __name__ == '__main__':
    voice_host_port = 50021
    voice_host_ip = '127.0.0.1'
    speaker_ID = 46
    text = 'いろはにほへとちりぬるを、わかよたれそつねならむ。ういのおくやまきょうこえて、あさきゆめみしえひもせす。'

    voice_host_address = f'{voice_host_ip}:{voice_host_port}'
    TTS_client = VoicevoxWrapper(voice_host_address)
    voice_config = {}
    voice_config['speaker'] = speaker_ID
    voice_config['speed'] = 1.2
    voice_config['volume'] = 0.4
    audio_query = TTS_client.generate_audio_query(text, voice_config)
    voice_data = TTS_client.generate_voice(audio_query, voice_config)
