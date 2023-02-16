from traceback import format_exception_only as f_exc
from os.path import isfile

from yaml import safe_load

from ui import UI
import db


class Worker():
    
    def __init__(self):
        self.ui = UI()
        self.db = db.DB()
        in_file = self.ui.args.file
        if in_file:
            self.process_file(in_file)
            #self.show_ex_data()

    def process_file(self, in_file):
        if in_file:
            if not isfile(in_file):
               self.ui.show_msg(f'{in_file} not found or not a file')
            else:
                self.ui.show_msg(f'validating {in_file}')
                with open(in_file) as in_f:
                    data = safe_load(in_f)
                    err_msg, data = self.db.check_all(data)
                if err_msg:
                    self.ui.show_msg(err_msg)
                else:
                    self.ui.show_msg(f'{in_file} is valid')
                    if not self.ui.args.validate:
                        self.ui.show_msg(f'processing {in_file}')
                        self.db.put_data(data)
                        self.ui.show_msg(f'{in_file} processed')
'''
    def show_ex_data(self):
        for i in self.db.get_ex_data():
            for n in i:
                self.ui.show_msg(n)
                
'''
if __name__ == "__main__":
    w = Worker()
    

