#!/usr/bin/env python3 

import argparse
import exifread
import os


def distribute(source_path, destination_path):
    source_path = os.path.abspath(source_path)
    destination_path = os.path.abspath(destination_path)
    assert source_path not in destination_path and destination_path not in source_path
    
    for directory, _, file_names in os.walk():
        for file_name in file_names:
            if os.path.splitext(file_name)[1].lower() not in ('.jpg', '.jpeg'):
                continue
            file_path = os.path.join(directory, file_name)
            _get_exif_date()


def main():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--source-path', required=True)
    argument_parser.add_argument('--destination-path', required=True)
    arguments = argument_parser.parse_args()
    distribute(arguments.source_path, arguments.destination_path)


if __name__ == '__main__':
    main()