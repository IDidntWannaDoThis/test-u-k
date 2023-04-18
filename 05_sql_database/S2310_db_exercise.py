"""
Som altid skal du læse hele opgavebeskrivelsen omhyggeligt, før du begynder at løse opgaven.

Kopier denne fil til din egen løsningsmappe. Skriv din løsning ind i kopien.

Anvend det, du har lært i dette kapitel om databaser, på en første opgave.

Trin 1:
Opret en ny database "my_second_sql_database.db" i din eksisterende mappe “data”.
Denne database skal indeholde 2 tabeller.
Den første tabel skal hedde "customers" og repræsenteres i Python-koden af en klasse kaldet "Customer".
Tabellen bruger sin første attribut "id" som primærnøgle.
De andre attributter i tabellen hedder "name", "address" og "age".
Definer selv fornuftige datatyper for attributterne.

Trin 2:
Den anden tabel skal hedde "products" og repræsenteres i Python-koden af en klasse kaldet "Product".
Denne tabel bruger også sin første attribut "id" som primærnøgle.
De andre attributter i tabellen hedder "product_number", "price" og "brand".

Trin 3:
Skriv en funktion create_test_data(), der opretter testdata for begge tabeller.

Trin 4:
Skriv en metode __repr__() for begge dataklasser, så du kan vise poster til testformål med print().

Til læsning fra databasen kan du genbruge de to funktioner select_all() og get_record() fra S2240_db_class_methods.py.

Trin 5:
Skriv hovedprogrammet: Det skriver testdata til databasen, læser dataene fra databasen med select_all() og/eller get_record() og udskriver posterne til konsollen med print().

Når dit program er færdigt, skal du skubbe det til dit github-repository.
Send derefter denne Teams-besked til din lærer: <filename> færdig
Fortsæt derefter med den næste fil.
"""
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import Column, String, Integer,Float
from sqlalchemy import create_engine
from sqlalchemy import create_engine, select

Database = 'sqlite:///../data/my_second_sql_database.db'
Base = declarative_base()

class Customer(Base):
    # this class declaration does 2 important things at once:
    # 1. as usual, it declares a class we can store data in, inside our python program.
    # 2. it creates a table in a sql database with the specified columns
    __tablename__ = "Customer"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    address = Column(String)
    age = Column(Integer)

    def __repr__(self):  # Only for testing/debugging purposes.
        return f"Person({self.id=}  {self.name=}  {self.name=}  {self.age=})"


class pruduct(Base):
    # this class declaration does 2 important things at once:
    # 1. as usual, it declares a class we can store data in, inside our python program.
    # 2. it creates a table in a sql database with the specified columns
    __tablename__ = "pruduct"
    id = Column(Integer, primary_key=True)
    product_number = Column(Integer)
    brand = Column(String)
    price = Column(Float)

    def __repr__(self):  # Only for testing/debugging purposes.
        return f"Person({self.id=}    {self.brand=}  {self.price=}  {self.product_number=})"

def create_test_data():  # Optional. Used to test data base functions before gui is ready.
    with Session(engine) as session:
        new_items = []
        new_items.append(Customer(name="peter", address="something", age=18))
        new_items.append(Customer(name="susan", address="something else", age=19))
        new_items.append(Customer(name="jane", address="need diffrent text", age=21))
        new_items.append(Customer(name="harry", address="to show it", age=20))

        new_items.append(pruduct(brand="peter", price=28.38, product_number=1800))
        new_items.append(pruduct(brand="susan", price=28.38, product_number=1900))
        new_items.append(pruduct(brand="jane", price=28.38, product_number=2100))
        new_items.append(pruduct(brand="harry", price=36.48, product_number=2000))
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

create_test_data()

print(select_all(Customer))
print(select_all(pruduct))