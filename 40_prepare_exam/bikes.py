
import tkinter as tk
from tkinter import ttk, messagebox

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, Date
from dateutil import parser
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, extract,event
from datetime import date
from sqlalchemy.engine import Engine

Database = 'sqlite:///../bakes.db'
Base = declarative_base()  # creating the registry and declarative base classes - combined into one step. Base will serve as the base class for the ORM mapped classes we declare.
# region global constants
padx = 8  # Horizontal distance to neighboring objects
pady = 4  # Vertical distance to neighboring objects
rowheight = 24  # rowheight in treeview
treeview_background = "#eeeeee"  # color of background in treeview
treeview_foreground = "black"  # color of foreground in treeview
treeview_selected = "#206030"  # color of selected row in treeview
oddrow = "#dddddd"  # color of odd row in treeview
evenrow = "#cccccc"  # color of even row in treeview
# endregion global constants

class Team(Base):
    __tablename__ = "team"
    id = Column(Integer, primary_key=True)
    skill = Column(Integer)
    size = Column(Integer)

    def __repr__(self):  # Optional. Only for test purposes.
        return f"{self.id}    {self.skill}    {self.size}"

    def convert_to_tuple(self):  # Convert Container to tuple
        return self.id, self.skill, self.size

    def valid(self):
        try:
            value = int(self.weight)
        except ValueError:
            return False
        return value >= 0

    @staticmethod
    def convert_from_tuple(tuple_):  # Convert tuple to Container
        container = Team(id=tuple_[0], skill=tuple_[1], size=tuple_[2])
        return container


class Route(Base):
    __tablename__ = "route"
    id = Column(Integer, primary_key=True)
    max_capacity = Column(Integer)
    difficulty = Column(Integer)

    def __repr__(self):  # Optional. Only for test purposes.
        return f"{self.id}   {self.max_capacity}  {self.difficulty}"

    def convert_to_tuple(self):  # Convert aircraft to tuple
        return self.id, self.max_capacity, self.difficulty

    def valid(self):
        try:
            value = int(self.max_capacity)
        except ValueError:
            return False
        return value >= 0

    @staticmethod
    def convert_from_tuple(tuple_):  # Convert tuple to aircraft
        try:
            # if tuple_[0] != '':  # unnecessary precaution
            #     id_ = int(tuple_[0])
            # else:
            #     id_ = 0
            hardness = int(tuple_[2])
            max_cargo_weight = int(tuple_[1])

            aircraft = Route(id=tuple_[0], max_capacity=max_cargo_weight, difficulty=tuple_[2])
            # aircraft = Aircraft(id=id_, max_cargo_weight=max_cargo_weight, registration=tuple_[2])
            return aircraft
        except:
            messagebox.showwarning("", "Entries could not be converted to route!")


class Booking(Base):
    __tablename__ = "transport"
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    team_id = Column(Integer, ForeignKey("Team.id"), nullable=False)
    route_id = Column(Integer, ForeignKey("Route.id"), nullable=False)

    def __repr__(self):  # Optional. Only for test purposes.
        return f"{self.id} {self.date} {self.team_id} {self.route_id}"

    def convert_to_tuple(self):  # Convert transport to tuple
        return self.id, self.date, self.team_id, self.route_id

    def valid(self):
        try:
            value = int(self.team_id)
        except ValueError:
            return False
        return value >= 0

    @staticmethod
    def convert_from_tuple(tuple_):  # Convert tuple to transport
        try:
            if tuple_[0] != '':  # unnecessary precaution?
                id_ = int(tuple_[0])
            else:
                id_ = 0
            date = parser.parse(tuple_[1])
            container_id = int(tuple_[2])
            aircraft_id = int(tuple_[3])
            # transport = Transport(id=tuple_[0], date=date, container_id=tuple_[2], aircraft_id=tuple_[3])  # unnecessary precaution?
            transport = Booking(id=id_, date=date, team_id=container_id, route_id=aircraft_id)
            return transport
        except:
            messagebox.showwarning("", "Entries could not be converted to transport!")


def get_record(classparam, record_id):  # https://docs.sqlalchemy.org/en/14/tutorial/data_select.html
    # return the record in classparams table with a certain id
    with Session(Engine) as session:
        record = session.scalars(select(classparam).where(classparam.id == record_id)).first()  # very useful for converting into our data class
    return record

def booked_cargo(aircraft, date_):
    # returns the already booked cargo on an aircraft at a certain date
    with Session(Engine) as session:
        records = session.scalars(select(Booking).where(Booking.route_id == aircraft.id).where(extract('day', Booking.date) == date_.day).where(extract('month', Booking.date) == date_.month).where(extract('year', Booking.date) == date_.year))
        weight = 0
        for record in records:
            weight += get_record(Team, record.team_id).weight
    return weight


def find_destination(aircraft, date_):
    # return an aircraft's destination at a certain date in the transport table
    with Session(Engine) as session:
        records = session.scalars(select(Booking).where(Booking.team_id_id == aircraft.id).where(extract('day', Booking.date) == date_.day).where(extract('month', Booking.date) == date_.month).where(extract('year', Booking.date) == date_.year))
        for record in records:
            return get_record(Team, record.team_id).destination
        return None


def capacity_available(aircraft, date_, new_container):
    # do the already booked cargo plus the new container weigh less than the aircraft's maximum cargo weight?
    booked = booked_cargo(aircraft, date_)
    # print(f'{aircraft.max_cargo_weight=} {booked=} {new_container.weight=}')
    return aircraft.max_capacity >= booked + new_container.size


def max_one_destination(aircraft, date_, new_container):
    # is the aircraft's destination at a certain date identical to the new container's destination?
    destination = find_destination(aircraft, date_)
    return destination is None or destination == new_container.id  # returns also True if aircraft had no destination yet

def delete_hard_container(container):
    # delete a record in the container table
    with Session(Engine) as session:
        session.execute(delete(Team).where(Team.id == container.id))
        session.commit()  # makes changes permanent in database


def delete_soft_container(container):
    # soft delete a record in the container table by setting its weight to -1 (see also method "valid" in the container class)
    with Session(Engine) as session:
        session.execute(update(Team).where(Team.id == container.id).values(weight=-1, destination=container.destination))
        session.commit()  # makes changes permanent in database
# endregion container


def create_record(record):  # https://docs.sqlalchemy.org/en/14/tutorial/orm_data_manipulation.html#orm-enabled-update-statements
    # create a record in the database
    with Session(Engine) as session:
        record.id = None
        session.add(record)
        session.commit()  # makes changes permanent in database


def read_container_entries():  # Read content of entry boxes
    return entry_container_id.get(), entry_container_weight.get(), entry_container_destination.get(),


def clear_container_entries():  # Clear entry boxes
    entry_container_id.delete(0, tk.END)  # Delete text in entry box, beginning with the first character (0) and ending with the last character (tk.END)
    entry_container_weight.delete(0, tk.END)
    entry_container_destination.delete(0, tk.END)

def write_container_entries(values):  # Fill entry boxes
    entry_container_id.insert(0, values[0])
    entry_container_weight.insert(0, values[1])
    entry_container_destination.insert(0, values[2])


def edit_container(event, tree):  # Copy selected tuple into entry boxes. Parameter event is mandatory but we don't use it.
    index_selected = tree.focus()  # Index of selected tuple
    values = tree.item(index_selected, 'values')  # Values of selected tuple
    clear_container_entries()  # Clear entry boxes
    write_container_entries(values)  # Fill entry boxes


def create_container(tree, record):  # add new tuple to database
    container = Team.convert_from_tuple(record)  # Convert tuple to Container
    create_record(container)  # Update database
    clear_container_entries()  # Clear entry boxes
    refresh_treeview(tree, Team)  # Refresh treeview table


def update_container(tree, record):  # update tuple in database
    container = Team.convert_from_tuple(record)  # Convert tuple to Container
    update_container(container)  # Update database
    clear_container_entries()  # Clear entry boxes
    refresh_treeview(tree, Team)  # Refresh treeview table

def delete_container(tree, record):  # delete tuple in database
    container = Team.convert_from_tuple(record)  # Convert tuple to Container
    delete_soft_container(container)  # Update database
    clear_container_entries()  # Clear entry boxes
    refresh_treeview(tree, Team)  # Refresh treeview table

def update_aircraft(aircraft):  # https://docs.sqlalchemy.org/en/14/tutorial/orm_data_manipulation.html#orm-enabled-update-statements
    # update a record in the aircraft table
    with Session(Engine) as session:
        session.execute(update(Route).where(Route.id == aircraft.id).values(max_capacity=aircraft.max_cargo_weight, registration=aircraft.registration))
        session.commit()  # makes changes permanent in database


def delete_hard_aircraft(aircraft):
    # delete a record in the aircraft table
    with Session(Engine) as session:
        session.execute(delete(Route).where(Route.id == aircraft.id))
        session.commit()  # makes changes permanent in database


def delete_soft_aircraft(aircraft):
    # soft delete a record in the aircraft table by setting its max_cargo_weight to -1 (see also method "valid" in the aircraft class)
    with Session(Engine) as session:
        session.execute(update(Route).where(Route.id == aircraft.id).values(max_Capacity=-1, registration=aircraft.registration))
        session.commit()  # makes changes permanent in database
# endregion aircraft


# def copy_container_id(event):  #
#     entry_transport_container_id.delete(0, tk.END)
#     entry_transport_container_id.insert(0, entry_container_id.get())
# endregion container functions


# region aircraft functions
def read_aircraft_entries():  # Read content of entry boxes
    return entry_aircraft_id.get(), entry_aircraft_max_cargo_weight.get(), entry_aircraft_registration.get(),


def clear_aircraft_entries():  # Clear entry boxes
    entry_aircraft_id.delete(0, tk.END)  # Delete text in entry box, beginning with the first character (0) and ending with the last character (tk.END)
    entry_aircraft_max_cargo_weight.delete(0, tk.END)
    entry_aircraft_registration.delete(0, tk.END)


def write_aircraft_entries(values):  # Fill entry boxes
    entry_aircraft_id.insert(0, values[0])
    entry_aircraft_max_cargo_weight.insert(0, values[1])
    entry_aircraft_registration.insert(0, values[2])


def edit_aircraft(event, tree):  # Copy selected tuple into entry boxes. Parameter event is mandatory but we don't use it.
    index_selected = tree.focus()  # Index of selected tuple
    values = tree.item(index_selected, 'values')  # Values of selected tuple
    clear_aircraft_entries()  # Clear entry boxes
    write_aircraft_entries(values)  # Fill entry boxes


def create_aircraft(tree, record):  # add new tuple to database
    aircraft = Route.convert_from_tuple(record)  # Convert tuple to Aircraft
    create_record(aircraft)  # Update database
    clear_aircraft_entries()  # Clear entry boxes
    refresh_treeview(tree, Route)  # Refresh treeview table


def update_aircraft(tree, record):  # update tuple in database
    aircraft = Route.convert_from_tuple(record)  # Convert tuple to Aircraft
    update_aircraft(aircraft)  # Update database
    clear_aircraft_entries()  # Clear entry boxes
    refresh_treeview(tree, Route)  # Refresh treeview table


def delete_aircraft(tree, record):  # delete tuple in database
    aircraft = Route.convert_from_tuple(record)  # Convert tuple to Aircraft
    delete_soft_aircraft(aircraft)  # Update database
    clear_aircraft_entries()  # Clear entry boxes
    refresh_treeview(tree, Route)  # Refresh treeview table


# def copy_aircraft_id(event):
#     entry_transport_aircraft_id.delete(0, tk.END)
#     entry_transport_aircraft_id.insert(0, entry_aircraft_id.get())
# endregion aircraft functions


# region transport functions
def read_transport_entries():  # Read content of entry boxes
    return entry_transport_id.get(), entry_transport_date.get(), entry_transport_container_id.get(), entry_transport_aircraft_id.get(),


def clear_transport_entries():  # Clear entry boxes
    entry_transport_id.delete(0, tk.END)  # Delete text in entry box, beginning with the first character (0) and ending with the last character (tk.END)
    entry_transport_date.delete(0, tk.END)
    entry_transport_container_id.delete(0, tk.END)
    entry_transport_aircraft_id.delete(0, tk.END)


def write_transport_entries(values):  # Fill entry boxes
    entry_transport_id.insert(0, values[0])
    entry_transport_date.insert(0, values[1])
    entry_transport_container_id.insert(0, values[2])
    entry_transport_aircraft_id.insert(0, values[3])


def edit_transport(event, tree):  # Copy selected tuple into entry boxes. Parameter event is mandatory but we don't use it.
    index_selected = tree.focus()  # Index of selected tuple
    values = tree.item(index_selected, 'values')  # Values of selected tuple
    clear_transport_entries()  # Clear entry
    # boxes
    write_transport_entries(values)  # Fill entry boxes


def create_transport(tree, record):  # add new tuple to database
    transport = Booking.convert_from_tuple(record)  # Convert tuple to Transport
    capacity_ok = capacity_available(get_record(Route, transport.route_id), transport.date, get_record(Team, transport.team_id))
    destination_ok = max_one_destination(get_record(Route, transport.route_id), transport.date, get_record(Team, transport.team_id))
    if destination_ok:
        if capacity_ok:
            create_record(transport)  # Update database
            clear_transport_entries()  # Clear entry boxes
            refresh_treeview(tree, Booking)  # Refresh treeview table
        else:
            # global INTERNAL_ERROR_CODE
            # INTERNAL_ERROR_CODE = 1
            messagebox.showwarning("", "Not enough capacity on aircraft!")
    else:
        messagebox.showwarning("", "Aircraft already has another destination!")


def update_transport(tree, record):  # update tuple in database
    transport = Booking.convert_from_tuple(record)  # Convert tuple to Transport
    capacity_ok = capacity_available(get_record(Route, transport.route_id), transport.date, get_record(Team, transport.team_id))
    destination_ok = max_one_destination(get_record(Route, transport.route_id), transport.date, get_record(Team, transport.team_id))
    if destination_ok:
        if capacity_ok:
            update_transport(transport)  # Update database
            clear_transport_entries()  # Clear entry boxes
            refresh_treeview(tree, Booking)  # Refresh treeview table
        else:
            # global INTERNAL_ERROR_CODE
            # INTERNAL_ERROR_CODE = 1
            messagebox.showwarning("", "Not enough capacity on aircraft!")
    else:
        messagebox.showwarning("", "Aircraft already has another destination!")


def delete_transport(tree, record):  # delete tuple in database
    transport = Booking.convert_from_tuple(record)  # Convert tuple to Transport
    delete_hard_transport(transport)  # Update database
    clear_transport_entries()  # Clear entry boxes
    refresh_treeview(tree, Booking)  # Refresh treeview table
# endregion transport functions
def update_transport(transport):  # https://docs.sqlalchemy.org/en/14/tutorial/orm_data_manipulation.html#orm-enabled-update-statements
    # update a record in the transport table
    with Session(Engine) as session:
        session.execute(update(Booking).where(Booking.id == transport.id).values(date=transport.date, Team_id=transport.Team_id, route_id=transport.route_id))
        session.commit()  # makes changes permanent in database


def delete_hard_transport(transport):
    # delete a record in the transport table
    with Session(Engine) as session:
        session.execute(delete(Booking).where(Booking.id == transport.id))
        session.commit()  # makes changes permanent in database
# endregion transport

def select_all(classparam):  # https://docs.sqlalchemy.org/en/14/tutorial/data_select.html
    # return a list of all records in classparams table
    with Session(Engine) as session: #xxx
        records = session.scalars(select(classparam))  # very useful for converting into our data class
        result = []
        for record in records:
            # print(record)
            result.append(record)
    return result

# region common functions
def read_table(tree, class_):  # fill tree from database
    count = 0  # Used to keep track of odd and even rows, because these will be colored differently.
    result = select_all(class_)  # Read all containers from database
    for record in result:
        if record.valid():  # this condition excludes soft deleted records from being shown in the data table
            if count % 2 == 0:  # even
                tree.insert(parent='', index='end', iid=str(count), text='', values=record.convert_to_tuple(), tags=('evenrow',))  # Insert one row into the data table
            else:  # odd
                tree.insert(parent='', index='end', iid=str(count), text='', values=record.convert_to_tuple(), tags=('oddrow',))  # Insert one row into the data table
            count += 1


def refresh_treeview(tree, class_):  # Refresh treeview table
    empty_treeview(tree)  # Clear treeview table
    read_table(tree, class_)  # Fill treeview from database


def empty_treeview(tree):  # Clear treeview table
    tree.delete(*tree.get_children())
# endregion common functions


# region common widgets
main_window = tk.Tk()  # Define the main window
main_window.title('AspIT S2: DanskCargo')  # Text shown in the top window bar
main_window.geometry("1200x500")  # window size

style = ttk.Style()  # Add style
style.theme_use('default')  # Pick theme

# Configure treeview colors and formatting. A treeview is an object that can contain a data table.
style.configure("Treeview", background=treeview_background, foreground=treeview_foreground, rowheight=rowheight, fieldbackground=treeview_background)
style.map('Treeview', background=[('selected', treeview_selected)])  # Define color of selected row in treeview
# endregion common widgets


# region container widgets
# Define Labelframe which contains all container related GUI objects (data table, labels, buttons, ...)
frame_container = tk.LabelFrame(main_window, text="Team")  # https://www.tutorialspoint.com/python/tk_labelframe.htm
frame_container.grid(row=0, column=0, padx=padx, pady=pady, sticky=tk.N)  # https://www.tutorialspoint.com/python/tk_grid.htm

# Define data table (Treeview) and its scrollbar. Put them in a Frame.
tree_frame_container = tk.Frame(frame_container)  # https://www.tutorialspoint.com/python/tk_frame.htm
tree_frame_container.grid(row=0, column=0, padx=padx, pady=pady)
tree_scroll_container = tk.Scrollbar(tree_frame_container)
tree_scroll_container.grid(row=0, column=1, padx=0, pady=pady, sticky='ns')
tree_container = ttk.Treeview(tree_frame_container, yscrollcommand=tree_scroll_container.set, selectmode="browse")  # https://docs.python.org/3/library/tkinter.ttk.html#treeview
tree_container.grid(row=0, column=0, padx=0, pady=pady)
tree_scroll_container.config(command=tree_container.yview)

# Define the data table's formatting and content
tree_container['columns'] = ("id", "skill", "size")  # Define columns
tree_container.column("#0", width=0, stretch=tk.NO)  # Format columns. Suppress the irritating first empty column.
tree_container.column("id", anchor=tk.E, width=40)  # "E" stands for East, meaning Right. Possible anchors are N, NE, E, SE, S, SW, W, NW and CENTER
tree_container.column("skill", anchor=tk.E, width=80)
tree_container.column("size", anchor=tk.W, width=200)
tree_container.heading("#0", text="", anchor=tk.W)  # Create column headings
tree_container.heading("id", text="Id", anchor=tk.CENTER)
tree_container.heading("skill", text="skill", anchor=tk.CENTER)
tree_container.heading("size", text="size", anchor=tk.CENTER)
tree_container.tag_configure('oddrow', background=oddrow)  # Create tags for rows in 2 different colors
tree_container.tag_configure('evenrow', background=evenrow)

tree_container.bind("<ButtonRelease-1>", lambda event: edit_container(event, tree_container))  # Define function to be called, when an item is selected.
# tree_container.bind("<Double-Button-1>", copy_container_id)  # Define function to be called after double click.

# Define Frame which contains labels, entries and buttons
controls_frame_container = tk.Frame(frame_container)
controls_frame_container.grid(row=3, column=0, padx=padx, pady=pady)

# Define Frame which contains labels (text fields) and entries (input fields)
edit_frame_container = tk.Frame(controls_frame_container)  # Add tuple entry boxes
edit_frame_container.grid(row=0, column=0, padx=padx, pady=pady)
# label and entry for container id
label_container_id = tk.Label(edit_frame_container, text="Id")  # https://www.tutorialspoint.com/python/tk_label.htm
label_container_id.grid(row=0, column=0, padx=padx, pady=pady)
entry_container_id = tk.Entry(edit_frame_container, width=4, justify="right")  # https://www.tutorialspoint.com/python/tk_entry.htm
entry_container_id.grid(row=1, column=0, padx=padx, pady=pady)
# label and entry for container weight
label_container_weight = tk.Label(edit_frame_container, text="skill")
label_container_weight.grid(row=0, column=1, padx=padx, pady=pady)
entry_container_weight = tk.Entry(edit_frame_container, width=8, justify="right")
entry_container_weight.grid(row=1, column=1, padx=padx, pady=pady)
# label and entry for container destination
label_container_destination = tk.Label(edit_frame_container, text="size")
label_container_destination.grid(row=0, column=2, padx=padx, pady=pady)
entry_container_destination = tk.Entry(edit_frame_container, width=20)
entry_container_destination.grid(row=1, column=2, padx=padx, pady=pady)

# Define Frame which contains buttons
button_frame_container = tk.Frame(controls_frame_container)
button_frame_container.grid(row=1, column=0, padx=padx, pady=pady)
# Define buttons
button_create_container = tk.Button(button_frame_container, text="Create", command=lambda: create_container(tree_container, read_container_entries()))
button_create_container.grid(row=0, column=1, padx=padx, pady=pady)
button_update_container = tk.Button(button_frame_container, text="Update", command=lambda: update_container(tree_container, read_container_entries()))
button_update_container.grid(row=0, column=2, padx=padx, pady=pady)
button_delete_container = tk.Button(button_frame_container, text="Delete", command=lambda: delete_container(tree_container, read_container_entries()))
button_delete_container.grid(row=0, column=3, padx=padx, pady=pady)
button_clear_boxes = tk.Button(button_frame_container, text="Clear Entry Boxes", command=clear_container_entries)
button_clear_boxes.grid(row=0, column=4, padx=padx, pady=pady)
# endregion container widgets


# region aircraft widgets
# Define Labelframe which contains all aircraft related GUI objects (data table, labels, buttons, ...)
frame_aircraft = tk.LabelFrame(main_window, text="Route")  # https://www.tutorialspoint.com/python/tk_labelframe.htm
frame_aircraft.grid(row=0, column=1, padx=padx, pady=pady, sticky=tk.N)  # https://www.tutorialspoint.com/python/tk_grid.htm

# Define data table (Treeview) and its scrollbar. Put them in a Frame.
tree_frame_aircraft = tk.Frame(frame_aircraft)  # https://www.tutorialspoint.com/python/tk_frame.htm
tree_frame_aircraft.grid(row=0, column=0, padx=padx, pady=pady)
tree_scroll_aircraft = tk.Scrollbar(tree_frame_aircraft)
tree_scroll_aircraft.grid(row=0, column=1, padx=0, pady=pady, sticky='ns')
tree_aircraft = ttk.Treeview(tree_frame_aircraft, yscrollcommand=tree_scroll_aircraft.set, selectmode="browse")  # https://docs.python.org/3/library/tkinter.ttk.html#treeview
tree_aircraft.grid(row=0, column=0, padx=0, pady=pady)
tree_scroll_aircraft.config(command=tree_aircraft.yview)

# Define the data table's formatting and content
tree_aircraft['columns'] = ("id", "max_capacity", "difficulty")  # Define columns
tree_aircraft.column("#0", width=0, stretch=tk.NO)  # Format columns. Suppress the irritating first empty column.
tree_aircraft.column("id", anchor=tk.E, width=40)  # "E" stands for East, meaning Right. Possible anchors are N, NE, E, SE, S, SW, W, NW and CENTER
tree_aircraft.column("max_capacity", anchor=tk.E, width=100)
tree_aircraft.column("difficulty", anchor=tk.W, width=100)
tree_aircraft.heading("#0", text="", anchor=tk.W)  # Create column headings
tree_aircraft.heading("id", text="Id", anchor=tk.CENTER)
tree_aircraft.heading("max_capacity", text="Max Capacity", anchor=tk.CENTER)
tree_aircraft.heading("difficulty", text="difficulty", anchor=tk.CENTER)
tree_aircraft.tag_configure('oddrow', background=oddrow)  # Create tags for rows in 2 different colors
tree_aircraft.tag_configure('evenrow', background=evenrow)

tree_aircraft.bind("<ButtonRelease-1>", lambda event: edit_aircraft(event, tree_aircraft))  # Define function to be called, when an item is selected.
# tree_aircraft.bind("<Double-Button-1>", copy_aircraft_id)  # Define function to be called after double click.

# Define Frame which contains labels, entries and buttons
controls_frame_aircraft = tk.Frame(frame_aircraft)
controls_frame_aircraft.grid(row=3, column=0, padx=padx, pady=pady)

# Define Frame which contains labels (text fields) and entries (input fields)
edit_frame_aircraft = tk.Frame(controls_frame_aircraft)  # Add tuple entry boxes
edit_frame_aircraft.grid(row=0, column=0, padx=padx, pady=pady)
# label and entry for aircraft id
label_aircraft_id = tk.Label(edit_frame_aircraft, text="Id")  # https://www.tutorialspoint.com/python/tk_label.htm
label_aircraft_id.grid(row=0, column=0, padx=padx, pady=pady)
entry_aircraft_id = tk.Entry(edit_frame_aircraft, width=4, justify="right")  # https://www.tutorialspoint.com/python/tk_entry.htm
entry_aircraft_id.grid(row=1, column=0, padx=padx, pady=pady)
# label and entry for aircraft weight
label_aircraft_max_cargo_weight = tk.Label(edit_frame_aircraft, text="Max Capacity")
label_aircraft_max_cargo_weight.grid(row=0, column=1, padx=padx, pady=pady)
entry_aircraft_max_cargo_weight = tk.Entry(edit_frame_aircraft, width=8, justify="right")
entry_aircraft_max_cargo_weight.grid(row=1, column=1, padx=padx, pady=pady)
# label and entry for aircraft destination
label_aircraft_registration = tk.Label(edit_frame_aircraft, text="difficulty")
label_aircraft_registration.grid(row=0, column=2, padx=padx, pady=pady)
entry_aircraft_registration = tk.Entry(edit_frame_aircraft, width=9)
entry_aircraft_registration.grid(row=1, column=2, padx=padx, pady=pady)

# Define Frame which contains buttons
button_frame_aircraft = tk.Label(controls_frame_aircraft)
button_frame_aircraft.grid(row=1, column=0, padx=padx, pady=pady)
# Define buttons
button_create_aircraft = tk.Button(button_frame_aircraft, text="Create", command=lambda: create_aircraft(tree_aircraft, read_aircraft_entries()))
button_create_aircraft.grid(row=0, column=1, padx=padx, pady=pady)
button_update_aircraft = tk.Button(button_frame_aircraft, text="Update", command=lambda: update_aircraft(tree_aircraft, read_aircraft_entries()))
button_update_aircraft.grid(row=0, column=2, padx=padx, pady=pady)
button_delete_aircraft = tk.Button(button_frame_aircraft, text="Delete", command=lambda: delete_aircraft(tree_aircraft, read_aircraft_entries()))
button_delete_aircraft.grid(row=0, column=3, padx=padx, pady=pady)
button_clear_boxes = tk.Button(button_frame_aircraft, text="Clear Entry Boxes", command=clear_aircraft_entries)
button_clear_boxes.grid(row=0, column=4, padx=padx, pady=pady)
# endregion aircraft widgets


# region transport widgets
# Define Labelframe which contains all transport related GUI objects (data table, labels, buttons, ...)
frame_transport = tk.LabelFrame(main_window, text="Booking")  # https://www.tutorialspoint.com/python/tk_labelframe.htm
frame_transport.grid(row=0, column=2, padx=padx, pady=pady, sticky=tk.N)  # https://www.tutorialspoint.com/python/tk_grid.htm

# Define data table (Treeview) and its scrollbar. Put them in a Frame.
tree_frame_transport = tk.Frame(frame_transport)  # https://www.tutorialspoint.com/python/tk_frame.htm
tree_frame_transport.grid(row=0, column=0, padx=padx, pady=pady)
tree_scroll_transport = tk.Scrollbar(tree_frame_transport)
tree_scroll_transport.grid(row=0, column=1, padx=0, pady=pady, sticky='ns')
tree_transport = ttk.Treeview(tree_frame_transport, yscrollcommand=tree_scroll_transport.set, selectmode="browse")  # https://docs.python.org/3/library/tkinter.ttk.html#treeview
tree_transport.grid(row=0, column=0, padx=0, pady=pady)
tree_scroll_transport.config(command=tree_transport.yview)

# Define the data table's formatting and content
tree_transport['columns'] = ("id", "date", "team_id", "route_id")  # Define columns
tree_transport.column("#0", width=0, stretch=tk.NO)  # Format columns. Suppress the irritating first empty column.
tree_transport.column("id", anchor=tk.E, width=40)  # "E" stands for East, meaning Right. Possible anchors are N, NE, E, SE, S, SW, W, NW and CENTER
tree_transport.column("date", anchor=tk.E, width=80)
tree_transport.column("team_id", anchor=tk.E, width=70)
tree_transport.column("route_id", anchor=tk.E, width=70)
tree_transport.heading("#0", text="", anchor=tk.W)  # Create column headings
tree_transport.heading("id", text="Id", anchor=tk.CENTER)
tree_transport.heading("date", text="Date", anchor=tk.CENTER)
tree_transport.heading("team_id", text="Team Id", anchor=tk.CENTER)
tree_transport.heading("route_id", text="Route Id", anchor=tk.CENTER)
tree_transport.tag_configure('oddrow', background=oddrow)  # Create tags for rows in 2 different colors
tree_transport.tag_configure('evenrow', background=evenrow)

tree_transport.bind("<ButtonRelease-1>", lambda event: edit_transport(event, tree_transport))  # Define function to be called, when an item is selected.

# Define Frame which contains labels, entries and buttons
controls_frame_transport = tk.Frame(frame_transport)
controls_frame_transport.grid(row=3, column=0, padx=padx, pady=pady)

# Define Frame which contains labels (text fields) and entries (input fields)
edit_frame_transport = tk.Frame(controls_frame_transport)  # Add tuple entry boxes
edit_frame_transport.grid(row=0, column=0, padx=padx, pady=pady)
# label and entry for transport id
label_transport_id = tk.Label(edit_frame_transport, text="Id")  # https://www.tutorialspoint.com/python/tk_label.htm
label_transport_id.grid(row=0, column=0, padx=padx, pady=pady)
entry_transport_id = tk.Entry(edit_frame_transport, width=4, justify="right")  # https://www.tutorialspoint.com/python/tk_entry.htm
entry_transport_id.grid(row=1, column=0, padx=padx, pady=pady)
# label and entry for transport weight
label_transport_date = tk.Label(edit_frame_transport, text="Date")
label_transport_date.grid(row=0, column=1, padx=padx, pady=pady)
entry_transport_date = tk.Entry(edit_frame_transport, width=10)
entry_transport_date.grid(row=1, column=1, padx=padx, pady=pady)
# label and entry for transport destination
label_transport_container_id = tk.Label(edit_frame_transport, text="Team Id")
label_transport_container_id.grid(row=0, column=2, padx=padx, pady=pady)
entry_transport_container_id = tk.Entry(edit_frame_transport, width=4, justify="right")
entry_transport_container_id.grid(row=1, column=2, padx=padx, pady=pady)
# label and entry for transport destination
label_transport_aircraft_id = tk.Label(edit_frame_transport, text="Route Id")
label_transport_aircraft_id.grid(row=0, column=3, padx=padx, pady=pady)
entry_transport_aircraft_id = tk.Entry(edit_frame_transport, width=4, justify="right")
entry_transport_aircraft_id.grid(row=1, column=3, padx=padx, pady=pady)

# Define Frame which contains buttons
button_frame_transport = tk.Frame(controls_frame_transport)
button_frame_transport.grid(row=1, column=0, padx=padx, pady=pady)
# Define buttons
button_create_transport = tk.Button(button_frame_transport, text="Create", command=lambda: create_transport(tree_transport, read_transport_entries()))
button_create_transport.grid(row=0, column=1, padx=padx, pady=pady)
button_update_transport = tk.Button(button_frame_transport, text="Update", command=lambda: update_transport(tree_transport, read_transport_entries()))
button_update_transport.grid(row=0, column=2, padx=padx, pady=pady)
button_delete_transport = tk.Button(button_frame_transport, text="Delete", command=lambda: delete_transport(tree_transport, read_transport_entries()))
button_delete_transport.grid(row=0, column=3, padx=padx, pady=pady)
button_clear_boxes = tk.Button(button_frame_transport, text="Clear Entry Boxes", command=clear_transport_entries)
button_clear_boxes.grid(row=0, column=4, padx=padx, pady=pady)
# endregion transport widgets

Team(id=1, skill=1, size=2)
Route(id=1, max_capacity=6,difficulty=0 )
Booking(id=1, date=date.today(), team_id=1, route_id=1)

if __name__ == "__main__":  # Executed when invoked directly. We use this so main_window.mainloop() does not keep our unit tests from running.
    refresh_treeview(tree_container, Team)  # Load data from database
    refresh_treeview(tree_aircraft, Route)  # Load data from database
    refresh_treeview(tree_transport, Booking)  # Load data from database
    main_window.mainloop()  # Wait for button clicks and act upon them

