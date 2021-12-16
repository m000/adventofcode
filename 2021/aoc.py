"""Boilerplate code for AoC solutions."""
import logging
import os
from itertools import repeat, takewhile
from pathlib import Path
from types import SimpleNamespace
from collections import namedtuple

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


def char_input(day, specifier=None, valid=None, ignored=None):
    """Reads input for day character by character. valid and ignored can
    be used to specify which characters are yielded (valid) and which
    are silently dropped (ignore). For any other characters, a warning
    will be logged.
    """
    if valid is None:
        is_valid = lambda c: True
    elif callable(valid):
        is_valid = valid
    else:
        is_valid = lambda c: c in valid

    if ignored is None:
        is_ignored = lambda c: True
    elif callable(ignored):
        is_ignored = ignored
    else:
        is_ignored = lambda c: c in ignored

    with input_file(day, specifier).open() as f:
        c = f.read(1)
        if is_valid(c):
            yield c
        elif is_ignored(c):
            continue
        else:
            logging.warning("Invalid character '{c}' in {f.name}:{f.tell()}.")


"""Named tuple for specifing how multi_input processes the input."""
MultiInputSpecifier = namedtuple('MultiInputSpecifier', ('name', 'takewhile_condition', 'line_parse'))

#def multi_input(day, specifier=None, striplines=True):
    #with input_file(day, specifier).open() as f:
        #for mispec in 
        #for l in takewhile
        #for line in f:
            #yield line if not striplines else line.strip()


def logging_setup(loglevel_default='WARNING'):
    """Sets up logging for AoC programs. Loglevel can be specified through the
    AOC_LOGLEVEL environment variable when running a program. A default level
    may be supplied to use when AOC_LOGLEVEL is not set.
    """
    loglevel = os.environ.get('AOC_LOGLEVEL', loglevel_default).upper()
    logging.basicConfig(level=loglevel)


def hr(fill='-', width=80, label=None):
    if label is None:
        return fill*width
    else:
        align = '<'
        return f'---{f" {label} ":{fill}{align}{width-5}}'
