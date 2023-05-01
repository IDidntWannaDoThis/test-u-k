import tkinter as tk
from tkinter import ttk

from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import Column, String, Integer,Float
from sqlalchemy import create_engine
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, update, delete


Database = 'sqlite:///../data/thesqldata.db'
Base = declarative_base()


class Box(Base):
    # this class declaration does 2 important things at once:
    # 1. as usual, it declares a class we can store data in, inside our python program.
    # 2. it creates a table in a sql database with the specified columns
    __tablename__ = "box"
    id = Column(Integer, primary_key=True)
    weight = Column(Integer)
    destination = Column(String)

    def convert_from_tuple(tuple_):  # Convert tuple to Container
        container = Box(id=tuple_[0], weight=tuple_[1], destination=tuple_[2])
        return container

    def __repr__(self):  # Only for testing/debugging purposes.
        return f"{self.id}  {self.weight}  {self.destination}"

class Aircraft(Base):
        # this class declaration does 2 important things at once:
        # 1. as usual, it declares a class we can store data in, inside our python program.
        # 2. it creates a table in a sql database with the specified columns
    __tablename__ = "Aircraft2"
    id = Column(Integer, primary_key=True)
    maxcargo = Column(Integer)
    registration = Column(Integer)

    def convert_from_tuple(tuple_):  # Convert tuple to Container
        container = Aircraft(id=tuple_[0], weight=tuple_[1], destination=tuple_[2])
        return container

    def __repr__(self):  # Only for testing/debugging purposes.
        return f"{self.id}  {self.maxcargo}  {self.registration}"

class Route(Base):

    # this class declaration does 2 important things at once:
    # 1. as usual, it declares a class we can store data in, inside our python program.
    # 2. it creates a table in a sql database with the specified columns
    __tablename__ = "route2"
    id = Column(Integer, primary_key=True)
    data = Column(Integer)
    airid = Column(Integer)
    conid = Column(Integer)

    def convert_from_tuple(tuple_):  # Convert tuple to Container
        container = Route(id=tuple_[0], weight=tuple_[1], destination=tuple_[2])
        return container

    def __repr__(self):  # Only for testing/debugging purposes.
        return f"{self.id} {self.data}  {self.airid}  {self.conid}"

def create_data(data):  # Optional. Used to test data base functions before gui is ready.
    with Session(engine) as session:
        new_items = []
        new_items.append(data)
        session.add_all(new_items)
        session.commit()


def select_all(classparam):  # https://docs.sqlalchemy.org/en/14/tutorial/data_select.html
    # return a list of all records in classparams table
    with Session(engine) as session:
        records = session.scalars(select(classparam))  # in the background this creates the sql query "select * from persons" when called with classparam=Person
        result = []
        for record in records:  # convert the query result into a list of records
            result.append(record)
    return result


engine = create_engine(Database, echo=False, future=True)  # define engine
Base.metadata.create_all(engine)

test_data_list = []
def empty_entry():
    print("button_1 was pressed")
    entry_1.delete(0, tk.END)
    entry_2.delete(0, tk.END)
    entry_3.delete(0, tk.END)
    entry_4.delete(0, tk.END)

    entry2_1.delete(0, tk.END)
    entry2_2.delete(0, tk.END)
    entry2_3.delete(0, tk.END)

    entry3_1.delete(0, tk.END)
    entry3_2.delete(0, tk.END)
    entry3_3.delete(0, tk.END)
    entry3_4.delete(0, tk.END)

def add_box():
    create_data(Box(id=entry_1.get(), weight=entry_2.get(), destination=entry_3.get()))

def add_craft():
    create_data(Aircraft(id=entry2_1.get(), maxcargo=entry2_2.get(), registration=entry2_3.get()))

def add_Route():
    create_data(Route(id=entry3_1.get(), data=entry3_2.get(), airid=entry3_3.get(), conid=entry3_4.get()))

def read_box():
    count = 0
    tree_1.delete(*tree_1.get_children())
    for record in select_all(Box):
        if count % 2 == 0:  # even
            tree_1.insert(parent='', index='end', text='', values=record, tags=('evenrow',))
        else:  # odd
            tree_1.insert(parent='', index='end', text='', values=record, tags=('oddrow',))
        count += 1
def read_craft():
    count = 0
    tree2_1.delete(*tree2_1.get_children())
    for record in select_all(Aircraft):
        if count % 2 == 0:  # even
            tree2_1.insert(parent='', index='end', text='', values=record, tags=('evenrow',))
        else:  # odd
            tree2_1.insert(parent='', index='end', text='', values=record, tags=('oddrow',))
        count += 1



def delete_hard_container():
    index_selected = tree_1.focus()  # Index of selected tuple
    values = tree_1.item(index_selected,'values')  # Values of selected tuple  # Fill entry boxes
    container = Box.convert_from_tuple(values)

    # delete a record in the container table
    with Session(engine) as session:
        session.execute(delete(Box).where(Box.id == container.id))
        session.commit()
def clear_container_entries():  # Clear entry boxes
    entry_1.delete(0, tk.END)  # Delete text in entry box, beginning with the first character (0) and ending with the last character (tk.END)
    entry_2.delete(0, tk.END)
    entry_3.delete(0, tk.END)
    entry_4.delete(0, tk.END)

def delete_hard_craft():
    index_selected = tree_1.focus()  # Index of selected tuple
    values = tree_1.item(index_selected, 'values')  # Values of selected tuple  # Fill entry boxes
    container = Aircraft.convert_from_tuple(values)
    # delete a record in the container table
    with Session(engine) as session:
        session.execute(delete(Aircraft).where(Aircraft.id == container.id))
        session.commit()

def delete_hard_route():
    index_selected = tree_1.focus()  # Index of selected tuple
    values = tree_1.item(index_selected, 'values')  # Values of selected tuple  # Fill entry boxes
    container = Route.convert_from_tuple(values)
    # delete a record in the container table
    with Session(engine) as session:
        session.execute(delete(Route).where(Route.id == container.id))
        session.commit()

def write_container_entries(values):  # Fill entry boxes
    entry_1.insert(0, values[0])
    entry_2.insert(0, values[1])
    entry_3.insert(0, values[2])

def write_route_entries(values):  # Fill entry boxes
    entry3_1.insert(0, values[0])
    entry3_2.insert(0, values[1])
    entry3_3.insert(0, values[2])

def write_craft_entries(values):  # Fill entry boxes
    entry2_1.insert(0, values[0])
    entry2_2.insert(0, values[1])
    entry2_3.insert(0, values[2])

def read_route():
    count = 0
    tree3_1.delete(*tree3_1.get_children())
    for record in select_all(Route):
        if count % 2 == 0:  # even
            tree3_1.insert(parent='', index='end', text='', values=record, tags=('evenrow',))
        else:  # odd
            tree3_1.insert(parent='', index='end', text='', values=record, tags=('oddrow',))
        count += 1

def update_box(tree, record):  # update tuple in database
    container = Box.convert_from_tuple(record)  # Convert tuple to Container
    update_container(container)  # Update database
    clear_container_entries()  # Clear entry boxes
    refresh_treeview(tree, Box)  # Refresh treeview table
def update_craft(tree, record):  # update tuple in database
    container = Aircraft.convert_from_tuple(record)  # Convert tuple to Container
    update_container(container)  # Update database
    clear_craft_entries()  # Clear entry boxes
    refresh_treeview(tree, Aircraft)  # Refresh treeview table

def update_route(tree, record):  # update tuple in database
    container = Route.convert_from_tuple(record)  # Convert tuple to Container
    update_container(container)  # Update database
    clear_route_entries()  # Clear entry boxes
    refresh_treeview(tree, Route)  # Refresh treeview table



padx = 8
pady = 5
rowheight = 24  # rowheight in treeview
treeview_background = "#eeeeee"  # color of background in treeview
treeview_foreground = "black"  # color of foreground in treeview
treeview_selected = "#773333"


main_window = tk.Tk()
main_window.title('my first GUI')

container = tk.LabelFrame(main_window, text="container")
container.grid(row=0, column=0, sticky=tk.N)

containerp1 = tk.Frame(container,)
containerp1.grid(row=0, column=0, sticky=tk.N)

style = ttk.Style()  # Add style
style.theme_use('default')  # Pick theme
style.configure("Treeview", background=treeview_background, foreground=treeview_foreground, rowheight=rowheight, fieldbackground=treeview_background)
style.map('Treeview', background=[('selected', treeview_selected)])

tree_1_scrollbar = tk.Scrollbar(containerp1)  # create a scrollbar and a treeview
tree_1_scrollbar.grid(row=0, column=2, sticky='ns')
tree_1 = ttk.Treeview(containerp1, yscrollcommand=tree_1_scrollbar.set, selectmode="browse")
tree_1.grid(row=0, column=0, padx=0, pady=pady)
tree_1_scrollbar.config(command=tree_1.yview)

tree_1['columns'] = ("col1", "col2", "col3")  # Define treeview columns
tree_1.column("#0", width=0, stretch=tk.NO)
tree_1.column("col1", anchor=tk.E, width=40)
tree_1.column("col2", anchor=tk.W, width=90)
tree_1.column("col3", anchor=tk.W, width=180)

tree_1.heading("#0", text="", anchor=tk.W) # Create treeview column headings
tree_1.heading("col1", text="id", anchor=tk.CENTER)
tree_1.heading("col2", text="weight", anchor=tk.CENTER)
tree_1.heading("col3", text="destination", anchor=tk.CENTER)

containerp2 = tk.Frame(container,)
containerp2.grid(row=1, column=0, sticky=tk.N)

label_1 = tk.Label(containerp2, text="id")
label_1.grid(row=0, column=0, padx=padx, pady=pady)

label_2 = tk.Label(containerp2, text="weight")
label_2.grid(row=0, column=1, padx=padx, pady=pady)

label_3 = tk.Label(containerp2, text="destination")
label_3.grid(row=0, column=2, padx=padx, pady=pady)

label_4 = tk.Label(containerp2, text="weather")
label_4.grid(row=0, column=3, padx=padx, pady=pady)

entry_1 = tk.Entry(containerp2, width=4)
entry_1.grid(row=1, column=0, padx=padx, pady=pady)

entry_2 = tk.Entry(containerp2, width=8)
entry_2.grid(row=1, column=1, padx=padx, pady=pady)

entry_3 = tk.Entry(containerp2)
entry_3.grid(row=1, column=2, padx=padx, pady=pady)

entry_4 = tk.Entry(containerp2,width=15)
entry_4.grid(row=1, column=3, padx=padx, pady=pady)

containerp3 = tk.Frame(container,)
containerp3.grid(row=2, column=0, sticky=tk.N)

button_1 = tk.Button(containerp3, text="create", command=add_box)  # create a button
button_1.grid(row=2, column=0, padx=padx, pady=pady)

button_2 = tk.Button(containerp3, text="update", command=read_box)  # create a button
button_2.grid(row=2, column=1, padx=padx, pady=pady)

button_3 = tk.Button(containerp3, text="delete", command=delete_hard_container)  # create a button
button_3.grid(row=2, column=2, padx=padx, pady=pady)

button_4 = tk.Button(containerp3, text="clear entry boxes", command=empty_entry)  # create a button
button_4.grid(row=2, column=3, padx=padx, pady=pady)





container2 = tk.LabelFrame(main_window, text="aircraft")
container2.grid(row=0, column=1, sticky=tk.N)

container2p1 = tk.Frame(container2,)
container2p1.grid(row=0, column=0, sticky=tk.N)

tree2_1_scrollbar = tk.Scrollbar(container2p1)  # create a scrollbar and a treeview
tree2_1_scrollbar.grid(row=0, column=2, sticky='ns')
tree2_1 = ttk.Treeview(container2p1, yscrollcommand=tree2_1_scrollbar.set, selectmode="browse")
tree2_1.grid(row=0, column=0, padx=0, pady=pady)
tree2_1_scrollbar.config(command=tree2_1.yview)

tree2_1['columns'] = ("col1", "col2", "col3")  # Define treeview columns
tree2_1.column("#0", width=0, stretch=tk.NO)
tree2_1.column("col1", anchor=tk.E, width=40)
tree2_1.column("col2", anchor=tk.W, width=90)
tree2_1.column("col3", anchor=tk.W, width=90)

tree2_1.heading("#0", text="", anchor=tk.W) # Create treeview column headings
tree2_1.heading("col1", text="id", anchor=tk.CENTER)
tree2_1.heading("col2", text="max.carg.wgt.", anchor=tk.CENTER)
tree2_1.heading("col3", text="registration", anchor=tk.CENTER)

container2p2 = tk.Frame(container2,)
container2p2.grid(row=1, column=0, sticky=tk.N)

label2_1 = tk.Label(container2p2, text="id")
label2_1.grid(row=0, column=0, padx=padx, pady=pady)

label2_2 = tk.Label(container2p2, text="maxcargo")
label2_2.grid(row=0, column=1, padx=padx, pady=pady)

label2_3 = tk.Label(container2p2, text="registration")
label2_3.grid(row=0, column=2, padx=padx, pady=pady)

entry2_1 = tk.Entry(container2p2, width=4)
entry2_1.grid(row=1, column=0, padx=padx, pady=pady)

entry2_2 = tk.Entry(container2p2, width=8)
entry2_2.grid(row=1, column=1, padx=padx, pady=pady)

entry2_3 = tk.Entry(container2p2, width=8)
entry2_3.grid(row=1, column=2, padx=padx, pady=pady)

container2p3 = tk.Frame(container2,)
container2p3.grid(row=2, column=0, sticky=tk.N)

button2_1 = tk.Button(container2p3, text="create", command=add_craft)  # create a button
button2_1.grid(row=2, column=0, padx=padx, pady=pady)

button2_2 = tk.Button(container2p3, text="update", command=read_craft)  # create a button
button2_2.grid(row=2, column=1, padx=padx, pady=pady)

button2_3 = tk.Button(container2p3, text="delete", command=delete_hard_craft)  # create a button
button2_3.grid(row=2, column=2, padx=padx, pady=pady)



container3 = tk.LabelFrame(main_window, text="container")
container3.grid(row=0, column=2, sticky=tk.N)

container3p1 = tk.Frame(container3,)
container3p1.grid(row=0, column=0, sticky=tk.N)

style = ttk.Style()  # Add style
style.theme_use('default')  # Pick theme
style.configure("Treeview", background=treeview_background, foreground=treeview_foreground, rowheight=rowheight, fieldbackground=treeview_background)
style.map('Treeview', background=[('selected', treeview_selected)])

tree3_1_scrollbar = tk.Scrollbar(container3p1)  # create a scrollbar and a treeview
tree3_1_scrollbar.grid(row=0, column=2, sticky='ns')
tree3_1 = ttk.Treeview(container3p1, yscrollcommand=tree3_1_scrollbar.set, selectmode="browse")
tree3_1.grid(row=0, column=0, padx=0, pady=pady)
tree3_1_scrollbar.config(command=tree3_1.yview)

tree3_1['columns'] = ("col1", "col2", "col3","col4")  # Define treeview columns
tree3_1.column("#0", width=0, stretch=tk.NO)
tree3_1.column("col1", anchor=tk.E, width=40)
tree3_1.column("col2", anchor=tk.W, width=60)
tree3_1.column("col3", anchor=tk.W, width=60)
tree3_1.column("col4", anchor=tk.W, width=60)


tree3_1.heading("#0", text="", anchor=tk.W) # Create treeview column headings
tree3_1.heading("col1", text="id", anchor=tk.CENTER)
tree3_1.heading("col2", text="date", anchor=tk.CENTER)
tree3_1.heading("col3", text="Container Id", anchor=tk.CENTER)
tree3_1.heading("col4", text="Aircraft Id", anchor=tk.CENTER)

container3p2 = tk.Frame(container3,)
container3p2.grid(row=1, column=0, sticky=tk.N)

label3_1 = tk.Label(container3p2, text="id")
label3_1.grid(row=0, column=0, padx=padx, pady=pady)

label3_2 = tk.Label(container3p2, text="date")
label3_2.grid(row=0, column=1, padx=padx, pady=pady)

label3_3 = tk.Label(container3p2, text="Container Id")
label3_3.grid(row=0, column=2, padx=padx, pady=pady)

label3_4 = tk.Label(container3p2, text="Aircraft Id")
label3_4.grid(row=0, column=3, padx=padx, pady=pady)

entry3_1 = tk.Entry(container3p2, width=4)
entry3_1.grid(row=1, column=0, padx=padx, pady=pady)

entry3_2 = tk.Entry(container3p2,width=10)
entry3_2.grid(row=1, column=1, padx=padx, pady=pady)

entry3_3 = tk.Entry(container3p2,width=4)
entry3_3.grid(row=1, column=2, padx=padx, pady=pady)

entry3_4 = tk.Entry(container3p2,width=4)
entry3_4.grid(row=1, column=3, padx=padx, pady=pady)

container3p3 = tk.Frame(container3,)
container3p3.grid(row=2, column=0, sticky=tk.N)

button3_1 = tk.Button(container3p3, text="create", command=add_Route)  # create a button
button3_1.grid(row=2, column=0, padx=padx, pady=pady)

button3_2 = tk.Button(container3p3, text="update", command=read_route)  # create a button
button3_2.grid(row=2, column=1, padx=padx, pady=pady)

button3_3 = tk.Button(container3p3, text="delete", command=delete_hard_route)  # create a button
button3_3.grid(row=2, column=2, padx=padx, pady=pady)

button3_4 = tk.Button(container3p3, text="clear entry boxes", command=empty_entry)  # create a button
button3_4.grid(row=2, column=3, padx=padx, pady=pady)


if __name__ == "__main__":
    main_window.mainloop()