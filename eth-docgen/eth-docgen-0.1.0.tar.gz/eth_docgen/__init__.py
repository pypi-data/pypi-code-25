
import sys, os, argparse
from os import path
from argparse import ArgumentTypeError
from .docgen import compile_contract, generate_docs

def error_exit(message):
    print('\n{}\n'.format(message))
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Ethereum HTML Document Generator", epilog="\n\n")
    parser.add_argument("-o", "--output", metavar='dir', help="Output directory")

    parser.add_argument("-c", "--contract", metavar='file', help="Contract to generate docs for", required=True)

    parser.add_argument("-s", "--style", help="Inline CSS with output HTML", action='store_true')

    args = parser.parse_args()
    
    out_dir = path.join(os.getcwd(), args.output) if args.output else None

    [source, info, ast] = compile_contract(path.join(os.getcwd(), args.contract))
    generate_docs(source, info, ast, out_dir, inline=args.style)
