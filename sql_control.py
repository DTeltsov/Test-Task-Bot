import sqlite3
import pandas as pd



def wrtitedb(data):
    con = sqlite3.connect('exchangerate.db')
    df = pd.DataFrame(data)
    df.to_sql("Rates", con, if_exists='replace')

def get_time():
    con = sqlite3.connect('exchangerate.db')
    cur = con.cursor()
    cur.execute('''  
    SELECT timestamp FROM Rates
          ''')
    return cur.fetchone()[0]

def get_rates():
    con = sqlite3.connect('exchangerate.db')
    df = pd.DataFrame()
    df = pd.read_sql_query("SELECT * from Rates", con)
    print(df)
    return df