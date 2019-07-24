#!/usr/local/bin/python3
import argparse
import os.path
import random
import sys
from itertools import groupby

__author__ = 'Sam Kariuki, david matten'



def py3_fasta_iter(fasta_name):
    """
    modified from Brent Pedersen: https://www.biostars.org/p/710/#1412
    given a fasta file. yield tuples of header, sequence
    """
    fh = open(fasta_name)
    faiter = (x[1] for x in groupby(fh, lambda line: line[0] == ">"))
    for header in faiter:
        # drop the ">"
        headerStr = header.__next__()[1:].strip()
        # join all sequence lines to one.
        seq = "".join(s.strip() for s in faiter.__next__())
        yield (headerStr, seq)


def py2_fasta_iter(fasta_name):
    """
    from Brent Pedersen: https://www.biostars.org/p/710/#1412
    given a fasta file. yield tuples of header, sequence
    """
    fh = open(fasta_name)
    faiter = (x[1] for x in groupby(fh, lambda line: line[0] == ">"))
    for header in faiter:
        # drop the ">"
        header = header.next()[1:].strip()
        # join all sequence lines to one.
        seq = "".join(s.strip() for s in faiter.next())
        yield header, seq


def fasta_form(k,v):
    return '>' + k + '\n' + v + '\n'

def main(fasta_fn, output_fn):
    # detect which version of python we are using
    cur_version = sys.version_info
    if cur_version >= (3,0):
        fasta_gen = py3_fasta_iter(fasta_fn)
    elif cur_version < (3,0):
        fasta_gen = py2_fasta_iter(fasta_fn)
    fasta_dict = {}
    for k,v in fasta_gen:
        fasta_dict[k] = v
    
    # read keys from dictionary
    keys = list(fasta_dict.keys())

    # shuffle keys
    random.shuffle(keys)

    # fasta-formated lines based on shuffled keys
    output_lines = [fasta_form(k, fasta_dict[k]) for k in keys]

    # write lines to file
    with open(output_file, 'w') as f:
        f.write(''.join(output_lines))


if __name__ != "__main":
    # read arguments
    parser = argparse.ArgumentParser(description='Shuffle sequences in fasta format file')
    parser.add_argument('-input',  '--input', type=str, help='path to the input *.fasta file')
    parser.add_argument('-output', '--output', type=str, help='path to the output *.fasta file')
    args = parser.parse_args()

    # get input/output paths
    input_file  =  args.input
    output_file =  args.output

    # check if input file exists
    if not os.path.isfile(input_file):
        print("It appears that the input file does not exist. Now exiting.")
        sys.exit()


    # check if output file exists
    if os.path.isfile(output_file):
        cont = str(input("File '" + output_file + "' already exists. Would you like to overwrite (y/n)? "))
        if cont != 'y':
            sys.exit()
    
    main(input_file, output_file)
