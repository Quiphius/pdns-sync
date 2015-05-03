import os


class DBDomain(object):
    def __init__(self, dbid, name, nstype):
        self.name = name
        self.id = dbid
        self.type = nstype


class DBRecord(object):
    def __init__(self, dbid, data, ttl, prio):
        self.id = dbid
        self.data = data
        self.ttl = ttl
        self.prio = prio


class Database(object):
    def __init__(self):
        dbtype = os.getenv('PDNS_DBTYPE', 'postgresql')
        database = os.getenv('PDNS_DB', 'pdns')
        user = os.getenv('PDNS_DBUSER', 'pdns')
        password = os.getenv('PDNS_DBPASSWORD', '')
        host = os.getenv('PDNS_DBHOST', 'localhost')

        if dbtype == 'postgresql':
            import psycopg2
            self.conn = psycopg2.connect(database=database, user=user, password=password, host=host)
        elif dbtype == 'mysql':
            import MySQLdb
            self.conn = MySQLdb.connect(db=database, user=user, passwd=password, host=host)
        else:
            print('E: no such database dbtype')
            quit()

    def get_domains(self):
        ret = {}
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM domains')
        for d in cur.fetchall():
            n = DBDomain(d[0], d[1], d[4])
            ret[d[1]] = n
        cur.close()
        return ret

    def create_domains(self, l):
        cur = self.conn.cursor()
        for d in l:
            cur.execute('INSERT INTO domains (name, type) VALUES (%s, \'NATIVE\')', (d, ))
        self.conn.commit()
        cur.close()

    def delete_domains(self, l):
        cur = self.conn.cursor()
        for d in l:
            cur.execute('DELETE FROM domains WHERE name = %s', (d,))
        self.conn.commit()
        cur.close()

    def get_records(self, zone):
        ret = {}
        cur = self.conn.cursor()
        cur.execute('SELECT * FROM records WHERE domain_id = (SELECT id from domains WHERE name = %s) AND type != \'\'', (zone, ))
        for d in cur.fetchall():
            i = (d[2], d[3])
            if i not in ret:
                ret[i] = []
            n = DBRecord(d[0], d[4], d[5], d[6])
            ret[i].append(n)
        cur.close()
        return ret

    def create_record(self, zone, name, nstype, data, ttl, prio):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO records (domain_id, name, type, content, ttl, prio) SELECT id, %s, %s, %s, %s, %s FROM domains WHERE name = %s', (name, nstype, data, ttl, prio, zone))
        self.conn.commit()
        cur.close()

    def update_record(self, dbid, ttl, prio):
        cur = self.conn.cursor()
        cur.execute('UPDATE records SET ttl = %s, prio = %s where id = %s', (ttl, prio, dbid))
        self.conn.commit()
        cur.close()

    def delete_record(self, dbid):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM records WHERE id = %s', (dbid,))
        self.conn.commit()
        cur.close()

    def update_soa(self, zone, content):
        cur = self.conn.cursor()
        cur.execute('UPDATE records set content = %s WHERE type = \'SOA\' AND domain_id = (SELECT id from domains WHERE name = %s)', (content, zone))
        self.conn.commit()
        cur.close()
