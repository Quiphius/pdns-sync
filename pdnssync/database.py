class DBDomain:
    def __init__(self, id, name, type):
        self.name = name
        self.id = id
        self.type = type


class DBRecord:
    def __init__(self, id, data, ttl, prio):
        self.id = id
        self.data = data
        self.ttl = ttl
        self.prio = prio


class Database:
    def __init__(self, type, database, user, password, host):
        if type == 'postgresql':
            import psycopg2
            self.conn = psycopg2.connect(database=database, user=user, password=password, host=host)
        elif type == 'mysql':
            import MySQLdb
            self.conn = MySQLdb.connect(db=database, user=user, passwd=password, host=host)
        else:
            print('E: no such database type')
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
        cur.execute('SELECT * FROM records WHERE domain_id = (SELECT id from domains WHERE name = %s)', (zone, ))
        for d in cur.fetchall():
            i = (d[2], d[3])
            if i not in ret:
                ret[i] = []
            n = DBRecord(d[0], d[4], d[5], d[6])
            ret[i].append(n)
        cur.close()
        return ret

    def create_record(self, zone, name, type, data, ttl, prio):
        cur = self.conn.cursor()
        cur.execute('INSERT INTO records (domain_id, name, type, content, ttl, prio) SELECT id, %s, %s, %s, %s, %s FROM domains WHERE name = %s', (name, type, data, ttl, prio, zone))
        self.conn.commit()
        cur.close()

    def update_record(self, id, ttl, prio):
        cur = self.conn.cursor()
        cur.execute('UPDATE records SET ttl = %s, prio = %s where id = %s', (ttl, prio, id))
        self.conn.commit()
        cur.close()

    def delete_record(self, id):
        cur = self.conn.cursor()
        cur.execute('DELETE FROM records WHERE id = %s', (id,))
        self.conn.commit()
        cur.close()

    def update_soa(self, zone, content):
        cur = self.conn.cursor()
        cur.execute('UPDATE records set content = %s WHERE type = \'SOA\' AND domain_id = (SELECT id from domains WHERE name = %s)', (content, zone))
        self.conn.commit()
        cur.close()
