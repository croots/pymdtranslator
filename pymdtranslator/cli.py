import sys
from .base import *


def help_base():
    print("AI batched translation tool for markdown files")
    print("Usage: mdtranslator translate <file>")
    print("Usage: mdtranslator build <UUID>")


def main():
    if len(sys.argv) == 0:
        help_base()
    elif len(sys.argv) == 1:
        help_base()
    elif sys.argv[1] == "help":
        help_base()
    elif sys.argv[1] == "translate":
        if len(sys.argv) != 3:
            print("Invalid arguments")
            help_base()
        else:
            file = sys.argv[2]
            request_translation(file)

    elif sys.argv[1] == "build":
        if len(sys.argv) != 3:
            print("Invalid arguments")
            help_base()
        else:
            batch_id = sys.argv[2]
            build_batch(batch_id)
    else:
        help_base()
