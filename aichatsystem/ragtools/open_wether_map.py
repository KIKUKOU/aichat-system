#!/usr/bin/env python3
"""
The class for open werher map(get wether).
"""

from __future__ import annotations

import datetime
from typing import Any

import requests

from .rag_tools_template import RagTools

api_key = 'a51b01c289dfcc6c5825e18dec77592c'
city = 'Tokyo'


class OpenWetherMap(RagTools):
    """
    Search the wether.
    """

    ERROR_STATUS_CODE = 200

    def __init__(
        self,
        key: str,
        config: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> None:
        """
        Initialize the RAG tools.

        Args:
            key (str): The API key for OpenAI.
            config (dict[str, Any] | None, optional): Configuration options for the tool. Defaults to None.
        """
        try:
            self.api_key = key
        except Exception as e:
            msg = f'Invalid API key: {e!s}'
            raise ValueError(msg) from e

    def get_response(
        self,
        keywords: dict[str, Any],
        config: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> dict[str, Any]:
        """
        Get a response from the tool based on the given keywards.

        Args:
            keywords (dict[str, Any]):
                The input keywards.
                ex1. city:Tokyo, time:3
                ex2. latitude:40.0000, longitude 140.0000, time:-24
                :: (S) -90 < latitude < 90 (N), (W) -180 < longitude < 180 (E).
                :: time(h) minus is before.
            config (dict[str, Any], optional): Configuration for this specific request. Defaults to None.
            is_streaming (bool, optional): Whether to stream the response. Defaults to False.

        Returns:
            Any: The response from the LLM.
        """
        url = 'https://api.openweathermap.org/data/2.5/forecast'
        self._validate_keywords(keywords)
        if 'city' in keywords:
            response = self._search_by_city(url, keywords)
        else:
            url = self._search_by_lat_lon(url, keywords)

        data = response.json()
        # エラーチェック
        if response.status_code != self.ERROR_STATUS_CODE:
            raise (f"error: {data['message']}")

        wether_time = datetime.datetime.today() + datetime.timedelta(hours=keywords['time'])  # noqa: DTZ002
        # TODO: Set timezone. #  noqa: FIX002
        # ISSUE-001
        wether_time = wether_time.replace(microsecond=0)
        for forecast in data['list']:
            forecast_time = datetime.datetime.fromtimestamp(forecast['dt'])  # noqa: DTZ006
            if forecast_time >= wether_time:
                return forecast

        return None

    def _search_by_city(self, url: str, keywords: dict[str, Any]) -> str:
        """
        Get the url by city name.

        Args:
            url (str): The wether api url.
            keywords (dict[str, Any]): The input keywards.

        Returns:
            str: search url.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        city = keywords['city']
        return requests.get(
            url,
            params={
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'ja',
            },
            timeout=10,
        )

    def _search_by_lat_lon(self, url: str, keywords: dict[str, Any]) -> str:
        """
        Get the url by city name.

        Args:
            url (str): The wether api url.
            keywords (dict[str, Any]): The input keywards.

        Returns:
            str: search url.

        Raises:
            NotImplementedError: If not implemented in subclass.
        """
        lat = keywords['lat']
        lon = keywords['lon']
        return requests.get(
            url,
            params={
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'ja',
            },
            timeout=10,
        )

    def _validate_keywords(self, keywords: dict[str, Any]) -> None:
        """
        Validate the keywords dictionary.

        Args:
            keywords (dict[str, Any]): The keywords to validate.

        Raises:
            ValueError: If the keywords is invalid.
        """
        if 'time' not in keywords:
            raise_message = 'Invalid keywords in time. It need time and city or time and lat and lon'
            raise ValueError(raise_message)

        if 'city' not in keywords and ('lat' not in keywords or 'lon' not in keywords):
            raise_message = 'Invalid keywords in forecast point. It need time and city or time and lat and lon'
            raise ValueError(raise_message)
