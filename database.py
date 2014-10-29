#!/usr/bin/env python

import psycopg2
from dbrecords import *

def db_connect():
    global conn
    conn = psycopg2.connect('dbname=pdns user=pdns host=localhost password=QNv7Yl0zZUfB')

def db_get_domains():
    ret = {}
    cur = conn.cursor()
    cur.execute('SELECT * FROM domains')
    for d in cur.fetchall():
        n = DBDomain(d[0], d[1], d[4])
        ret[d[1]] = n
    cur.close()
    return ret

def db_get_records(domain):
    ret = {}
    cur = conn.cursor()
    cur.execute('SELECT * FROM records WHERE domain_id = (SELECT id from domains WHERE name = %s)', (domain, ))
    for d in cur.fetchall():
        i = (d[2], d[3])
        if i not in ret:
            ret[i] = []
        n = DBRecord(d[0], d[4], d[5], d[6])
        ret[i].append(n)
    cur.close()
    return ret

def db_create_record(zone, name, type, data, ttl, prio):
    cur = conn.cursor()
    cur.execute('INSERT INTO records (domain_id, name, type, content, ttl, prio) SELECT id, %s, %s, %s, %s, %s FROM domains WHERE name = %s', (name, type, data, ttl, prio, zone))
    conn.commit()
    cur.close()

def db_update_record(id, data, ttl, prio):
    cur = conn.cursor()
    cur.execute('UPDATE records SET content = %s, ttl = %s, prio = %s where id = %s', (data, ttl, prio, id))
    conn.commit()
    cur.close()

def db_delete_record(id):
    cur = conn.cursor()
    cur.execute('DELETE FROM records WHERE id = %s', (id,))
    conn.commit()
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
