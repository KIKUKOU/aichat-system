#!/usr/bin/env python3
"""
The class for google search.
"""

from __future__ import annotations

from typing import Any

from googleapiclient.discovery import build

from .rag_tools_template import RagTools


class GoogleSearch(RagTools):
    """
    Search on google custom search.
    """

    def __init__(
        self,
        key: str,
        cse_id: str,
        config: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> None:
        """
        Initialize the RAG tools.

        Args:
            key (str): The API key for GCP.
            cse_id (str): Search engine ID.
            config (dict[str, Any] | None, optional): Configuration options for the tool. Defaults to None.

        Raises:
            ValueError: If the API key is invalid.
        """
        try:
            self.client = build('customsearch', 'v1', developerKey=key)
        except Exception as e:
            msg = f'Invalid API key: {e!s}'
            raise ValueError(msg) from e

        self.cse_id = cse_id

    def get_response(
        self,
        keywords: list[Any],
        num_of_items: int = 3,
        config: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> list[dict[str, Any]]:
        """
        Get a response from the tool based on the given keywards.

        Args:
            keywords (Any): The input prompt for the search.
            num_of_items(int): num of use articles. Default is 3.
            config (dict[str, Any], optional): Configuration for this specific request. Defaults to None.

        Returns:
            Any: The response from the LLM.
        """
        return self.client.cse().list(q=keywords, cx=self.cse_id, lr='lang_ja', num=num_of_items, start=1).execute()

    @staticmethod
    def convert_search_result(data: dict[str, Any]) -> dict[str, Any]:
        """
        convert data for ai input.

        Args:
            data (dict[str, Any]): The raw data from google search.

        Raises:
            ValueError: If the keywords is invalid.
        """
        output = {
            'queries': {
                'request': [
                    {
                        'searchTerms': data['queries']['request'][0]['searchTerms'],
                        'count': data['queries']['request'][0]['count'],
                        'startIndex': data['queries']['request'][0]['startIndex'],
                    },
                ],
            },
            'searchInformation': {
                'searchTime': data['searchInformation']['searchTime'],
                'totalResults': data['searchInformation']['totalResults'],
            },
            'items': [],
        }

        # itemsの処理
        for item in data['items']:
            output['items'].append({'title': item['title'], 'link': item['link'], 'snippet': item['snippet']})

        return output
