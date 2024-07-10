#!/usr/bin/env python3
"""
The class wrap gemini api.
"""

from __future__ import annotations

import copy
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import google.generativeai as genai  # pip install google-generativeai
from google.api_core import exceptions as google_exceptions  # pip install google-generativeai

if TYPE_CHECKING:
    from google.generativeai.types.generation_types import GenerateContentResponse  # pip install google-generativeai

from .llm_wrapper import LLMWrapper


class GeminiWrapper(LLMWrapper):
    """
    Wrapper class for the Google Gemini API.

    This class provides methods to interact with the Gemini API,
    including generating responses and managing prompts.
    """

    # class values
    _ROLE = 'role'
    _CONTENT = 'parts'

    # class functions
    def __init__(
        self,
        key: str,
        config: dict[str, Any] | None = None,
        prompt_log_name: str | None = None,
    ) -> None:
        """
        Initialize the GeminiWrapper.

        Args:
            key (str): The API key for Gemini.
            config (dict[str, Any], optional): Configuration options. Defaults to None.
            prompt_log_name (str | None, optional): Name of the file to log prompts. Defaults to None.

        Raises:
            ValueError: If the API key is invalid.
        """
        config = config or {}
        config = copy.deepcopy(config)
        self.model_name_list = ['gemini-1.5-flash', 'gemini-1.5-pro']
        self.model_name_dict = {
            'default': 'gemini-1.5-flash',
            'cheep': 'gemini-1.5-flash',
            'rich': 'gemini-1.5-pro',
        }
        self.prompt_log_name = prompt_log_name
        self._responce_type = None
        try:
            genai.configure(api_key=key)
            self.client = []
        except Exception as e:
            msg = f'Invalid API key: {e!s}'
            raise ValueError(msg) from e

        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_response(
        self,
        prompt: list[dict[str, str]],
        config: dict[str, Any] | None = None,
        is_streaming: bool = False,  # noqa: FBT001, FBT002 NOTE: Streaming is only available in presence or absence, so use Boolean.
    ) -> GenerateContentResponse:
        """
        Get a response from the Gemini API.

        Args:
            prompt (List[Dict[str, str]]): The input prompt.
            config (Optional[Dict[str, Any]], optional): Configuration for this request.
            Defaults to None.
            is_streaming (bool, optional): Whether to stream the response. Defaults to False.

        Returns:
            Any: The response from the Gemini API.

        Raises:
            ValueError: If the configuration is invalid.
            RuntimeError: If there's an error in the API call.
        """
        config = config or {}
        config = copy.deepcopy(config)
        self._validate_config(config)

        model_name = config.pop('model_name', self.model_name_dict['default'])

        try:
            self.client = genai.GenerativeModel(
                model_name=model_name,
                generation_config=config,
            )
            response = self.client.generate_content(
                prompt,
                stream=is_streaming,
            )
            self.logger.info('Successfully generated content with model: %s', model_name)
        except google_exceptions.GoogleAPIError as e:
            raise_message = f'Error in Gemini API call: {e!s}'
            self.logger.exception(raise_message)
            raise RuntimeError(raise_message) from e
        else:
            self._responce_type = type(response)
            return response

    def read_text(self, response: GenerateContentResponse) -> str:
        """
        Extract the text content from the Gemini response.

        Args:
            response (GenerateContentResponse): The response object from the Gemini.

        Returns:
            str: The extracted text content.

        Raises:
            ValueError: If the response is invalid.
        """
        if 'text' in vars(response):
            text = response.text
        else:
            text = ''

        return text

    def save_prompt_on_newline(self, prompt: list[dict[str, str]], file_name: str | None = None) -> str:
        """
        Save the given prompt to a file, with each message on a new line.

        Args:
            prompt (list[dict[str, str]]): The prompt messages to save.
            file_name (str | None = None, optional): The name of the file to save to. Defaults to None.

        Returns:
            str: The name of the file where the prompt was saved.

        Raises:
            pass
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
                    if role == 'model':
                        role = 'assistant'

                    writer.writerow([datetime_now, role, content])

        return file_name

    def load_prompt(self, file_name: str | None = None) -> list[dict[str, str]]:
        """
        Load a prompt from a file.

        Args:
            file_name (str | None, optional): The name of the file to load from.
                Defaults to None.

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
                        if role == 'system':
                            role = 'user'
                        elif role == 'assistant':
                            role = 'model'
                        # end if

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
