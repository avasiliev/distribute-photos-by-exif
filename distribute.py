#!/usr/bin/env python3 

from datetime import datetime
from pathlib import Path
import argparse
import exifread
import logging
import os
import sys


log = logging.getLogger(__name__)


def _get_exif_date(image_path):
    with open(image_path, 'rb') as image_file:
        tags = exifread.process_file(image_file)
    datetime_string = tags.get('EXIF DateTimeOriginal') or tags.get('Image DateTime')
    if not datetime_string:
        return None
    if str(datetime_string).startswith('0000'):
        return None
    try:
        return datetime.strptime(str(datetime_string), '%Y:%m:%d %H:%M:%S')
    except ValueError:
        return None


def _create_directory_for_date(destination_path, date):
    directory = Path(destination_path, f'{date.year}', f'{date.month:02d}')
    Path(directory).mkdir(parents=True, exist_ok=True)
    return directory


def _make_hardlink(source_path, destination_path):
    log.info(f'{source_path!s} <- {destination_path!s}')
    destination_path.symlink_to(source_path)


def distribute(source_path, destination_path):
    source_path = Path(source_path).resolve()
    destination_path = Path(destination_path).resolve()
    log.info(f'{source_path=!s}')
    log.info(f'{destination_path=!s}')

    try:
        source_path.relative_to(destination_path)
    except ValueError:
        pass
    else:
        raise Exception('Source and destination paths are relative')
    
    for directory, _, file_names in os.walk(source_path):
        for file_name in file_names:
            if Path(file_name).suffix.lower() not in ('.jpg', '.jpeg'):
                continue
            file_path = Path(directory, file_name)
            exif_datetime = _get_exif_date(file_path)
            if exif_datetime is None:
                log.warning(f'No datetime found for {file_path!s}')
                continue
            datetime_directory = _create_directory_for_date(destination_path, exif_datetime.date())
            datetime_file_name = '{}.jpg'.format(exif_datetime.isoformat())
            _make_hardlink(file_path, Path(datetime_directory, datetime_file_name))


def main():
    logging.basicConfig(stream=sys.stderr, level=logging.INFO, format='%(msg)s')

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--source-path', required=True)
    argument_parser.add_argument('--destination-path', required=True)
    arguments = argument_parser.parse_args()
    distribute(arguments.source_path, arguments.destination_path)


if __name__ == '__main__':
    main()