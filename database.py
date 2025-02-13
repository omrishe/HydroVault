import sqlite3
import csv
import os

# Create a connection to the database
connection = sqlite3.connect('storeroom.db')

# Create a table (|UniqueIdentifier |IDGroup |FluidType |FluidAmount |Description)
connection.execute('''CREATE TABLE IF NOT EXISTS storeroom (
         IDGroup         TEXT NOT NULL,
         FluidType       TEXT NOT NULL,
         FluidAmount     INT  NOT NULL,
         Description     TEXT,
         PRIMARY KEY (IDGroup)
         );''')
connection.close()

def insertDb(IDGroup,FluidType,FluidAmount,Description=''):
    db_conn = sqlite3.connect('storeroom.db')  # Open a new connection
    query_handler = db_conn.cursor()
    query_handler.execute("INSERT INTO storeroom VALUES (?, ?, ?, ?)", (IDGroup, FluidType, FluidAmount, Description))
    db_conn.commit()
    db_conn.close()
    print_db_to_csv()

def isIDExist(IDGroup):
    db_conn = sqlite3.connect('storeroom.db')  # Open a new connection
    query_handler = db_conn.cursor()
    query_handler.execute("SELECT 1 FROM storeroom WHERE IDGroup = ? LIMIT 1", (IDGroup,))
    result = query_handler.fetchone()  # Fetch one result
    db_conn.close() 
    return result is not None
    

def changeFluidValue(IDGroup,FluidAmount):
    try:
        db_conn = sqlite3.connect('storeroom.db')  # Open a new connection
        query_handler = db_conn.cursor()
        # Update the FluidAmount for the given IDGroup
        query_handler.execute("UPDATE storeroom SET FluidAmount = ? WHERE IDGroup = ?", (FluidAmount, IDGroup))
        db_conn.commit()
        print("Updated FluidAmount for IDGroup: " + str(IDGroup) + "to " + str(FluidAmount) + " sucessfully")
        db_conn.close()
    except sqlite3.Error as e:
        print("Error occurred while updating FluidAmount:", e)
    print_db_to_csv() 

def drainAllBarrels(FluidAmount=0):
    try:
        db_conn = sqlite3.connect('storeroom.db')  # Open a new connection
        query_handler = db_conn.cursor()
        # Update the FluidAmount for the given IDGroup
        query_handler.execute("UPDATE storeroom SET FluidAmount = ?", (FluidAmount,))
        db_conn.commit()
        db_conn.close()
    except sqlite3.Error as e:
        print("Error occurred while updating FluidAmount:", e)
    print_db_to_csv() 

def printDb():
       # Execute a query to select all records from the table
    db_conn = sqlite3.connect('storeroom.db')  # Open a new connection
    query_handler = db_conn.cursor()
    table = query_handler.execute("SELECT * FROM storeroom")
    rows = table.fetchall()
    db_conn.close()
    # Print the column names
    print("IDGroup | NumberInGroup | FluidType | FluidAmount | Description")
    print("-" * 70)  # Prints a separator line

    # Loop through each row in database and print the values
    for row in rows:
        print(f"| {row[0]} | {row[1]} | {row[2]} | {row[3]} |")

def print_db_to_csv():
    #save table to csv
    db_conn = sqlite3.connect('storeroom.db')  # Open a new connection
    query_handler = db_conn.cursor()
    table = query_handler.execute("SELECT * FROM storeroom")
    rows = table.fetchall()
    csv_file = 'storeroom_data.csv' #set file path
    if os.path.exists(csv_file):
        os.remove(csv_file)
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['IDGroup', 'NumberInGroup', 'FluidType', 'FluidAmount', 'Description'])
        writer.writerows(rows)
    print(f"Data saved to {csv_file}.")
    db_conn.close()

def load_data():
        try:
            #Connect to the database
            conn = sqlite3.connect('storeroom.db')
            db_cursor = conn.cursor()
            #select all data from the database
            db_cursor.execute("SELECT * FROM storeroom")
            rows = db_cursor.fetchall()
            #format data
            firstRow =""
            for colName in db_cursor.description:
                firstRow+="|  " + colName[0] + "  |"
            data = firstRow +"\n"
            for row in rows:
                data += str(row) + "\n"
            return data
            conn.close()
        except sqlite3.Error as e:
            print("error occured:")
            print(e)

