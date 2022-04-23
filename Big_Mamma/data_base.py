import sqlite3
from sqlite3 import Error
from Big_Mamma.get_data import get_data_sales
import os

def create_connection(file_name):
    """
    return a database connection to a new DB stored in memory
    """
    conn = None
    try:
        conn = sqlite3.connect(file_name)
        return conn
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_vente(conn, project):
    """
    Create a new line into the Ventes table
    :param conn:
    :param project:
    :return: project id
    """
    sql = ''' INSERT INTO Ventes(date,item_id,item_quantity,item_name,item_montant,montant_total)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, project)
    conn.commit()
    return cur.lastrowid


def create_item(conn, task):
    """
    Create a new item in the items table
    :param conn:
    :param task:
    :return:
    """

    sql = ''' INSERT INTO items(id,Name,Price,Categorie)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()
    return cur.lastrowid

def drop_table(conn, name):
    """
    Create a new item in the items table
    :param conn:
    :param task:
    :return:
    """
    sql = ''' DROP TABLE IF EXISTS ? '''
    cur = conn.cursor()
    cur.execute(sql, (name,))
    conn.commit()
    return cur.lastrowid

def generate_db():
    '''
    Update the file sales.db with the 2 sheets from google
    Return True if the opération went well, False otherwise
    '''
    sheet_ventes=get_data_sales(sheet='Ventes')
    sheet_items=get_data_sales(sheet='items')

    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'data/sales.db')

    conn=create_connection(filename)

    sql_create_projects_table = """
                                    CREATE TABLE Ventes (
                                    id integer PRIMARY KEY,
                                    date date,
                                    item_id integer,
                                    item_quantity integer,
                                    item_name varchar,
                                    item_montant float,
                                    montant_total float
                                ); """

    sql_create_tasks_table =    """
                                    CREATE TABLE items (
                                    id integer PRIMARY KEY,
                                    Name varchar,
                                    Price float,
                                    Categorie varchar
                                );"""

    # create tables
    if conn is not None:
        # create projects table
        sql = ''' DROP TABLE IF EXISTS Ventes ;'''
        cur = conn.cursor()
        cur.execute(sql)

        sql = ''' DROP TABLE IF EXISTS items ;'''
        cur = conn.cursor()
        cur.execute(sql)

        create_table(conn, sql_create_projects_table)

        # create tasks table
        create_table(conn, sql_create_tasks_table)

        for i in range(1,len(sheet_ventes)):
            create_vente(conn,sheet_ventes[i])
        for i in range (1,len(sheet_items)):
            create_item(conn,sheet_items[i])

        return True

    return False

if __name__=='__main__':
    generate_db()
