#!/usr/bin/env python3
"""
The functions required to obtain log data, and the format of the contents to be included in the log data.
"""

from __future__ import annotations

from typing import Any

from utilities.log_utilities import Time, logger


def standby() -> None:
    """
    At event function finish.
    """
    logger('system', '==== Standby ====')
    return


def prompt(input_prompt: list[dict[str, str]]) -> None:
    """
    At make prompt.

    Args:
        input_prompt(list[dict[str, str]]): Prompt.
    """
    datetime_now = Time()
    for p in input_prompt:
        role = p['role']
        content = p['content']
        text = f'role:{role} content:{content}'
        logger('prompt', text, datetime_now)

    return


def on_ready(discord_client: Any) -> None:
    """
    At last of on_ready().

    Args:
        discord_client(str): temp.
    """  # noqa: D402
    datetime_now = Time()
    logger('system', '==== DiscordLoginSuccessfully ====', datetime_now)
    logger('system', f'own_user_ID:{discord_client.user.id}', datetime_now)
    logger('system', f'own_user_name:{discord_client.user}', datetime_now)
    return


def mentioned(message: Any, question: str) -> None:
    """
    At on_massage() in mentioned.

    Args:
        message(str): temp.
        question(str): temp.
    """
    datetime_now = Time()
    logger('system', '==== Mentioned ====', datetime_now)
    logger('system', f'message_ID:{message.id}', datetime_now)
    logger('system', f'author_ID:{message.author.id}', datetime_now, 'f')
    logger('system', f'author_name:{message.author.name}', datetime_now)
    logger('input:text', question, datetime_now)
    return


def send_message(channel: Any, send_text: str) -> None:
    """
    At message() in send message.

    Args:
        channel(str): temp.
        send_text(str): temp.
    """
    datetime_now = Time()
    logger('system', '==== SendMessage ====', datetime_now)
    logger('system', f'target_channel_ID:{channel.id}', datetime_now, 'f')
    logger('system', f'target_channel_name:{channel.name}', datetime_now)
    logger('output:text', send_text, datetime_now)
    return


def reply_massage(message: Any, reply_text: str) -> None:
    """
    At message() in reply.

    Args:
        message(str): temp.
        reply_text(str): temp.
    """
    datetime_now = Time()
    logger('system', '==== Reply ====', datetime_now)
    logger('system', f'target_message_ID:{message.id}', datetime_now)
    logger('system', f'target_user_ID:{message.author.id}', datetime_now, 'f')
    logger('system', f'target_user_name:{message.author.name}', datetime_now)
    logger('output:text', reply_text, datetime_now)


def speach_generate_start(
    llm_name: str,
    model_name: str,
    speaker_id: str | int,
    speaker_name: str,
    is_use_prompt_log: bool,  # noqa: FBT001
) -> None:
    """
    At at aichat() in start function.

    Args:
        llm_name(str): temp.
        model_name(str): temp.
        speaker_id(str | int): temp.
        speaker_name(str): temp.
        is_use_prompt_log(bool): temp.
    """
    datetime_now = Time()
    logger('system', '==== GenerateSpeach ====', datetime_now)
    logger('system', f'llm_name:{llm_name}', datetime_now)
    logger('system', f'model_name:{model_name}', datetime_now)
    logger('system', f'speaker_ID:{speaker_id}', datetime_now, 'f')
    logger('system', f'speaker_name:{speaker_name}', datetime_now)
    logger('system', f'use_log:{is_use_prompt_log}', datetime_now)


def first_speach(speach_start_time: float) -> None:
    """
    At at aichat() in start function.

    Args:
        speach_start_time(float): time of input to first speech start.
    """
    datetime_now = Time()
    logger('system', f'speach_start_time:{speach_start_time}', datetime_now)
    return


def output_voice(speach_text: str) -> None:
    """
    At at aichat() in speech.

    Args:
        speach_text(str): Speech text.
    """
    logger('output:voice', speach_text)
    return


def speach_finish(speach_start_time: float, speach_finish_time: float) -> None:
    """
    At at aichat() in all speech finish.

    Args:
        speach_start_time(float): time of input to first speech start.
        speach_finish_time(float): time of input to last speech finish.
    """
    datetime_now = Time()
    logger('system', f'speach_finish_time:{speach_finish_time}', datetime_now)
    logger('system', f'speach_time:{speach_finish_time - speach_start_time}', datetime_now)
    return


def generate_finish(generation_time: float) -> None:
    """
    At at aichat() in finish generate text when no voice.

    Args:
        generation_time(str): time of input to generate text.
    """
    datetime_now = Time()
    logger('system', f'generation_time:{generation_time}', datetime_now)
    return


def speach_generate_finish(generated_text: str) -> None:
    """
    At at aichat() in finish speech or generate finish.

    Args:
        generated_text(str): The generated text by AI.
    """
    datetime_now = Time()
    logger('system', f'text_length:{len(generated_text)}', datetime_now)
    logger('system', generated_text, datetime_now)
    return
