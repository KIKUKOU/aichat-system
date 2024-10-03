#!/usr/bin/env python3
"""
The discord bot.
"""
# TODO: Modularize functions related to discord bot.  # noqa: FIX002
# ISSUE-008

from __future__ import annotations

import asyncio
import copy
import datetime
import os
import random
import time
from typing import Any

import discord  # pip install discord.py[voice]
import ffmpeg  # pip install ffmpeg-python
import utilities.log_utilities as log_util
import utilities.sound_utilities as sound_util
import utilities.text_utilities as text_util
from discord.ext import commands  # pip install discord.py[voice]
from llm.gemini_wrapper import GeminiWrapper
from llm.openai_wrapper import OpenAIWrapper
from ragtools.google_search import GoogleSearch
from ragtools.open_weather_map import OpenWeatherMap
from systemlogger import discord_logger
from tts.voicevox_wrapper import VoicevoxWrapper

# Common Config
SOUND_DEBUG = False
SYSTEM_LOG = True

# Discord Config
DISCORD_API_KEY = os.getenv('DISCORD_API_KEY')
TARGET_TEXT_CHANNEL = 'bot操作用（ミュート推奨）'  # noqa: RUF001
TARGET_VOICE_CHANNEL = '雑談ボイチャ'
COMMAND_PREFIX = '*'

# LLM Config
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')
LLM_CONFIG = {}
LLM_CONFIG['use_llm'] = 'openai'
LLM_CONFIG['use_model'] = 'gpt-4o-mini'

# TTS Config
TTS_HOST_IP = '192.168.100.211'
TTS_PORT = '50021'
TTS_CONFIG = {}
TTS_CONFIG['use_tts'] = 'voicevox'
TTS_CONFIG['speaker_ID'] = 46  # Sayo
TTS_CONFIG['speedScale'] = 1.2
TTS_CONFIG['volumeScale'] = 0.4

# FFmpeg Config
FADE_LEN = 0.1

# Character Config Value
USE_PROMPT_LOG = True
USE_FILLER = False
PROMPT_LOG_NAME = './log_files/prompt/prompt_log.csv'
CHARACTER_PROMPT_NAME = './prompt_files/character/nojyaloli.csv'
SYSTEM_PROMPT_NAME = './prompt_files/system/voicechat.csv'
TOOLS_CHOICE_PROMPT_NAME = './prompt_files/system/tools_choice.csv'
CHECH_WEATHER_PROMPT_NAME = './prompt_files/system/check_weather.csv'
WEB_SEARCH_PROMPT_NAME = './prompt_files/system/search_keywords.csv'

filler_words = ['あー', 'ふむ', 'ほう', 'なるほど', 'うむ']
FILLER_DIR = './sound_files/filler/'

# Grobal Value

# other
WEATHER_API_KEY = os.getenv('OPEN_WEATHER_MAP_API_KEY')
GCP_API_KEY = os.getenv('GOOGLE_CUSTOM_SEARCH_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CUSTOM_SEARCH_CSE_ID')


def get_llm_client() -> Any:  # noqa: ANN401
    # NOTE: Any is llm client openai, gemini and so on.
    """
    get llm client.

    Returns:
        Any: llm client openai, gemini and so on.
    """
    if LLM_CONFIG['use_llm'] == 'openai':
        llm_client = OpenAIWrapper(OPENAI_API_KEY, prompt_log_name=PROMPT_LOG_NAME)
    elif LLM_CONFIG['use_llm'] == 'gemini':
        llm_client = GeminiWrapper(GEMINI_API_KEY, prompt_log_name=PROMPT_LOG_NAME)

    return llm_client


def get_tts_client() -> Any:  # noqa: ANN401
    # NOTE: Any is tts client voicevox, google-tts and so on.
    """
    get llm client.

    Returns:
        Any: tts client voicevox, google-tts and so on.
    """
    if TTS_CONFIG['use_tts'] == 'voicevox':
        tts_address = f'{TTS_HOST_IP}:{TTS_PORT}'
        tts_client = VoicevoxWrapper(tts_address)

    return tts_client


if __name__ == '__main__':
    # Discord bot permission settings
    intents = discord.Intents.default()
    intents.message_content = True  # permission to retrieve message content
    intents.voice_states = True
    discord_client = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

    llm_client = get_llm_client()
    tts_client = get_tts_client()

    log_file_name = log_util.open_log_file()

    @discord_client.command()
    async def join(ctx: commands.Context) -> None:
        """
        Join the voice channel of the user who invoked the command.

        Args:
            ctx (commands.Context): The context of the command invocation.
        """
        is_target_text_channel = ctx.channel.name == TARGET_TEXT_CHANNEL
        is_user_in_voice_channel = ctx.message.author.voice is not None
        if is_target_text_channel:
            if is_user_in_voice_channel:
                await ctx.message.author.voice.channel.connect()
                send_text = '接続したのじゃ。 Powered by VOICEVOX 小夜'
                await send_message(ctx.message.channel, send_text)
            else:
                send_text = 'お主はボイスチャンネルに入っておらぬぞ。'
                await send_message(ctx.message.channel, send_text)

    @discord_client.command()
    async def bye(ctx: commands.Context) -> None:
        """
        Disconnect the bot from the voice channel.

        Args:
            ctx (commands.Context): The context of the command invocation.
        """
        is_target_text_channel = ctx.channel.name == TARGET_TEXT_CHANNEL
        is_bot_in_voice_channel = ctx.message.guild.voice_client is not None
        if is_target_text_channel:
            if is_bot_in_voice_channel:
                await ctx.message.guild.voice_client.disconnect()
                send_text = 'さらばじゃ。'
                await send_message(ctx.message.channel, send_text)
            else:
                send_text = 'わしはボイスチャンネルに入っておらぬぞ。'
                await send_message(ctx.message.channel, send_text)

    @discord_client.command()
    async def weather(ctx: commands.Context, city: str, time: str) -> None:
        """
        Tell weather.

        Args:
            ctx (commands.Context): The context of the command invocation.
            city (str): weather area.
            time (int): weather time.
        """
        weather_client = OpenWeatherMap(WEATHER_API_KEY)
        weather_data = weather_client.get_response({'city': city, 'time': int(time)})
        forecast_time = datetime.datetime.fromtimestamp(weather_data['dt'])  # noqa: DTZ006
        send_text = ''
        send_text += f'地点: {city}\n'
        send_text += f'日時: {forecast_time}\n'
        send_text += f"天気: {weather_data['weather'][0]['description']}\n"
        send_text += f"気温: {weather_data['main']['temp']}°C\n"
        send_text += f"湿度: {weather_data['main']['humidity']}%"
        await send_message(ctx.message.channel, send_text)

    @discord_client.listen()
    async def on_ready() -> None:
        """
        Event handler for when the bot is ready and connected to Discord.
        Sends a greeting message to the target text channel.
        """
        discord_logger.on_ready(discord_client)
        for channel in discord_client.get_all_channels():
            if channel.name == TARGET_TEXT_CHANNEL:
                greeting = 'お疲れ様なのじゃ。'
                await send_message(channel, greeting)

        discord_logger.standby()

    @discord_client.event
    async def on_message(message: discord.Message) -> None:
        """
        Event handler for incoming messages. Processes commands and generates AI responses.

        Args:
            message (discord.Message): The received message object.
        """
        is_human = not message.author.bot
        is_target_text_channel = message.channel.name == TARGET_TEXT_CHANNEL
        is_mentioned = discord_client.user in message.mentions  # noqa: F841
        # NOTE: The value will be used in a future.
        is_command = message.content[0] == COMMAND_PREFIX

        if is_human and is_command and is_target_text_channel:
            await discord_client.process_commands(message)
            return

        if is_human and is_target_text_channel:
            question = message.content
            discord_logger.mentioned(message, question)
            use_tools = await tell_tools_choice(question)
            if use_tools[0] == "'":
                use_tools = use_tools[1:-1]

            if use_tools == '天気予報':
                weather = await tell_weather(question)
                question = str(f'{weather}/n') + question
            elif use_tools == 'ネット検索':
                search_result = await web_search(question, 3)
                question = str(f'{search_result}/n') + question

            reply_text = await aichat(message, question)
            await reply_massage(message, reply_text)
            discord_logger.standby()
            return

    async def send_message(channel: discord.TextChannel, send_text: str) -> None:
        """
        Send a message to a specified Discord channel.

        Args:
            channel (discord.TextChannel): The channel to send the message to.
            send_text (str): The text content of the message to send.
        """
        await channel.send(send_text)
        discord_logger.send_message(channel, send_text)

    async def reply_massage(message: discord.Message, reply_text: str) -> None:
        """
        Reply to a message with the given text.

        Args:
            message (discord.Message): The original message to reply to.
            reply_text (str): The text content of the reply.
        """
        reply = f'{message.author.mention} {reply_text}'
        await message.channel.send(reply)
        discord_logger.reply_massage(message, reply_text)

    async def tell_tools_choice(input_text: str) -> str:
        """
        Generate an AI response to the input text, optionally with voice output.

        Args:
            input_text (str): The input text to generate a response for.

        Returns:
            str: The generated response text.
        """
        llm_client = get_llm_client()
        llm_config = copy.deepcopy(LLM_CONFIG)

        prompt = llm_client.load_prompt(TOOLS_CHOICE_PROMPT_NAME)
        prompt = llm_client.make_prompt(prompt, 'user', input_text)
        response = llm_client.get_response(prompt, llm_config)
        return llm_client.read_text(response)

    async def tell_weather(input_text: str) -> str:
        """
        Tell weather by AI and open weather map.

        Args:
            input_text (str): The input text to generate a response for.

        Returns:
            str: The generated response text.
        """
        llm_client = get_llm_client()
        llm_config = copy.deepcopy(LLM_CONFIG)

        weather_client = OpenWeatherMap(WEATHER_API_KEY)

        prompt = llm_client.load_prompt(CHECH_WEATHER_PROMPT_NAME)
        prompt = llm_client.make_prompt(prompt, 'user', input_text)
        llm_response = llm_client.get_response(prompt, llm_config)
        weather_keywords = llm_client.read_text(llm_response)
        if weather_keywords[0] == "'":
            weather_keywords = weather_keywords[1:-1]

        weather_keywords = weather_keywords.split(',')
        weather_words = {'city': weather_keywords[0:2]}
        weather_words['time'] = 0
        # TODO: 時刻変化に対応する。技術が足りないのでそのうち修正する。  # noqa: FIX002
        # ISSUE-008
        data = weather_client.get_response(weather_words)
        return weather_client.convert_weather_data_by_5days(data)

    async def web_search(
        input_text: str,
        num_of_items: int = 3,
    ) -> str:
        """
        .

        Args:
            input_text (str): The input text to generate a response for.
            num_of_items(int): num of use articles. Default is 3.

        Returns:
            str: The generated response text.
        """
        llm_client = get_llm_client()
        llm_config = copy.deepcopy(LLM_CONFIG)

        search_client = GoogleSearch(GCP_API_KEY, GOOGLE_CSE_ID)

        prompt = llm_client.load_prompt(WEB_SEARCH_PROMPT_NAME)
        prompt = llm_client.make_prompt(prompt, 'user', input_text)
        llm_response = llm_client.get_response(prompt, llm_config)
        search_keywords = llm_client.read_text(llm_response)
        # TODO: 時刻変化に対応する。技術が足りないのでそのうち修正する。  # noqa: FIX002
        # ISSUE-008
        data = search_client.get_response(search_keywords, num_of_items)
        return search_client.convert_search_result(data)

    async def aichat(message: discord.Message, input_text: str) -> str:  # noqa: C901, PLR0912, PLR0915
        # TODO: Declare each client when it is used within a function.  # noqa: FIX002
        # ISSUE-006
        # TODO: Refactor this function. Too long and complex.  # noqa: FIX002
        # ISSUE-007
        """
        Generate an AI response to the input text, optionally with voice output.

        Args:
            message (discord.Message): The received message object.
            input_text (str): The input text to generate a response for.
            llm_client (Any): The language model client (OpenAI or Gemini).
            tts_client (Any): The text-to-speech client.

        Returns:
            str: The generated response text.
        """
        llm_client = get_llm_client()
        tts_client = get_tts_client()
        llm_config, voice_config = prepare_configs(message)
        sound_controller, talk_counter = initialize_sound_controller(voice_config)

        discord_logger.speach_generate_start(
            llm_config['use_llm'],
            llm_config['model_name'],
            voice_config['speaker_ID'],
            tts_client.speakers_name_dict[voice_config['speaker_ID']],
            USE_PROMPT_LOG,
        )

        time_start = time.perf_counter()

        if llm_config['streaming'] and USE_FILLER:
            filler_num = random.randint(0, len(filler_words))  # noqa: S311
            # NOTE: Use random module because do not need secure here.
            if filler_num != 0:
                speach_start_time = await first_talk_prosess(time_start)

                text = filler_words[filler_num - 1]
                filler_file_name = f'{FILLER_DIR}{text}.wav'

                sound_controller.append_thread(filler_file_name)
                sound_controller.thread_control()
                talk_counter += 1

        response, prompt = generate_llm_response(llm_client, input_text, llm_config)

        if not llm_config['streaming']:
            generated_raw_text = llm_client.read_text(response)
            generation_time = time.perf_counter() - time_start
            discord_logger.generate_finish(generation_time)
        else:
            word_marks = text_util.WordMarks()
            generated_raw_text = ''
            text_buffer = ''
            is_make_voice = False
            for chunk in response:
                txt = llm_client.read_text(chunk)
                if txt is not None:
                    generated_raw_text = generated_raw_text + txt
                    for letter in txt:
                        is_sp, is_p, is_e, is_q, is_n = word_marks.check_letter(letter)
                        if not is_sp and is_make_voice and len(text_buffer) > 0:
                            if talk_counter == 0:
                                speach_start_time = await first_talk_prosess(time_start)

                            sound_controller = await play_voice_process(
                                message,
                                sound_controller,
                                text_buffer,
                                voice_config,
                            )
                            text_buffer = ''
                            is_make_voice = False
                            talk_counter += 1
                            await asyncio.sleep(0.1)

                        if not is_n:
                            text_buffer = text_buffer + letter

                        if is_sp:
                            is_make_voice = True

            if talk_counter == 0:
                speach_start_time = await first_talk_prosess(time_start)

            sound_controller = await play_voice_process(message, sound_controller, text_buffer, voice_config)
            while not sound_controller.is_finish_all_thread():
                await asyncio.sleep(0.1)
                sound_controller.thread_control()

            speach_finish_time = time.perf_counter() - time_start
            discord_logger.speach_finish(speach_start_time, speach_finish_time)

        finalize_response(llm_client, generated_raw_text)
        return generated_raw_text

    def prepare_configs(message: discord.Message) -> tuple[dict, dict]:
        """Prepare LLM and voice configurations."""
        llm_config = copy.deepcopy(LLM_CONFIG)
        voice_config = copy.deepcopy(TTS_CONFIG)

        voice_client = message.guild.voice_client
        if voice_config['speaker_ID'] == -1 or voice_client is None:
            llm_config['streaming'] = False
            voice_config['speaker_ID'] = -1
        else:
            llm_config['streaming'] = True
            voice_config['speaker'] = voice_config['speaker_ID']

        llm_config['model_name'] = llm_config['use_model']

        return llm_config, voice_config

    def initialize_sound_controller(voice_config: dict) -> tuple[sound_util.SoundControler, int]:
        """Initialize sound controller and talk counter."""
        if voice_config['speaker_ID'] != -1 or SOUND_DEBUG:
            return sound_util.SoundControler(), 0
        return None, 0

    def generate_llm_response(llm_client: Any, input_text: str, llm_config: dict) -> tuple[Any, Any]:  # noqa: ANN401
        # NOTE: Any is llm client openai, gemini and so on.
        """Generate LLM response."""
        system_prompt = llm_client.load_prompt(SYSTEM_PROMPT_NAME)
        character_prompt = llm_client.load_prompt(CHARACTER_PROMPT_NAME)

        if not USE_PROMPT_LOG:
            prompt = llm_client.add_prompt(system_prompt, character_prompt)
            response = llm_client.get_response(prompt, llm_config)
        else:
            add_prompt = llm_client.add_prompt(system_prompt, character_prompt)
            response, prompt = llm_client.get_chat_response(input_text, llm_config, add_prompt)

        discord_logger.prompt(prompt)
        return response, prompt

    async def first_talk_prosess(time_start: float) -> float:
        """
        Process the first talk event and log the speech start time.

        Args:
            time_start (float): The start time of the entire process.

        Returns:
            float: The speech start time.
        """
        speach_start_time = time.perf_counter() - time_start
        discord_logger.first_speach(speach_start_time)
        return speach_start_time

    async def play_voice_process(
        message: discord.Message,
        sound_controller: sound_util.SoundController,
        text_buffer: str,
        voice_config: dict[str, Any],
    ) -> sound_util.SoundController:
        """
        Generate and play voice for the given text buffer.

        Args:
            message (discord.Message): The received message object.
            sound_controller (sound_util.SoundControler): The sound controller object.
            text_buffer (str): The text to convert to speech.
            voice_config (Dict[str, Any]): Configuration for the voice generation.

        Returns:
            sound_util.SoundControler: The updated sound controller.
        """
        discord_logger.output_voice(text_buffer)
        audio_query = tts_client.generate_audio_query(text_buffer, voice_config)
        voice_data = tts_client.generate_voice(audio_query, voice_config)
        file_name = sound_util.generate_temp_wav(voice_data)
        # play voice
        # NOTE: Play audio while generating text with GPT and generating voice with VOICEVOX.
        #       For that purpose, we implemented parallel processing using threading.
        if SOUND_DEBUG:
            sound_controller.append_thread(sound_util.play_wav, (file_name,))
        else:
            sound_controller.append_thread(
                play_sound,
                (
                    message,
                    file_name,
                ),
            )

        sound_controller.thread_control()
        return sound_controller

    def play_sound(message: discord.Message, file_name: str) -> None:
        """
        Play a sound file through the Discord voice client.

        Args:
            message (discord.Message): The received message object.
            file_name (str): The path to the sound file to play.
        """
        voice_client = message.guild.voice_client
        video_info = ffmpeg.probe(file_name)
        dur = float(video_info['format']['duration'])
        opt = f'"afade=t=in:st=0:d={FADE_LEN},afade=t=out:st={dur-FADE_LEN}:d={FADE_LEN}"'
        ffmpeg_options = {
            'options': f'-vn -af {opt}',
        }
        voice = discord.FFmpegPCMAudio(file_name, **ffmpeg_options)

        voice_client.play(voice)
        while voice_client.is_playing():
            time.sleep(0.1)

        voice_client.stop()

    def finalize_response(llm_client: Any, generated_raw_text: str) -> None:  # noqa: ANN401
        # NOTE: Any is llm client openai, gemini and so on.
        """Finalize response processing."""
        discord_logger.speech_generate_finish(generated_raw_text)
        llm_client.save_assistant_response(generated_raw_text)

    discord_client.run(DISCORD_API_KEY)
