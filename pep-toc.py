#!/usr/bin/env python
"""
Generate a toc for PEPs.

References:

 - genpepindex.py

"""


import sys
import os
import codecs

import re

from operator import attrgetter
from email.parser import HeaderParser
from dateutil.parser import parse as parse_date

from pep0.pep import PEP as PEP_, PEPError


RE_BAD_SUFFIX = re.compile(r'\ .*$')


class PEP(PEP_):

    def __init__(self, pep_file):
        super(PEP, self).__init__(pep_file)

        pep_file.seek(0)
        parser = HeaderParser()
        self.metadata = metadata = parser.parse(pep_file)

        date_string = metadata['Created']

        if date_string:
            self.created = parse_date(RE_BAD_SUFFIX.sub('', metadata['Created']))
        else:
            self.created = None


def get_pep_list(path):

    peps = []
    if os.path.isdir(path):
        for file_path in os.listdir(path):
            if file_path == 'pep-0000.txt':
                continue
            abs_file_path = os.path.join(path, file_path)
            if not os.path.isfile(abs_file_path):
                continue
            if file_path.startswith("pep-") and file_path.endswith((".txt", "rst")):
                with codecs.open(abs_file_path, 'r', encoding='UTF-8') as pep_file:
                    try:
                        pep = PEP(pep_file)
                        if pep.number != int(file_path[4:-4]):
                            raise PEPError('PEP number does not match file name',
                                           file_path, pep.number)
                        peps.append(pep)
                    except PEPError as e:
                        errmsg = "Error processing PEP %s (%s), excluding:" % \
                            (e.number, e.filename)
                        print(errmsg, e, file=sys.stderr)
                        sys.exit(1)
        peps.sort(key=attrgetter('number'))
    elif os.path.isfile(path):
        with open(path, 'r') as pep_file:
            peps.append(PEP(pep_file))
    else:
        raise ValueError("argument must be a directory or file path")

    return peps


def main(argv):

    if not argv[1:]:
        path = '.'
    else:
        path = argv[1]

    pep_metas = [(p.number, p.created, p.type_abbr + p.status_abbr, p.title) for p in get_pep_list(path) if p.created]

    for pep in sorted(pep_metas, key=lambda x: x[1]):
        print('x', *pep, sep='\t')


if __name__ == '__main__':
    main(sys.argv)
