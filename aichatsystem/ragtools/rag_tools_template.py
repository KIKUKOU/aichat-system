#!/usr/bin/env python3
"""
The abstract class for rag tools.
"""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Any


class RagTools(metaclass=ABCMeta):
    """
    Abstract base class for RAG (Retrieval-Augmented Generation) tools.

    This class defines the interface for interacting with various RAG tools.
    """

    @abstractmethod
    def __init__(
        self,
        config: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize the RAG tools.

        Args:
            config (dict[str, Any] | None, optional): Configuration options for the tool. Defaults to None.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        self.client = []
        self.speakers_name_dict = {}
        raise_massage = 'Subclasses must implement __init__'
        raise NotImplementedError(raise_massage)

    @abstractmethod
    def get_response(
        self,
        keywords: list[Any],
        config: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get a response from the tool based on the given keywards.

        Args:
            keywords (Any): The input prompt for the LLM.
            config (dict[str, Any], optional): Configuration for this specific request. Defaults to None.
            is_streaming (bool, optional): Whether to stream the response. Defaults to False.

        Returns:
            Any: The response from the LLM.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        raise_massage = 'Subclasses must implement __init__'
        raise NotImplementedError(raise_massage)
