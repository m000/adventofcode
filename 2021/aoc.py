"""Boilerplate code for AoC solutions."""
import logging
import os
from pathlib import Path


def input_file(day, specifier=None):
    input_dir = Path(__file__).parent / 'input'
    specifier = specifier if specifier is not None else os.environ.get('AOC_INPUTSPEC', None)
    if specifier is not None:
        return input_dir / f'input{day:02d}.{specifier}.txt'
    else:
        return input_dir / f'input{day:02d}.txt'


def input_lines(day, specifier=None, keepends=False):
    return input_file(day, specifier).read_text().splitlines(keepends=keepends)


def input(day, specifier=None, striplines=True):
    with input_file(day, specifier).open() as f:
        for line in f:
            yield line if not striplines else line.strip()


def input_enum(day, specifier=None, striplines=True, start=0):
    with input_file(day, specifier).open() as f:
        for n, line in enumerate(f, start=start):
            line = line if not striplines else line.strip()
            yield n, line


def logging_setup(loglevel_default='WARNING'):
    loglevel = os.environ.get('AOC_LOGLEVEL', loglevel_default).upper()
    logging.basicConfig(level=loglevel)


def hr(fill='-', width=80, label=None):
    if label is None:
        return fill*width
    else:
        align = '<'
        return f'---{f" {label} ":{fill}{align}{width-5}}'
