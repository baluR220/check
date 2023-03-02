from argparse import ArgumentParser
import tkinter as tk


class UI():

    def __init__(self, **kwargs):
        self.args = self.get_args()
        self.gui = self.cli = None
        self.worker = kwargs['worker']
        self.worker.ui = kwargs['ui'] = self
        if self.args.gui:
            GUI(kwargs['ui'], kwargs['choices_dict'])
        else:
            CLI(kwargs['ui'], kwargs['choices_dict'])

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

    def submit_data(self, data):
        self.worker.process_data(data)

class GUI():
 
    def __init__(self, ui, choices_dict):
        self.ui = ui
        self.ui.front = self
        root = tk.Tk()
        self.root = root
        root.geometry("800x700",)
        root.bind('<Button-1>', self.set_focus)
        root.resizable(False, False)
        form_o = tk.Frame(root)
        form_o.pack()
        form_c = tk.Canvas(form_o, width=520, height=650)
        form_f = tk.Frame(form_c)
        form_s = tk.Scrollbar(form_o, orient="vertical", command=form_c.yview)
        form_c.configure(yscrollcommand=form_s.set)
        sug_f = tk.Frame(form_o, width=80)
        sug_f.pack(side="left")
        self.sug_f = sug_f
        form_s.pack(side="right", fill="y")
        form_c.pack(side="left", fill="both", expand=True)
        form_c.create_window((4,4), window=form_f, anchor="nw")

        form_f.bind(
            "<Configure>", 
            lambda event, canvas=form_c: self.form_f_conf(canvas)
        )
        form_f.pack_row = 0
        self.create_entry_pack(
            form_f, choices_dict
        )
        new_check_b = tk.Button(
            form_f, text='Add check', name='new_check_b',
            command=lambda: self.add_check(form_f, choices_dict)
        )
        new_check_b.grid(column=0, row=form_f.pack_row+1)
        subm_b = tk.Button(
            root, text='Submit', 
            command=lambda: self.subm_form(form_f)
        )
        subm_b.pack()
        root.mainloop()

    def show_msg(self, *args, **kwargs):
        print(*args, **kwargs)

    def set_focus(self, event):
        event.widget.focus_set()

    def create_entry_pack(self, parent, choices_dict):
        pack_f = tk.Frame(parent, name='pack_'+str(parent.pack_row))
        pack_f.goods = []
        pack_f.grid(column=0, columnspan=2, row=parent.pack_row, pady=10)
        l = tk.Label(pack_f, text='Datetime')
        l.grid(column=0, row=0)
        datetime = tk.Entry(pack_f, name='datetime')
        datetime.grid(column=0, row=1)
        l = tk.Label(pack_f, text='Shop name')
        l.grid(column=1, row=0)
        shop_name_val = tk.StringVar()
        shop_name = tk.Entry(
            pack_f, textvariable=shop_name_val, name='shop_name',
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
            pack_f, textvariable=shop_addr_val, name='shop_addr',
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
        l.grid(column=0, row=2)
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
        del_b = tk.Button(
            pack_f, text='Del check',
            command=lambda: self.del_check(pack_f)
        )
        del_b.grid(column=1, row=pack_f.good_row+1)
        parent.pack_row += 1

    def entry_change_hook(self, choices_list, entry, entry_val, *args):
        if not entry_val.get() or self.sug_f:
            for i in self.sug_f.winfo_children():
                i.destroy()
        val = entry_val.get()
        if val:
            for i in sorted(choices_list):
                if val in i:
                    tk.Button(
                        self.sug_f, text=i[:20], width=17,
                        command=lambda x=i: self.change_val(x, entry_val)
                    ).pack()

    def change_val(self, i, entry_val):
        entry_val.set(i)
        for i in self.sug_f.winfo_children():
            i.destroy()

    def create_good(self, pack_f, choices_dict):
        good_f = tk.Frame(pack_f, name='good_'+str(pack_f.good_row-3))
        good_f.grid(column=0, columnspan=3, row=pack_f.good_row, pady=10)
        pack_f.goods.append(good_f)
        l = tk.Label(good_f, text='Full name')
        l.grid(column=0, row=0)
        full_name_val = tk.StringVar()
        full_name = tk.Entry(
            good_f, textvariable=full_name_val, name='full_name',
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
            good_f, textvariable=short_name_val, name='short_name',
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
            good_f, textvariable=price_val, name='price',
        )
        price.grid(column=0, row=3)
        l = tk.Label(good_f, text='Quantity')
        l.grid(column=1, row=2)
        quan_val = tk.StringVar()
        quan = tk.Entry(
            good_f, textvariable=quan_val, name='quantity',
        )
        quan.grid(column=1, row=3)
        l = tk.Label(good_f, text='Cost')
        l.grid(column=2, row=2)
        cost_val = tk.StringVar()
        cost = tk.Entry(
            good_f, textvariable=cost_val, name='cost',
        )
        cost.grid(column=2, row=3)
        pack_f.good_row += 1

    def add_good(self, parent, choices_dict):
        for i in parent.children.keys():
            if i.startswith('good'):
                full_c = parent.children[i].children['full_name'].get()
                if full_c and full_c not in choices_dict['full_name']:
                    choices_dict['full_name'].append(full_c)
                short_c = parent.children[i].children['short_name'].get()
                if short_c and short_c not in choices_dict['short_name']:
                    choices_dict['short_name'].append(short_c)
        self.create_good(parent, choices_dict)
        parent.children['new_good_b'].grid_configure(row=parent.good_row+1)
        parent.children['total_l'].grid_configure(row=parent.good_row)
        parent.children['total_e'].grid_configure(row=parent.good_row+1)

    def del_good(self, good_f):
        good_f.destroy()

    def add_check(self, parent, choices_dict):
        for i in parent.children.keys():
            if i.startswith('pack'):
                name_c = parent.children[i].children['shop_name'].get()
                if name_c and name_c not in choices_dict['shop_name']:
                    choices_dict['shop_name'].append(name_c)
                addr_c = parent.children[i].children['shop_addr'].get()
                if addr_c and addr_c not in choices_dict['shop_addr']:
                    choices_dict['shop_addr'].append(addr_c)
        self.create_entry_pack(parent, choices_dict)
        parent.children['new_check_b'].grid_configure(row=parent.pack_row+1)
        
    def del_check(self, pack_f):
        pack_f.destroy()

    def subm_form(self, form_f):
        data = []
        for i in form_f.children.keys():
            if i.startswith('pack'):
                pack = form_f.children[i].children
                goods = []
                for n in pack.keys():
                    if n.startswith('good'):
                        goods.append({
                            'full_name': pack[n].children['full_name'].get(),
                            'short_name': pack[n].children['short_name'].get(),
                            'price': pack[n].children['price'].get(),
                            'quantity': pack[n].children['quantity'].get(),
                            'cost': pack[n].children['cost'].get(),
                        })
                pack = form_f.children[i]
                data.append({
                    'datetime': pack.children['datetime'].get(),
                    'shop_name': pack.children['shop_name'].get(),
                    'shop_addr': pack.children['shop_addr'].get(),
                    'goods': goods,
                    'total': pack.children['total_e'].get(),
                })
        self.ui.submit_data(data)

    def form_f_conf(self, canvas):
        canvas.configure(scrollregion=canvas.bbox("all"))


class CLI():
    
    def __init__(self, ui, choices_dict):
        self.ui = ui
        self.ui.front = self

    def show_msg(self, *args, **kwargs):
        print(*args, **kwargs)

