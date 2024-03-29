from argparse import ArgumentParser
import tkinter as tk
from tkinter import ttk


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

    def submit_form(self, data):
        self.worker.process_form(data)

class GUI():
 
    def __init__(self, ui, choices_dict):
        self.ui = ui
        self.ui.front = self
        root = tk.Tk()
        root.minsize(600, 400)
        root.bind('<Button-1>', self.set_focus)
        ttk.Style().configure('TButton', wraplength=150,)
        self.create_form(root, choices_dict)
        root.mainloop()

    def show_msg(self, *args, **kwargs):
        print(*args, **kwargs)

    def set_focus(self, event):
        event.widget.focus_set()
        
    def create_form(self, root, choices_dict):
        form_a = ttk.Frame(root)
        form_a.pack()
        form_o = ttk.Frame(form_a, name='form_o')
        form_o.pack()
        root.update()
        form_c = tk.Canvas(form_o, name='form_c')
        form_f = ttk.Frame(form_c, name='form_f')
        form_s = ttk.Scrollbar(form_o, orient="vertical", command=form_c.yview)
        form_c.configure(yscrollcommand=form_s.set)
        self.sug_f = None
        form_s.pack(side="right", fill="y")
        form_c.pack(side="left", fill="both", expand=True)
        form_c.form_f_id = form_c.create_window(
            (0,0), window=form_f, anchor="nw"
        )
        form_f.bind(
            "<Configure>", 
            lambda event, canvas=form_c: self.form_f_conf(canvas)
        )
        root.bind(
            "<Configure>",
            lambda event, canvas=form_c, root=root: self.root_conf(canvas, root)
        )
        form_f.pack_row = 0
        self.create_entry_pack(
            form_f, choices_dict
        )
        new_check_b = ttk.Button(
            form_f, text='Add check', name='new_check_b',
            command=lambda: self.add_check(form_f, choices_dict)
        )
        new_check_b.grid(column=0, row=form_f.pack_row+1)
        subm_b = ttk.Button(
            form_a, text='Submit', 
            command=lambda: self.subm_form(form_f)
        )
        subm_b.pack()

    def create_entry_pack(self, parent, choices_dict):
        pack_f = ttk.Frame(parent, name='pack_'+str(parent.pack_row))
        pack_f.goods = []
        pack_f.grid(column=0, columnspan=2, row=parent.pack_row, pady=10)
        l = ttk.Label(pack_f, text='Datetime')
        l.grid(column=0, row=0)
        datetime = tk.Entry(pack_f, name='datetime')
        datetime.grid(column=0, row=1)
        l = ttk.Label(pack_f, text='Shop name')
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
        l = ttk.Label(pack_f, text='Shop address')
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
        l = ttk.Label(pack_f, text='Goods')
        l.grid(column=0, row=2)
        pack_f.good_row = 3
        self.create_good(pack_f, choices_dict)
        new_good_b = ttk.Button(
            pack_f, text='Add good', 
            command=lambda: self.add_good(pack_f, choices_dict),
            name='new_good_b'
        )
        new_good_b.grid(column=2, row=pack_f.good_row+1)
        l = ttk.Label(pack_f, text='Total', name='total_l')
        l.grid(column=0, row=pack_f.good_row)
        total_val = tk.StringVar()
        total = tk.Entry(
            pack_f, textvariable=total_val, name='total_e'
        )
        total.grid(column=0, row=pack_f.good_row+1)
        del_b = ttk.Button(
            pack_f, text='Del check', name='del_check_b',
            command=lambda: self.del_check(pack_f)
        )
        del_b.grid(column=1, row=pack_f.good_row+1)
        parent.pack_row += 1

    def entry_change_hook(self, choices_list, entry, entry_val, *args):
        if not entry_val.get() or self.sug_f:
            self.sug_f.destroy()
        val = entry_val.get()
        (x, y) = (entry.winfo_x(), entry.winfo_y()+entry.winfo_height())
        w = entry
        while True:
            w = w.master
            x += w.winfo_x()
            y += w.winfo_y() if w.winfo_y() > 0 else 0
            if w.master.winfo_name() == 'form_o':
                break
        self.sug_f = ttk.Frame(w.children['form_f'])
        self.sug_f.place(x=x, y=y)
        if val:
            for i in sorted(choices_list):
                if val.lower() in i.lower():
                    ttk.Button(
                        self.sug_f, text=i, width=17,
                        command=lambda x=i: self.change_val(x, entry_val)
                    ).pack()

    def change_val(self, i, entry_val):
        entry_val.set(i)
        self.sug_f.destroy()

    def create_good(self, pack_f, choices_dict):
        good_f = ttk.Frame(pack_f, name='good_'+str(pack_f.good_row-3))
        good_f.grid(column=0, columnspan=3, row=pack_f.good_row, pady=10)
        pack_f.goods.append(good_f)
        l = ttk.Label(good_f, text='Full name')
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
        l = ttk.Label(good_f, text='Short name')
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
        del_b = ttk.Button(
            good_f, text='Del good',
            command=lambda: self.del_good(good_f)
        )
        del_b.grid(column=2, row=0)
        short_name.grid(column=1, row=1)
        l = ttk.Label(good_f, text='Price')
        l.grid(column=0, row=2)
        price_val = tk.StringVar()
        price = tk.Entry(
            good_f, textvariable=price_val, name='price',
        )
        price.grid(column=0, row=3)
        l = ttk.Label(good_f, text='Quantity')
        l.grid(column=1, row=2)
        quan_val = tk.StringVar()
        quan = tk.Entry(
            good_f, textvariable=quan_val, name='quantity',
        )
        quan.grid(column=1, row=3)
        l = ttk.Label(good_f, text='Cost')
        l.grid(column=2, row=2)
        cost_val = tk.StringVar()
        cost = tk.Entry(
            good_f, textvariable=cost_val, name='cost',
        )
        cost.grid(column=2, row=3)
        pack_f.good_row += 1

    def add_good(self, parent, choices_dict):
        self.update_choices_good(parent, choices_dict)
        self.create_good(parent, choices_dict)
        parent.children['new_good_b'].grid_configure(row=parent.good_row+1)
        parent.children['total_l'].grid_configure(row=parent.good_row)
        parent.children['total_e'].grid_configure(row=parent.good_row+1)
        parent.children['del_check_b'].grid_configure(row=parent.good_row+1)

    def del_good(self, good_f):
        good_f.destroy()

    def add_check(self, parent, choices_dict):
        for i in parent.children.keys():
            if i.startswith('pack'):
                self.update_choices(
                    parent.children[i], choices_dict, 'shop_name'
                )
                self.update_choices(
                    parent.children[i], choices_dict, 'shop_addr'
                )
                self.update_choices_good(parent.children[i], choices_dict)
        self.create_entry_pack(parent, choices_dict)
        parent.children['new_check_b'].grid_configure(row=parent.pack_row+1)
        
    def update_choices(self, parent, choices_dict, entry):
        val = parent.children[entry].get()
        if val and val not in choices_dict[entry]:
            choices_dict[entry].append(val)

    def update_choices_good(self, parent, choices_dict):
        for i in parent.children.keys():
            if i.startswith('good'):
                self.update_choices(
                    parent.children[i], choices_dict, 'full_name'
                )
                self.update_choices(
                    parent.children[i], choices_dict, 'short_name'
                )

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
                            'price': self.floatify(
                                pack[n].children['price'].get()
                            ),
                            'quantity': self.floatify(
                                pack[n].children['quantity'].get()
                            ),
                            'cost': self.floatify(
                                pack[n].children['cost'].get()
                            ),
                        })
                pack = form_f.children[i]
                data.append({
                    'datetime': pack.children['datetime'].get(),
                    'shop_name': pack.children['shop_name'].get(),
                    'shop_addr': pack.children['shop_addr'].get(),
                    'goods': goods,
                    'total': self.floatify(
                        pack.children['total_e'].get()
                    ),
                })
        self.ui.submit_form(data)

    def form_f_conf(self, canvas):
        canvas.configure(scrollregion=canvas.bbox("all"))
        
    def root_conf(self, canvas, root):
        canvas.configure(
            height=root.winfo_height()-50, width=root.winfo_width()-80
        )
        '''
        canvas.itemconfigure(canvas.form_f_id, width=canvas.winfo_width())
        if (canvas.winfo_height() - int(canvas.itemcget(canvas.form_f_id, 'height'))) > 0:
            canvas.itemconfigure(canvas.form_f_id, height=canvas.winfo_height())
            print(1)
        else:
            canvas.itemconfigure(
                canvas.form_f_id,
                height=canvas.children['form_f'].winfo_height()
            )
            print(canvas.children['form_f'].winfo_height())
        canvas.configure(scrollregion=canvas.bbox("all"))
        '''

    def floatify(self, string):
        try:
            return(float(string.replace(',', '.')))
        except ValueError:
            return(string)


class CLI():
    
    def __init__(self, ui, choices_dict):
        self.ui = ui
        self.ui.front = self

    def show_msg(self, *args, **kwargs):
        print(*args, **kwargs)

