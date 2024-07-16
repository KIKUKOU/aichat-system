#!/usr/bin/env python3
"""
The class wrap openAI api.
"""

from __future__ import annotations

import copy
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from openai import OpenAI, OpenAIError  # pip install openai
from openai.types.chat.chat_completion import ChatCompletion  # pip install openai
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk  # pip install openai

from .llm_wrapper import LLMWrapper


class OpenAIWrapper(LLMWrapper):
    """
    Wrapper class for the OpenAI API.

    This class provides methods to interact with the OpenAI API,
    including generating chat completions and managing prompts.
    """

    # class values
    _ROLE = 'role'
    _CONTENT = 'content'

    # class functions
    def __init__(
        self,
        key: str,
        config: dict[str, Any] | None = None,
        prompt_log_name: str | None = None,
    ) -> None:
        """
        Initialize the OpenAIWrapper.

        Args:
            key (str): The API key for OpenAI.
            config (dict[str, Any] | None, optional): Configuration options. Defaults to None.
            prompt_log_name (Optional[str], optional): Name of the prompt log file. Defaults to None.

        Raises:
            ValueError: If the API key is invalid.
        """
        config = config or {}
        config = copy.deepcopy(config)
        self._validate_config(config)

        self.model_name_list = [
            'gpt-3.5-turbo',
            'gpt-4',
            'gpt-4-turbo',
            'gpt-4o',
        ]
        self.model_name_dict = {
            'default': 'gpt-3.5-turbo',
            'cheep': 'gpt-3.5-turbo',
            'rich': 'gpt-4o',
        }
        self.prompt_log_name = prompt_log_name
        try:
            self.client = OpenAI(api_key=key)
        except Exception as e:
            msg = f'Invalid API key: {e!s}'
            raise ValueError(msg) from e

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        return

    # TODO: ストリーミングの有無で関数を分ける。  # noqa: FIX002
    #       ストリーミングは返す型も後続で必要な処理も違うので、別の関数としたほうが混乱が少なくなる。
    # ISSUE-003
    def get_response(
        self,
        prompt: list[dict[str, str]],
        config: dict[str, Any] | None = None,
        is_streaming: bool = False,  # noqa: FBT001, FBT002 NOTE: Streaming is only available in presence or absence, so use Boolean.
    ) -> ChatCompletionChunk | ChatCompletion:
        """
        Get a response from the OpenAI API.

        Args:
            prompt (list[dict[str, str]]): The input prompt.
            config (dict[str, Any] | None, optional): Configuration for this request. Defaults to {}.
            is_streaming (bool, optional): Whether to stream the response. Defaults to False.

        Returns:
            Any: The response from the OpenAI API.

        Raises:
            ValueError: If the configuration is invalid.
            RuntimeError: If there's an error in the API call.
        """
        config = config or {}
        config = copy.deepcopy(config)
        self._validate_config(config)
        model_name = config.pop('model_name', self.model_name_dict['default'])

        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=prompt,
                stream=is_streaming,
                # **config,
            )
            self.logger.info('Successfully generated content with model: %s', model_name)
        except OpenAIError as e:
            raise_message = f'Error in OpenAI API call: {e!s}'
            self.logger.exception(raise_message)
            raise RuntimeError(raise_message) from e
        else:
            return response

    def get_chat_response(
        self,
        question: str,
        config: dict[str, Any] | None = None,
        add_prompt: list[dict[str, str]] | None = None,
    ) -> ChatCompletionChunk | ChatCompletion:
        """
        Get a chat response from the OpenAI based on the given question and optional system prompt.

        Args:
            question (str): The user's question or input.
            config (dict[str, Any] | None, optional): Configuration for this specific request. Defaults to None.
            add_prompt (list[dict[str, str]] | None, optional): Additional prompt to guide the LLM's behavior.
                Defaults to None.

        Returns:
            ChatCompletionChunk | ChatCompletion: The chat response from the LLM.
            list[dict[str, str]]: All prompt.
        """
        response, prompt = super().get_chat_response(question, config, add_prompt)
        return response, prompt

    def read_text(self, response: ChatCompletionChunk | ChatCompletion) -> str:
        """
        Extract the text content from the OpenAI response.

        Args:
            response (ChatCompletionChunk | ChatCompletion): The response object from the Gemini.

        Returns:
            str: The extracted text content.
        """
        if type(response) == ChatCompletionChunk:
            text = response.choices[0].delta.content
            if text is None:
                text = ''
        elif type(response) == ChatCompletion:
            text = response.choices[0].message.content

        return text

    def save_prompt_on_newline(self, prompt: list[dict[str, str]], file_name: str | None = None) -> str:
        """
        Save the given prompt to a file, with each message on a new line.

        Args:
            prompt (list[dict[str, str]]): The prompt messages to save.
            file_name (str | None, optional): The name of the file to save to. Defaults to None.

        Returns:
            str: The name of the file where the prompt was saved.
        """
        if file_name is None:
            file_name = self.prompt_log_name

        if Path(file_name).is_file():
            with Path(file_name).open('a', encoding='utf_8_sig', newline='') as f:
                datetime_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # noqa: DTZ005
                # TODO: Set timezone. #  noqa: FIX002
                # ISSUE-001
                # NOTE: Currently, we are only considering use within Japan, so we will omit the time zone setting.
                #       It will be defined as necessary in the next update or later.
                writer = csv.writer(f)
                for p in prompt:
                    role = p[self._ROLE]
                    content = p[self._CONTENT]
                    writer.writerow([datetime_now, role, content])

        return file_name

    def load_prompt(self, file_name: str | None = None) -> list[dict[str, str]]:
        """
        Load a prompt from a file.

        Args:
            file_name (str | None, optional): The name of the file to load from. Defaults to None.

        Returns:
            list[dict[str, str]]: The loaded prompt messages.
        """
        if file_name is None:
            file_name = self.prompt_log_name

        if file_name is not None:
            if Path(file_name).is_file():
                with Path(file_name).open('r', encoding='utf_8_sig') as f:
                    _ = next(csv.reader(f))
                    reader = csv.reader(f)
                    prompt = []
                    for row in reader:
                        time = row[0]  # noqa: F841 NOTE: Although not used, we define it to make it clear that the time variable exists.
                        role = row[1]
                        content = row[2]
                        prompt = self.make_prompt(prompt, role, content)
                    # end for
                # end with

            else:
                with Path(file_name).open('w', encoding='utf_8_sig', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['time', 'role', 'content'])
                    prompt = []
                # end with
            # end if

        return prompt

    def _validate_config(self, config: dict[str, Any]) -> None:
        """
        Validate the configuration dictionary.

        Args:
            config (dict[str, Any]): The configuration to validate.

        Raises:
            ValueError: If the configuration is invalid.
        """
        if 'model_name' in config and config['model_name'] not in self.model_name_list:
            raise_message = f'Invalid model name. Supported models are: {", ".join(self.model_name_list)}'
            raise ValueError(raise_message)

        return
