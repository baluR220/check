from argparse import ArgumentParser
import tkinter as tk


class UI():

    def __init__(self, **kwargs):
        self.args = self.get_args()
        self.gui = self.cli = None
        if self.args.gui:
            kwargs['ui'] = self
            self.front = GUI(**kwargs)
        else:
            self.front = CLI()

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
        self.front.show_msg(*args, **kwargs)


class GUI():
 
    def __init__(self, ui, choices_dict):
        self.ui = ui
        root = tk.Tk()
        self.root = root
        root.geometry("600x400")
        root.bind('<Button-1>', self.set_focus)
        self.last_pack_index = 0
        self.create_entry_pack(
            root, choices_dict
        )
        new_check_b = tk.Button(
            root, text='Add check', 
            command=self.add_check
        )
        new_check_b.pack()
        root.mainloop()

    def show_msg(self, *args, **kwargs):
        print(*args, **kwargs)

    def set_focus(self, event):
        event.widget.focus_set()

    def create_entry_pack(self, parent, choices_dict):
        self.sug_f = None
        pack_f = tk.Frame(parent)
        pack_f.goods = []
        pack_f.pack()
        l = tk.Label(pack_f, text='Datetime')
        l.grid(column=0, row=0)
        datetime = tk.Entry(pack_f)
        datetime.grid(column=0, row=1)
        l = tk.Label(pack_f, text='Shop name')
        l.grid(column=1, row=0)
        shop_name_val = tk.StringVar()
        shop_name = tk.Entry(
            pack_f, textvariable=shop_name_val
        )
        shop_name_val.trace_add(
            "write",
            lambda *args: self.entry_change_hook(
                choices_dict['shop_name'], shop_name,
                shop_name_val, *args
            )
        )
        shop_name.grid(column=1, row=1)
        l = tk.Label(pack_f, text='Shop address')
        l.grid(column=2, row=0)
        shop_addr_val = tk.StringVar()
        shop_addr = tk.Entry(
            pack_f, textvariable=shop_addr_val
        )
        shop_addr_val.trace_add(
            "write",
            lambda *args: self.entry_change_hook(
                choices_dict['shop_addr'], shop_addr,
                shop_addr_val, *args
            )
        )
        shop_addr.grid(column=2, row=1)
        l = tk.Label(pack_f, text='Goods')
        l.grid(column=0, row=2, pady=5)
        pack_f.good_row = 3
        self.create_good(pack_f, choices_dict)
        new_good_b = tk.Button(
            pack_f, text='Add good', 
            command=lambda: self.add_good(pack_f, choices_dict),
            name='new_good_b'
        )
        new_good_b.grid(column=2, row=pack_f.good_row+1)
        l = tk.Label(pack_f, text='Total', name='total_l')
        l.grid(column=0, row=pack_f.good_row)
        total_val = tk.StringVar()
        total = tk.Entry(
            pack_f, textvariable=total_val, name='total_e'
        )
        total.grid(column=0, row=pack_f.good_row+1)

    def entry_change_hook(self, choices_list, entry, entry_val, *args):
        if not entry_val.get() or self.sug_f:
            self.sug_f.destroy()
        self.sug_f = tk.Frame(self.root)
        self.sug_f.place(
            x=entry.winfo_x()+entry.master.winfo_x(),
            y=entry.winfo_y()+entry.master.winfo_y()+entry.winfo_height()
        )
        val = entry_val.get()
        if val:
            for i in sorted(choices_list):
                if val in i:
                    tk.Button(
                        self.sug_f, text=i,
                        command=lambda x=i: self.change_val(x, entry_val)
                    ).pack()

    def change_val(self, i, entry_val):
        entry_val.set(i)
        self.sug_f.destroy()

    def create_good(self, pack_f, choices_dict):
        good_f = tk.Frame(pack_f)
        good_f.grid(column=0, columnspan=3, row=pack_f.good_row, pady=10)
        pack_f.goods.append(good_f)
        l = tk.Label(good_f, text='Full name')
        l.grid(column=0, row=0)
        full_name_val = tk.StringVar()
        full_name = tk.Entry(
            good_f, textvariable=full_name_val
        )
        full_name_val.trace_add(
            "write",
            lambda *args: self.entry_change_hook(
                choices_dict['full_name'], full_name,
                full_name_val, *args
            )
        )
        full_name.grid(column=0, row=1)
        l = tk.Label(good_f, text='Short name')
        l.grid(column=1, row=0)
        short_name_val = tk.StringVar()
        short_name = tk.Entry(
            good_f, textvariable=short_name_val
        )
        short_name_val.trace_add(
            "write",
            lambda *args: self.entry_change_hook(
                choices_dict['short_name'], short_name,
                short_name_val, *args
            )
        )
        del_b = tk.Button(
            good_f, text='Del good',
            command=lambda: self.del_good(good_f)
        )
        del_b.grid(column=2, row=0)
        short_name.grid(column=1, row=1)
        l = tk.Label(good_f, text='Price')
        l.grid(column=0, row=2)
        price_val = tk.StringVar()
        price = tk.Entry(
            good_f, textvariable=price_val
        )
        price.grid(column=0, row=3)
        l = tk.Label(good_f, text='Quantity')
        l.grid(column=1, row=2)
        quan_val = tk.StringVar()
        quan = tk.Entry(
            good_f, textvariable=quan_val
        )
        quan.grid(column=1, row=3)
        l = tk.Label(good_f, text='Cost')
        l.grid(column=2, row=2)
        cost_val = tk.StringVar()
        cost = tk.Entry(
            good_f, textvariable=cost_val
        )
        cost.grid(column=2, row=3)
        pack_f.good_row += 1

    def add_good(self, pack_f, choices_dict):
        self.create_good(pack_f, choices_dict)
        pack_f.children['new_good_b'].grid(column=2, row=pack_f.good_row+1)
        pack_f.children['total_l'].grid(column=0, row=pack_f.good_row)
        pack_f.children['total_e'].grid(column=0, row=pack_f.good_row+1)

    def del_good(self, good_f):
        good_f.destroy()

    def add_check(self):
        pass


class CLI():
    
    def __init__(self):
        pass

    def show_msg(self, *args, **kwargs):
        print(*args, **kwargs)

