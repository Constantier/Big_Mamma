import os
import sqlite3
from Big_Mamma.get_data import get_data_sales


def create_connection(file_name):
    """
    return a database connection to the DB file provided
    :param file_name: the path of the file to connect

    return a sqlite3.Connection object or None if the connection fail
    """
    conn = None
    try:
        conn = sqlite3.connect(file_name)
        return conn
    except sqlite3.Error as e:
        print(e)

    return conn

def line_exist_vente(conn,date,item_id):
    '''
    return 1 if the line with this date and this item_id exist in the table Ventes, 0 otherwise
    :param conn: a sqlite3.Connection object to the DB
    :param date: the date of the line
    :param item_id: the item_id of the line
    '''
    cur=conn.execute('''
                    SELECT COUNT(1)
                    FROM Ventes v
                    WHERE v.date = ? AND v.item_id = ?
                    ''',(date,item_id))
    return cur.fetchone()

def line_exist_item(conn,item_id):
    '''
    return 1 if the line with this id exist in the table items, 0 otherwise
    :param conn: a sqlite3.Connection object to the DB
    :param item_id: the item_id to identify the line
    '''
    cur=conn.execute('''
                    SELECT COUNT(1)
                    FROM items i
                    WHERE i.id=?
                    ''',(item_id))
    return cur.fetchone()

def update_line_vente(conn,vente):
    '''
    Update the line identified by date and item_id with the new values.
    :param conn: connexion param to the db
    :param vente: the sales line from the sheet (date, item_id, item_quantiy, item_name, item_montant, montant_total)

    return nothing
    '''
    sql=""" UPDATE Ventes
            SET item_quantity=?,item_name=?,item_montant=?,montant_total=?
            WHERE date =? AND item_id =?"""
    cur=conn.cursor()
    cur.execute(sql,(vente[2],vente[3],vente[4],vente[5],vente[0],vente[1]))
    conn.commit()
    return

def update_line_item(conn,item):
    '''
    Update the line identified by id with the new values.
    :param conn: connexion param to the db
    :param item: the item line from the sheet (id, Name, Price, Categorie)

    return nothing
    '''
    sql=""" UPDATE items
            SET Name=?,Price=?,Categorie=?
            WHERE id =?"""
    cur=conn.cursor()
    cur.execute(sql,(item[1],item[2],item[3],item[0]))
    conn.commit()
    return

def create_vente(conn, vente):
    """
    Create a new line into the Ventes table
    :param conn: connexion param to the db
    :param vente: the line to add (date, item_id, item_quantiy, item_name, item_montant, montant_total)
    return the vente id
    """
    sql = """ INSERT INTO Ventes(date,item_id,item_quantity,item_name,item_montant,montant_total)
              VALUES(?,?,?,?,?,?) """
    cur = conn.cursor()
    cur.execute(sql, vente)
    conn.commit()
    return cur.lastrowid


def create_item(conn, item):
    """
    Create a new item in the items table
    :param conn:
    :param item: item params (id, Name, Price, Categorie)
    return the item id
    """

    sql = """ INSERT INTO items(id,Name,Price,Categorie)
              VALUES(?,?,?,?) """
    cur = conn.cursor()
    cur.execute(sql, item)
    conn.commit()
    return cur.lastrowid

def update_db():
    """
    Update the file sales.db with the 2 sheets from google
    Return True if the opération went well, False otherwise
    """
    # call to the google API to read the sheet
    sheet_ventes = get_data_sales(sheet="Ventes")
    sheet_items = get_data_sales(sheet="items")

    #connection to the SQL db
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, "data/sales.db")
    conn = create_connection(filename)

    # checking if the connexion is done
    if conn is not None:
        # looping on each line of the sheet
        for i in range(1, len(sheet_ventes)):

            # check if the line with this date and this item_id exist on the table Ventes
            if line_exist_vente(conn,sheet_ventes[i][0],sheet_ventes[i][1])[0]:
                #update the line if it exist

                update_line_vente(conn,sheet_ventes[i])
            else :
                #create it otherwise
                create_vente(conn,sheet_ventes[i])

        # doing the same for the table items
        for i in range(1, len(sheet_items)):
            if line_exist_item(conn,sheet_items[i][0])[0]:
                update_line_item(conn,sheet_items[i])
            else :
                create_item(conn,sheet_items[i])

        conn.close()
        return True

    return False

if __name__ == "__main__":
    update_db()
