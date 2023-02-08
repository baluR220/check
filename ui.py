from argparse import ArgumentParser


class UI():

    def __init__(self):
        self.args = self.get_args()

    def get_args(self):
        parser = ArgumentParser()
        parser.add_argument('-f', help='path to yaml with data')
        return(parser.parse_args())

    
    def show_msg(self, *args, **kwargs):
        print(*args, **kwargs)

