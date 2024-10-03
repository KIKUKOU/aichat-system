#!/usr/bin/env python3
"""
The class for open werher map(get weather).
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import pytz
import requests

from .rag_tools_template import RagTools


class OpenWeatherMap(RagTools):
    """
    Search the weather.
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
            key (str): The API key for open weather map.
            config (dict[str, Any] | None, optional): Configuration options for the tool. Defaults to None.

        Raises:
            ValueError: If the API key is invalid.
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

        Returns:
            Any: The response from open weather map 5days(3h) weather.
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

        return data

    def _search_by_city(self, url: str, keywords: dict[str, Any]) -> str:
        """
        Get the url by city name.

        Args:
            url (str): The weather api url.
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
            },
            timeout=10,
        )

    def _search_by_lat_lon(self, url: str, keywords: dict[str, Any]) -> str:
        """
        Get the url by city name.

        Args:
            url (str): The weather api url.
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

    @staticmethod
    def convert_weather_data_by_5days(data: dict[str, Any]) -> dict[str, Any]:
        """
        convert data for ai input.

        Args:
            data (dict[str, Any]): The raw data from open weather map by 5days forcust.

        Raises:
            ValueError: If the keywords is invalid.
        """
        output = {
            'list': [],
            'city': {
                'name': data['city']['name'],
                'coord': data['city']['coord'],
                'country': data['city']['country'],
                'timezone': data['city']['timezone'],
                'sunrise': data['city']['sunrise'],
                'sunset': data['city']['sunset'],
            },
        }

        jst = pytz.timezone('Asia/Tokyo')
        now = datetime.now(jst)
        today = now.date()
        tomorrow = today + timedelta(days=1)
        day_after_tomorrow = today + timedelta(days=2)

        for item in data['list']:
            dt = datetime.fromtimestamp(item['dt'], pytz.UTC).astimezone(jst)
            item_date = dt.date()

            # 今日と明日の条件
            condition_today_tomorrow = (
                item_date <= tomorrow and (dt.hour in [0, 6, 12, 18] or dt <= now) and dt.minute == 0
            )

            # 明後日以降の条件
            condition_future = item_date >= day_after_tomorrow and dt.hour in [12] and dt.minute == 0

            if condition_today_tomorrow or condition_future:
                new_item = {
                    'dt': item['dt'],
                    'main': {
                        'temp': item['main']['temp'],
                        'feels_like': item['main']['feels_like'],
                        'pressure': item['main']['pressure'],
                        'humidity': item['main']['humidity'],
                    },
                    'weather': [
                        {'main': item['weather'][0]['main'], 'description': item['weather'][0]['description']},
                    ],
                    'clouds': item['clouds'],
                    'wind': item['wind'],
                    'pop': item['pop'],
                    'dt_txt': dt.strftime('%Y-%m-%d %H:%M:%S'),
                }

                if 'rain' in item:
                    new_item['rain'] = item['rain']

                output['list'].append(new_item)

        output['list'].sort(key=lambda x: x['dt'])
        return output
