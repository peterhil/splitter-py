# Splitter

**Splitter** is a quick and dirty solution to split (possibly large) files by regexp into parts, 
and output them into a new subdirectory of the given outdir option (defaults to the current directory).

Calls shell commands grep and cut to get the byte boundaries of the matches.
Does nothing if the regexp doesn't match anything in the input file.

## Usage

    ./splitter.py '^Foo' -i example.yml -o .

## Help

    ./splitter.py -h

## License

Copyright (c) 2013, Peter Hillerström <peter.hillerstrom@gmail.com>  
All rights reserved. This software is licensed under MIT license.

For the full copyright and license information, please view the LICENSE  
file that was distributed with this source code.
