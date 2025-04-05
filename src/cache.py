import sqlite3

def get_mouse_data() -> list[dict]:
    con = sqlite3.connect("P4MouseCoords.db")
    cur = con.cursor()
    cur.execute("")

def initialize_mouse_table():
    con = sqlite3.connect("P4MouseCoords.db")
    cur = con.cursor()
    cur.execute("")