#!/usr/bin/env python -u
# encoding: utf-8
#
# Copyright (c) 2013, Peter Hillerström <peter.hillerstrom@gmail.com>
# All rights reserved. This software is licensed under MIT license.
#
# For the full copyright and license information, please view the LICENSE
# file that was distributed with this source code.
"""Splitter -- Split files by regexp

Usage:
  splitter.py REGEXP (-i infile) [-o dir]
  splitter.py (-h | --help)
  splitter.py --version

Options:
  -i --in infile  Input file to be splitted
  -o --out dir    Output directory [default: .]
  -h --help       Show help screen
  --version       Show version

"""
import math
import os
import sys
import tempfile

from docopt import docopt
from itertools import izip, tee
from subprocess import PIPE, Popen


__version__ = '0.0.1'


def pairwise(iterable):
    """
    Pair consecutive elements and return an iterator.

    >>> list(pairwise([0, 1, 2, 3]))
    [(0, 1), (1, 2), (2, 3)]
    """
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)


def get_byte_boundaries(regexp, infile):
    """
    Equivalent to: `grep -bE regexp infile | cut -d':' -f1`
    """
    p_grep = Popen(['grep', '-boE', regexp, infile], stdout=PIPE)
    p_cut = Popen(['cut', '-d:', '-f1'], stdin=p_grep.stdout, stdout=PIPE)
    p_grep.stdout.close()
    output, errors = p_cut.communicate()
    if errors:
        sys.stderr.write("Error grepping: %s/n" % errors)
    return map(int, filter(None, output.split("\n")))


def filesize(path):
    return os.path.getsize(path)


def fix_bounds_to_file_boundaries(bounds, infile):
    """
    Filter bounds to be within 0 and infile size.
    Return list padded with 0 at start end infile size at the end.
    """
    file_size = filesize(infile)
    bounds = filter(lambda x: 0 < x < file_size, sorted(bounds))
    return [0] + bounds + [file_size]


def pad(count, total):
    return str(count).rjust(int(math.ceil(math.log10(total))), '0')


def split_file_by_bounds(infile, outdir, bounds):
    bounds = fix_bounds_to_file_boundaries(bounds, infile)
    try:
        outdir = tempfile.mkdtemp(prefix='splitter-', dir=outdir)

        with open(infile, 'rb') as f_in:
            for fileno, (start, end) in enumerate(pairwise(bounds)):
                count = end - start
                prefix = pad(fileno, len(bounds) - 1)
                outfile = ''.join((outdir, '/', prefix, '-', os.path.basename(infile)))

                print('>>> Writing %i bytes (starting from %i) into file "%s" (%s of %s)' % \
                      (count, start, outfile, fileno + 1, len(bounds) - 1))

                f_in.seek(start)
                chunk = f_in.read(count)
                with open(outfile, 'wb') as f_out:
                    f_out.write(chunk)
        print('All parts written into:\n%s' % outdir)
    except (IOError, OSError) as err:
        sys.stderr.write("Splitter [ERROR] IO or OS error: %s\n" % err)
        exit(1)


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Splitter ' + __version__)
    regexp = arguments['REGEXP']
    infile = arguments['--in']
    outdir = arguments['--out']
    
    bounds = get_byte_boundaries(regexp, infile)

    if len(bounds) > 0:
        split_file_by_bounds(infile, outdir, bounds)
    else:
        sys.stderr.write("No matches found!\n")
