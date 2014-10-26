#!/usr/bin/env python

import psycopg2

class DBDomain:
    def __init__(self, id, name, type):
        self.name = name
        self.id = id
        self.type = type

def db_connect():
    global conn
    conn = psycopg2.connect('dbname=pdns user=pdns host=localhost password=QNv7Yl0zZUfB')

def db_get_domains(domains):
    cur = conn.cursor()
    cur.execute('SELECT * FROM domains')
    for d in cur.fetchall():
        n = DBDomain(d[0], d[1], d[4])
        domains[d[1]] = n
    cur.close()

def db_create_domains(l):
    cur = conn.cursor()
    for d in l:
        cur.execute('INSERT INTO domains (name, type) VALUES (%s, %s)', (d, 'NATIVE'))
    conn.commit()
    cur.close()

def db_delete_domains(l):
    cur = conn.cursor()
    for d in l:
        cur.execute('DELETE FROM records WHERE domain_id = (SELECT id FROM domains WHERE name = %s)', (d,))
        cur.execute('DELETE FROM domains WHERE name = %s', (d,))
    conn.commit()
    cur.close()
    
