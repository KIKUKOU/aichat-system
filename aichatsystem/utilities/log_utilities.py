#!/usr/bin/env python3
"""
The functions required to obtain log data, and the format of the contents to be included in the log data.
"""

# TODO: Use logging at all.  # noqa: FIX002
# ISSUE-002

from __future__ import annotations

import csv
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Literal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TimeForm(Enum):
    """
    Format for Time class.
    """

    SYSTEM_LOG = '%Y-%m-%d %H:%M:%S'
    LOG_FILE_NAME = '%Y_%m%d'

    def get_form_by_str(self, form: str) -> TimeForm:
        """
        Get format.

        Args:
            form(str): Format name.

        Returns:
            TimeForm: Time format.
        """
        if form == 'SYSTEM_LOG':
            form = TimeForm.SYSTEM_LOG.value
        elif form == 'LOG_FILE_NAME':
            form = TimeForm.LOG_FILE_NAME.value

        return form


class Time:
    """
    Time class for log.
    """

    def __init__(self) -> None:
        """
        Set time.
        """
        self.datetime_now = datetime.now()  # noqa: DTZ005
        # TODO: Set timezone. #  noqa: FIX002
        # ISSUE-001
        # NOTE: Currently, we are only considering use within Japan, so we will omit the time zone setting.
        #       It will be defined as necessary in the next update or later.

    def get_time_str(self, form: TimeForm = TimeForm.SYSTEM_LOG) -> str:
        """
        Get time just now.

        Args:
            form(str): Time format.

        Returns:
            datetime: Time just now.
        """
        return self.datetime_now.strftime(form.value)


def get_latest_modified_file_path(dir_name: str) -> str:
    """
    Get latest Logfile name.

    Args:
        dir_name (str): Log files path.(ex. './log_files/system')

    Returns:
        str: log file names at log files path.

    Raises:
        FileNotFoundError: If no files are found in the specified directory.
    """
    target = Path(dir_name)
    files = [(f, f.stat().st_mtime) for f in target.glob('*.log')]
    if not files:
        raise_massage = f'No files found in directory: {dir_name}'
        raise FileNotFoundError(raise_massage)

    latest_modified_file_path = max(files, key=lambda x: x[1])
    return latest_modified_file_path[0]


def export_log(log_text: str, log_file_name: str) -> None:
    """
    Open log file and write text.

    Args:
        log_text(str) : Log text.
        log_file_name(str) : Log file name with path. (ex. './log_files/system/logfile.log')
    """
    try:
        with Path(log_file_name).open('a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([log_text])
    except OSError:
        logging.exception('Failed to write to log file %s', log_file_name)


def logger(
    status: str,
    log_text: str,
    datetime_now: Time | None = None,
    target: Literal['f', 'p', 'fp'] = 'fp',
    log_file_name: str | None = None,
) -> None:
    """
    Export system information for file and console.

    Args:
        status (str): About log purpose. (ex. system, user, assistant, input/output:text/voice)
        log_text (str): Log text.
        datetime_now (datetime | None, optional): Datetime. Defaults to None.
        target (Literal['f', 'p', 'fp']): Output target. (ex. 'f' for file, 'p' for console, 'fp' both)
        log_file_name (str | None, optional): Log file name with path. Defaults to None.
    """
    if datetime_now is None:
        datetime_now = Time()

    now_str = datetime_now.get_time_str(TimeForm.SYSTEM_LOG)
    log_text = f'{now_str} [{status}] {log_text}'

    if 'p' in target:
        print(log_text)

    if 'f' in target:
        if log_file_name is None:
            try:
                log_file_name = get_latest_modified_file_path('./log_files/system')
            except FileNotFoundError:
                logging.exception('No log file found. Creating a new one.')
                log_file_name = open_log_file()

        export_log(log_text, log_file_name)

    return


def open_log_file(log_file_name: str | None = None) -> str:
    """
    Open log file. And if not exist the file, make new file.

    Args:
        log_file_name (str | None, optional): Log file name with path. Defaults to None.

    Returns:
        str: The path of the opened or created log file.
    """
    datetime_now = Time()

    if log_file_name is None:
        now_str = datetime_now.get_time_str(TimeForm.LOG_FILE_NAME)
        log_file_name = f'./log_files/system/{now_str}.log'

    try:
        with Path(log_file_name).open('a', encoding='utf-8', newline=''):
            pass

        if Path(log_file_name).stat().st_size == 0:
            logger('system', '==== MakeFile ====', datetime_now)
        else:
            logger('system', '==== UseFile ====', datetime_now)

        logger('system', f'{log_file_name}', datetime_now, target='p')
    except OSError:
        logging.exception('Failed to create or open log file %s', log_file_name)

    return log_file_name
