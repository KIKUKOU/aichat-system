#!/usr/bin/env python3
"""
The discord bot.
"""
# TODO: Modularize functions related to discord bot.  # noqa: FIX002
# ISSUE-008

from __future__ import annotations

import asyncio
import copy
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
LLM_CONFIG['use_model'] = 'gpt-4o'

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

filler_words = ['あー', 'ふむ', 'ほう', 'なるほど', 'うむ']
FILLER_DIR = './sound_files/filler/'

# Grobal Value

# other

if __name__ == '__main__':
    # Discord bot permission settings
    intents = discord.Intents.default()
    intents.message_content = True  # permission to retrieve message content
    intents.voice_states = True
    discord_client = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)

    if LLM_CONFIG['use_llm'] == 'openai':
        llm_client = OpenAIWrapper(OPENAI_API_KEY, prompt_log_name=PROMPT_LOG_NAME)
    elif LLM_CONFIG['use_llm'] == 'gemini':
        llm_client = GeminiWrapper(GEMINI_API_KEY, prompt_log_name=PROMPT_LOG_NAME)

    if TTS_CONFIG['use_tts'] == 'voicevox':
        tts_address = f'{TTS_HOST_IP}:{TTS_PORT}'
        tts_client = VoicevoxWrapper(tts_address)

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
            reply_text = await aichat(message, question, llm_client, tts_client)
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

    async def aichat(message: discord.Message, input_text: str, llm_client: Any, tts_client: Any) -> str:  # noqa: ANN401, C901, PLR0912, PLR0915
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
        voice_client = message.guild.voice_client
        llm_config = copy.deepcopy(LLM_CONFIG)
        voice_config = copy.deepcopy(TTS_CONFIG)
        if voice_config['speaker_ID'] == -1 or voice_client is None:
            llm_config['streaming'] = False
            llm_config['model_name'] = llm_config['use_model']
            voice_config['speaker_ID'] = -1
        else:
            llm_config['streaming'] = True
            llm_config['model_name'] = llm_config['use_model']
            voice_config['speaker'] = voice_config['speaker_ID']
            sound_controler = sound_util.SoundControler()
            talk_counter = 0

        if SOUND_DEBUG:
            llm_config['streaming'] = True
            llm_config['model_name'] = llm_config['use_model']
            voice_config['speaker_ID'] = TTS_CONFIG['speaker_ID']
            voice_config['speaker'] = voice_config['speaker_ID']
            sound_controler = sound_util.SoundControler()
            talk_counter = 0

        discord_logger.speach_generate_start(
            llm_config['use_llm'],
            llm_config['model_name'],
            voice_config['speaker_ID'],
            tts_client.speakers_name_dict[voice_config['speaker_ID']],
            USE_PROMPT_LOG,
        )

        time_start = time.perf_counter()

        system_prompt = llm_client.load_prompt(SYSTEM_PROMPT_NAME)
        character_prompt = llm_client.load_prompt(CHARACTER_PROMPT_NAME)
        if not USE_PROMPT_LOG:
            prompt = llm_client.add_prompt(system_prompt, character_prompt)
            response = llm_client.get_response(prompt, llm_config)
        else:
            add_prompt = llm_client.add_prompt(system_prompt, character_prompt)
            response, prompt = llm_client.get_chat_response(input_text, llm_config, add_prompt)

        discord_logger.prompt(prompt)
        if llm_config['streaming'] and USE_FILLER:
            filler_num = random.randint(0, len(filler_words))  # noqa: S311
            # NOTE: Use random module because do not need secure here.
            if filler_num != 0:
                speach_start_time = await first_talk_prosess(time_start)

                text = filler_words[filler_num - 1]
                filler_file_name = f'{FILLER_DIR}{text}.wav'

                sound_controler.append_thread(filler_file_name)
                sound_controler.thread_control()
                talk_counter += 1

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

                            sound_controler = await play_voice_process(
                                message,
                                sound_controler,
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

            sound_controler = await play_voice_process(message, sound_controler, text_buffer, voice_config)
            while not sound_controler.is_finish_all_thread():
                await asyncio.sleep(0.1)
                sound_controler.thread_control()

            speach_finish_time = time.perf_counter() - time_start
            discord_logger.speach_finish(speach_start_time, speach_finish_time)

        discord_logger.speach_generate_finish(generated_raw_text)
        llm_client.save_assistant_response(generated_raw_text)
        return generated_raw_text

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
        sound_controler: sound_util.SoundControler,
        text_buffer: str,
        voice_config: dict[str, Any],
    ) -> sound_util.SoundControler:
        """
        Generate and play voice for the given text buffer.

        Args:
            message (discord.Message): The received message object.
            sound_controler (sound_util.SoundControler): The sound controller object.
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
            sound_controler.append_thread(sound_util.play_wav, (file_name,))
        else:
            sound_controler.append_thread(
                play_sound,
                (
                    message,
                    file_name,
                ),
            )

        sound_controler.thread_control()
        return sound_controler

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

    discord_client.run(DISCORD_API_KEY)
