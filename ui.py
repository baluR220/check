from argparse import ArgumentParser
import tkinter as tk


class UI():

    def __init__(self):
        self.args = self.get_args()

    def get_args(self):
        parser = ArgumentParser()
        parser.add_argument('-f', dest='file', help='path to yaml with data')
        parser.add_argument(
            '-v', dest='validate', action='store_true',
            help='validate file and exit'
        )
        parser.add_argument(
            '-g', dest='gui', action='store_true',
            help='start with gui'
        )
        args = parser.parse_args()
        if not (args.gui or args.file):
            parser.print_help()
        return(args)

    def show_msg(self, *args, **kwargs):
        print(*args, **kwargs)

