from traceback import format_exception_only as f_exc
from os.path import exists

from yaml import safe_load

from ui import UI
import db


class Worker():
    
    def __init__(self):
        self.ui = UI()
        self.db = db.DB()
        in_file = self.ui.args.f
        if in_file:
            self.process_file(in_file)

    def process_file(self, in_file):
        if in_file:
            if not exists(in_file):
               self.ui.show_msg(f'{in_file} not found')
            else:
                with open(in_file) as in_f:
                    data = safe_load(in_f)
                    err_msg, data = self.db.check_all(data)
                if err_msg:
                    self.ui.show_msg(err_msg)
                else:
                    self.db.put_data(data)



if __name__ == "__main__":
    w = Worker()
    

