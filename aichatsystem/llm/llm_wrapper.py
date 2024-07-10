#!/usr/bin/env python3
"""
The abstract class for llm wrapper.
"""

from __future__ import annotations

import copy
from abc import ABCMeta, abstractmethod
from typing import Any


class LLMWrapper(metaclass=ABCMeta):
    """
    Abstract base class for LLM (Large Language Model) API wrappers.

    This class defines the interface for interacting with various LLM APIs,
    providing a consistent way to handle prompts, responses, and configurations.
    """

    # class values
    _ROLE = ''
    _CONTENT = ''

    # class functions
    @abstractmethod
    def __init__(
        self,
        key: str,
        config: dict[str, Any] | None = None,
        prompt_log_name: str | None = None,
    ) -> None:
        """
        Initialize the LLM wrapper.

        Args:
            key (str): API key for the LLM service.
            config (dict[str, Any] | None, optional): Configuration options for the LLM.
                Defaults to None.
            prompt_log_name (str | None, optional): Name of the file to log prompts. Defaults to None.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        config = config or {}
        config = copy.deepcopy(config)
        self.model_name_list = []
        self.model_name_dict = {}
        self.prompt_log_name = prompt_log_name
        self.client = None
        raise_message = 'Subclasses must implement __init__'
        raise NotImplementedError(raise_message)

    @abstractmethod
    def get_response(
        self,
        prompt: list[dict[str, str]],
        config: dict[str, Any] | None = None,
        is_streaming: bool = False,  # noqa: FBT001, FBT002 NOTE: Streaming is only available in presence or absence, so use Boolean.
    ) -> Any:
        """
        Get a response from the LLM based on the given prompt.

        Args:
            prompt (list[dict[str, str]]): The input prompt for the LLM.
            config (dict[str, Any], optional): Configuration for this specific request. Defaults to None.
            is_streaming (bool, optional): Whether to stream the response. Defaults to False.

        Returns:
            Any: The response from the LLM.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        raise_message = 'Subclasses must implement get_response'
        raise NotImplementedError(raise_message)

    def get_chat_response(
        self,
        question: str,
        config: dict[str, Any] | None = None,
        add_prompt: list[dict[str, str]] | None = None,
    ) -> Any:
        """
        Get a chat response from the LLM based on the given question and optional system prompt.

        Args:
            question (str): The user's question or input.
            config (dict[str, Any] | None, optional): Configuration for this specific request. Defaults to None.
            add_prompt (list[dict[str, str]] | None, optional): Additional prompt to guide the LLM's behavior.
                Defaults to None.

        Returns:
            Any: The chat response from the LLM.
            list[dict[str, str]]: All prompt.
        """
        config = copy.deepcopy(config)
        streaming = config.pop('streaming', False)

        prompt = self.load_prompt()
        if add_prompt is not None:
            for p in add_prompt:
                role = p[self._ROLE]
                content = p[self._CONTENT]
                prompt = self.make_prompt(prompt, role, content)

        prompt = self.make_prompt(prompt, 'user', question)
        response = self.get_response(prompt, config, streaming)
        # save content
        save_prompt = self.make_prompt([], 'user', question)
        self.save_prompt_on_newline(save_prompt)
        return response, prompt

    def save_assistant_response(self, content: str) -> None:
        """
        Save the assistant response text at prompt log file.

        Args:
            content (str): The response text from the LLM.
        """
        prompt = self.make_prompt([], 'assistant', content)
        self.save_prompt_on_newline(prompt)
        return

    @abstractmethod
    def read_text(self, response: Any) -> str:
        """
        Extract the text content from the LLM's response.

        Args:
            response (Any): The response object from the LLM.

        Returns:
            str: The extracted text content.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        raise_message = 'Subclasses must implement read_text'
        raise NotImplementedError(raise_message)

    def make_prompt(self, prompt: list[dict[str, str]], role: str, content: str) -> list[dict[str, str]]:
        """
        Create a prompt by adding a new message with the specified role and content.

        Args:
            prompt (list[dict[str, str]]): The existing prompt messages.
            role (str): The role of the new message (e.g., "user", "assistant", "system").
            content (str): The content of the new message.

        Returns:
            list[dict[str, str]]: The updated prompt with the new message added.
        """
        prompt.append({self._ROLE: role, self._CONTENT: content})
        return prompt

    def add_prompt(self, base_prompt: list[dict[str, str]], add_prompt: list[dict[str, str]]) -> list[dict[str, str]]:
        """
        Create a prompt by adding a other prompt.

        Args:
            base_prompt (list[dict[str, str]]): The existing prompt messages.
            add_prompt (list[dict[str, str]]): The other prompt messages.

        Returns:
            list[dict[str, str]]: The updated prompt with the other prompt added.
        """
        for p in add_prompt:
            role = p[self._ROLE]
            content = p[self._CONTENT]
            base_prompt.append({self._ROLE: role, self._CONTENT: content})

        return base_prompt

    @abstractmethod
    def save_prompt_on_newline(self, prompt: list[dict[str, str]], file_name: str | None = None) -> str:
        """
        Save the given prompt to a file, with each message on a new line.

        Args:
            prompt (list[dict[str, str]]): The prompt messages to save.
            file_name (str | None, optional): The name of the file to save to. Defaults to None.

        Returns:
            str: The name of the file where the prompt was saved.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        raise_message = 'Subclasses must implement save_prompt_on_newline'
        raise NotImplementedError(raise_message)

    @abstractmethod
    def load_prompt(self, file_name: str | None = None) -> list[dict[str, str]]:
        """
        Load a prompt from a file.

        Args:
            file_name (str | None, optional): The name of the file to load from.
                Defaults to None.

        Returns:
            list[dict[str, str]]: The loaded prompt messages.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        raise_message = 'Subclasses must implement load_prompt'
        raise NotImplementedError(raise_message)

    @abstractmethod
    def _validate_config(self, config: dict[str, Any]) -> None:
        """
        Validate the configuration dictionary.

        Args:
            config (dict[str, Any]): The configuration to validate.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        raise_message = 'Subclasses must implement _validate_config'
        raise NotImplementedError(raise_message)
