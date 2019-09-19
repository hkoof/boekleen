#!/usr/bin/env python3

import os.path
import datetime
import sqlite3
import barcode

import prog

class BoekLeenError(Exception): pass

class Row(sqlite3.Row):
    def __init__(self, *args, **kwargs):
        self.extra_attrs = dict()
        super().__init__()

    def __getitem__(self, key):
        if key in self.keys():
            return super().__getitem__(key)
        return self.extra_attrs[key]

    def __setitem__(self, key, value):
        self.extra_attrs[key] = value

    def __str__(self):
        result = list()
        for key in self.keys():
            result.append("{} ==> {}".format(key, self[key]))
        for key, value in self.extra_attrs.items():
            result.append("{} ==> {}".format(key, value))
        result.append("\n")
        return "\n".join(result)

    def items(self):
        result = list()
        for key in self.keys():
            value = self[key]
            result.append((key, value,))
        for key, value in self.extra_attrs.items():
            result.append((key, value,))
        return result

def nu():  # aantal seconden sinds epoch om datum-tijd op te kunnen slaan in DB
    return int(datetime.datetime.today().timestamp())

def tijdstring(secs_since_epoch): # geeft string terug met datum in leesbare vorm
    if not secs_since_epoch:
        return ""
    return str(datetime.datetime.fromtimestamp(secs_since_epoch))

class BoekLeenDB:
    def __init__(self, db_file_path=None, create=False):
        def initDB():
            self.db = sqlite3.connect(self.dbfile)
            self.db.row_factory = Row
            self.db.execute('PRAGMA foreign_keys = ON')

        if db_file_path != None:
            self.dbfile = db_file_path
        else:
            self.dbfile = prog.default_sqlite_database_file

        if not create:
            if not os.path.isfile(self.dbfile):
                raise NameError("File {} bestaat niet.".format(self.dbfile))
            initDB()
            return

        # Vanaf hier: database is nieuw en dus leeg.

        if os.path.isfile(self.dbfile):
            raise NameError("File {} bestaat reeds.".format(self.dbfile))
        initDB()

        # Tabellen in database maken met SQL statements
        #
        cursor = self.db.cursor()
        self.db.execute('''
            create table boeken (
                isbn text primary key not null unique,
                titel text,
                auteur text,
                categorie_id integer,
                kastcode_id integer,
                omschrijving text,
                trefwoorden text,
                invoertijdstip integer not null,
                verwijdertijdstip integer,
                foreign key(categorie_id) references categorie(id),
                foreign key(kastcode_id) references kastcode(id)
            )''')
        self.db.execute('''
            create view boek as select * from boeken where verwijdertijdstip is null
            ''')
        self.db.execute('''
            create table categorie (
                id integer primary key autoincrement not null,
                categorienaam text
            )''')
        self.db.execute('''
            create table kastcode (
                id integer primary key autoincrement not null,
                code text not null,
                tekstkleur text,
                achtergrondkleur text
            )''')
        self.db.execute('''
            create table personen (
                id integer primary key autoincrement not null,
                voornaam text,
                achternaam text not null,
                klas text,
                invoertijdstip integer not null,
                verwijdertijdstip integer
            )''')
        self.db.execute('''
            create view persoon as select * from personen where verwijdertijdstip is null
            ''')
        self.db.execute('''
            create table uitleningen (
                id integer primary key autoincrement not null,
                persoon_id integer not null,
                isbn text not null,
                uitgeleend integer not null,
                teruggebracht integer,
                foreign key(persoon_id) references personen(id),
                foreign key(isbn) references boeken(isbn)
            )''')

        # Indexen
        #
        self.db.execute('create index boeken_titel on boeken (titel)')
        self.db.execute('create index boeken_auteur on boeken (auteur)')
        self.db.execute('create index boeken_kastcode on boeken (kastcode_id)')
        self.db.execute('create index boeken_categorie on boeken (categorie_id)')
        self.db.execute('create index persoon_voornaam on personen (voornaam)')
        self.db.execute('create index persoon_achternaam on personen (achternaam)')
        self.db.execute('create index persoon_klas on personen (klas)')
        self.db.execute('create index uitleningen_persoon on uitleningen (persoon_id)')
        self.db.execute('create index uitleningen_isbn on uitleningen (isbn)')

        self.db.commit()

    def update_table(self, table, key, **kwargs):
        # Als key niet een tuple (key_name, key_value) is, wordt key_name "id"
        # als default genomen.
        if isinstance(key, int):
            key = ('id', str(key))
        elif isinstance(key, str):
            key = ('id', key)

        cursor = self.db.cursor()
        sql_args = list()
        sql = 'update {} set '.format(table)
        for column, value in kwargs.items():
            sql += '{}=?, '.format(column)
            sql_args.append(value)
        sql = sql[:-2] + ' '  # laatste komma verwijderen voor geldige sql syntax
        sql += 'where {}=?'.format(key[0])
        sql_args.append(key[1])
        cursor.execute(sql, sql_args)
        self.db.commit()

    def nieuw_persoon(self, voornaam, achternaam, klas):
        cursor = self.db.cursor()
        cursor.execute('insert into personen values (null, ?, ?, ?, ?, null)', (voornaam, achternaam, klas, nu()))
        self.db.commit()

    def verwijder_persoon(self, persoon_id):
        cursor = self.db.cursor()
        sql = '''update personen set
                 voornaam="----[verwijderd]----",
                 achternaam="----[verwijderd]----",
                 klas="----[verwijderd]----",
                 verwijdertijdstip=?
                 where id=?
        '''
        cursor.execute(sql, (nu(), persoon_id))
        self.db.commit()

    def nieuwe_categorie(self, categorienaam):
        cursor = self.db.cursor()
        cursor.execute('insert into categorie values (null, ?)', (categorienaam,))
        self.db.commit()

    def nieuwe_kastcode(self, code, tekstkleur, achtergrondkleur):
        cursor = self.db.cursor()
        cursor.execute('insert into kastcode values (null, ?, ?, ?)', (code, tekstkleur, achtergrondkleur))
        self.db.commit()

    def verwijder_kastcode(self, kastcode_id):
        cursor = self.db.cursor()
        sql = 'delete from kastcode where id = ?'
        cursor.execute(sql, (kastcode_id,))
        self.db.commit()

    def verwijder_categorie(self, categorie_id):
        cursor = self.db.cursor()
        sql = 'delete from categorie where id = ?'
        cursor.execute(sql, (categorie_id,))
        self.db.commit()

    def nieuw_boek(self, isbn, titel, auteur, categorie_id, kastcode_id, omschrijving=None, trefwoorden=None):
        cursor = self.db.cursor()
        cursor.execute('insert into boeken values (?, ?, ?, ?, ?, ?, ?, ?, null)',
                    (isbn, titel, auteur, categorie_id, kastcode_id, omschrijving, trefwoorden, nu())
                )
        self.db.commit()

    def verwijder_boek(self, isbn):
        cursor = self.db.cursor()
        sql = 'update boeken set kastcode_id=null, categorie_id=null, verwijdertijdstip=? where isbn=?'
        cursor.execute(sql, (nu(), isbn))
        self.db.commit()

    def persoon(self, persoon_id):
        cursor = self.db.cursor()
        cursor.execute("select * from persoon where id=?", (persoon_id,))
        return cursor.fetchone()

    def boek(self, isbn):  # boek is een readonly view met alleen niet-verwijderde boeken
        cursor = self.db.cursor()
        cursor.execute("select * from boek where isbn=?", (isbn,))
        return cursor.fetchone()

    def boeken(self, isbn): # boeken is de echte tabel met ook de verwijderde
        cursor = self.db.cursor()
        cursor.execute("select * from boeken where isbn=?", (isbn,))
        return cursor.fetchone()

    def kastcode(self, kastcode_id):
        cursor = self.db.cursor()
        cursor.execute("select * from kastcode where id=?", (kastcode_id,))
        return cursor.fetchone()

    def categorie(self, categorie_id):
        cursor = self.db.cursor()
        cursor.execute("select * from categorie where id=?", (categorie_id,))
        return cursor.fetchone()

    def kastcode_usage(self, kastcode_id):
        cursor = self.db.cursor()
        cursor.execute('''select count(*) as count
                          from boek
                          where kastcode_id = ?
                       ''', (kastcode_id,))
        return cursor.fetchone()['count']

    def alle_kastcodes(self):
        cursor = self.db.cursor()
        cursor.execute('''select *
                          from kastcode
                          order by code
                       ''')
        return cursor.fetchall()

    def categorie_usage(self, categorie_id):
        cursor = self.db.cursor()
        cursor.execute('''select count(*) as count
                          from boek
                          where categorie_id = ?
                       ''', (categorie_id,))
        return cursor.fetchone()['count']

    def alle_categorien(self):
        cursor = self.db.cursor()
        cursor.execute('''select *
                          from categorie
                          order by categorienaam
                       ''')
        return cursor.fetchall()

    def alle_auteurs(self):
        cursor = self.db.cursor()
        cursor.execute('''select distinct auteur
                          from   boek
                          order by auteur
                       ''')
        return [rec['auteur'] for rec in cursor.fetchall()]

    def alle_personen(self):
        cursor = self.db.cursor()
        cursor.execute('''select *
                          from persoon
                          order by achternaam
                       ''')
        return cursor.fetchall()

    def zoek_personen(self, zoekstring=None, zoekcolumns=None, selectie=None):
        if not zoekstring:
            if not selectie:
                return self.alle_personen()
        elif not zoekcolumns:
            return list()

        query = "select * from persoon\nwhere\n"
        query_args = list()
        if zoekstring:
            search_condition = "(\n    " + "\n    or ".join(["{} like ?".format(col) for col in zoekcolumns]) + "\n)"
            args = [ "%{}%".format(zoekstring) for tmp in range(len(zoekcolumns))]
            query_args.extend(args)
        else:
            search_condition = None

        if selectie:
            selection_list = list()
            args = list()
            for key, val in selectie.items():
                selection_list.append("{} = ?".format(key))
                args.append(val)
            selection_condition = "(\n    " + "\n    and ".join(selection_list) + "\n)"
            query_args.extend(args)
        else:
            selection_condition = None

        if search_condition:
            query += search_condition
            if selection_condition:
                query += "\nand\n" + selection_condition
        else:
            query += selection_condition

        query += "\norder by voornaam"
        cursor = self.db.cursor()
        cursor.execute(query, query_args)
        return cursor.fetchall()

    def alle_klassen(self):
        cursor = self.db.cursor()
        cursor.execute('''select distinct klas
                          from   persoon
                          order by klas
                       ''')
        return [rec['klas'] for rec in cursor.fetchall()]

    def alle_boeken(self):
        cursor = self.db.cursor()
        cursor.execute('''select isbn,
                                 titel,
                                 auteur
                          from   boek
                          order by titel
                       ''')
        return cursor.fetchall()

    def zoek_boeken(self, zoekstring=None, zoekcolumns=None, selectie=None, uitgeleend=None):
        if not zoekstring:
            if not selectie:
                if uitgeleend == None:
                    return self.alle_boeken()
        elif not zoekcolumns:
            return list()

        query = "select * from boek where 1\n"

        query_args = list()
        if zoekstring:
            search_condition = "and (\n    " + "\n    or ".join(["{} like ?".format(col) for col in zoekcolumns]) + "\n)"
            args = [ "%{}%".format(zoekstring) for tmp in range(len(zoekcolumns))]
            query_args.extend(args)
        else:
            search_condition = ""

        if selectie:
            selection_list = list()
            args = list()
            for key, val in selectie.items():
                selection_list.append("{} = ?".format(key))
                args.append(val)
            selection_condition = "and (\n    " + "\n    and ".join(selection_list) + ")\n"
            query_args.extend(args)
        else:
            selection_condition = ""

        if uitgeleend == True:
            selection_condition += """
                and isbn in (select isbn from uitleningen where teruggebracht is null
                and uitleningen.persoon_id in (select id from persoon))
            """
        elif uitgeleend == False:
            selection_condition += """
                and isbn not in (select isbn from uitleningen where teruggebracht is null
                and uitleningen.persoon_id in (select id from persoon))
            """

        query += search_condition + selection_condition
        query += "order by titel"

        cursor = self.db.cursor()
        cursor.execute(query, query_args)
        return cursor.fetchall()

    def uitgeleend(self, isbn):
        cursor = self.db.cursor()
        sql = '''
            select titel,
                   voornaam,
                   achternaam,
                   klas,
                   auteur,
                   uitgeleend,
                   teruggebracht
            from
                boek,
                persoon,
                uitleningen
            where uitleningen.isbn = boek.isbn
            and uitleningen.persoon_id = persoon.id
            and boek.isbn=? and teruggebracht is null
        '''
        cursor.execute(sql, (isbn,))
        return cursor.fetchone()

    def leenuit(self, persoon_id, isbn, dagengeleden=0):  # dagengeleden is eigenlijk alleen voor test-data
        boek = self.boek(isbn)
        if not boek:
            raise BoekLeenError("Boek {} bestaat niet".format(isbn))
        lener = self.persoon(persoon_id)
        if not lener:
            raise BoekLeenError("{} bestaat niet".format(lener[1]))
        geleend = self.uitgeleend(isbn)
        if geleend:
            raise BoekLeenError("'{}' is sinds {} uitgeleend aan {} {}.".format(
                boek[1], tijdstring(geleend[2]), lener[1], lener[2]), geleend)

        cursor = self.db.cursor()
        cursor.execute('insert into uitleningen values (null,?,?,?,null)',
                (str(persoon_id), str(isbn), nu() - (dagengeleden * 24*60*60)))
        self.db.commit()

    def brengterug(self, isbn):
        boek = self.boek(isbn)
        if not boek:
            raise BoekLeenError("Boek {} bestaat niet".format(isbn))
        geleend = self.uitgeleend(isbn)

        if not geleend:
            boek = self.boek(isbn)
            if not boek:
                raise BoekLeenError("ISBN '{}' bestaat niet.".format(isbn))
            raise BoekLeenError("ISBN '{}' is niet uitgeleend.".format(boek['isbn']))
        cursor = self.db.cursor()
        sql = '''
            update uitleningen
            set teruggebracht=?
            where isbn=?
            and teruggebracht is null
        '''
        cursor.execute(sql, (nu(), isbn))
        self.db.commit()

    def uitleningen(self, persoon_id=None, isbn=None,
            uitgeleend=None,
            min_dagen_uitgeleend=None,
            max_dagen_uitgeleend=None
        ):
        cursor = self.db.cursor()
        query = '''
            select titel,
                   voornaam,
                   achternaam,
                   klas,
                   auteur,
                   uitgeleend,
                   teruggebracht
            from
                boek,
                persoon,
                uitleningen
            where uitleningen.isbn = boek.isbn
            and uitleningen.persoon_id = persoon.id
        '''
        arguments = list()

        if isbn != None:
            query += 'and isbn = ? '
            arguments.append(str(isbn))

        if persoon_id != None:
            query += 'and persoon_id = ? '
            arguments.append(str(persoon_id))

        if uitgeleend != None:
            if uitgeleend:
                query += 'and teruggebracht is null '
            else:
                query += 'and teruggebracht is not null '

        if min_dagen_uitgeleend != None:
            tijd = datetime.datetime.now()
            vandaag_begin = datetime.datetime(tijd.year, tijd.month, tijd.day).timestamp()
            min_seconden_uitgeleend = 24 * 3600 * min_dagen_uitgeleend
            query += 'and ? - uitgeleend > ? '
            arguments.append(vandaag_begin)
            arguments.append(min_seconden_uitgeleend)

        if max_dagen_uitgeleend != None:
            tijd = datetime.datetime.now()
            vandaag_begin = datetime.datetime(tijd.year, tijd.month, tijd.day).timestamp()
            max_seconden_uitgeleend = 24 * 3600 * max_dagen_uitgeleend
            query += 'and ? - uitgeleend < ? '
            arguments.append(vandaag_begin)
            arguments.append(max_seconden_uitgeleend)

        if len(arguments) > 0:
            cursor.execute(query, arguments)
        else:
            cursor.execute(query)

        result = list()
        ditmoment = nu()
        for rec in cursor:
            uitleendatum = datetime.date.fromtimestamp(rec['uitgeleend'])
            if rec['teruggebracht']:
                terugbrengdatum = datetime.date.fromtimestamp(rec['teruggebracht'])
                rec['leendagen'] = (terugbrengdatum - uitleendatum).days
            else:
                vandaag = datetime.date.fromtimestamp(ditmoment)
                rec['leendagen'] = (vandaag - uitleendatum).days
            rec['uitleentijd'] = tijdstring(rec['uitgeleend'])
            rec['terugbrengtijd'] = tijdstring(rec['teruggebracht']) if rec['teruggebracht'] else None
            result.append(rec)

        result.sort(reverse=True, key=lambda r: r['leendagen'])
        return result

    def create_barcodes_table_if_not_exists(self):
        self.db.execute('''
            create table if not exists barcodes (
                isbn text primary key not null unique,
                printtime int,
                notes text
            )''')
        self.db.execute('create index if not exists barcodes_printtime on barcodes (printtime)')
        self.db.execute('create index if not exists barcodes_notes on barcodes (notes)')
        self.db.commit()

    def get_barcodes_where_clause(self, with_book=None, printed=None, with_notes=None):   # false, true or None
        sql = ' '  # start with space: safe to append to other string
        if with_book == False:    # note: not None
            sql += 'where isbn not in (select isbn from boek) '
        elif with_book == True:
            sql += 'where isbn in (select isbn from boek) '
        else:
            sql += 'where 1 '

        if printed == False:      # note: not None
            sql += 'and printtime is null '
        elif printed == True:
            sql += 'and printtime is not null '

        if with_notes == False:   # note: not None
            sql += 'and notes is null '
        elif with_notes == True:
            sql += 'and notes is not null '
        return sql

    def get_barcode_record(self, barcode):
        cursor = self.db.cursor()
        cursor.execute("select isbn, printtime, notes from barcodes where isbn=?", (barcode,))
        return cursor.fetchone()

    def get_barcodes(self, with_book=None, printed=None, with_notes=None):   # false, true or None
        sql = '''
            select isbn, printtime, notes
            from barcodes
        '''
        sql += self.get_barcodes_where_clause(with_book, printed, with_notes)
        sql += 'order by isbn'
        cursor = self.db.cursor()
        cursor.execute(sql)
        result = list()
        for rec in cursor:
            r = dict(rec)
            r['printtime'] = tijdstring(rec['printtime'])
            result.append(r)
        return result

    def get_latest_custom_barcode(self):
        sql = 'select min(isbn) as isbn from barcodes'
        sql += self.get_barcodes_where_clause(with_book=False, printed=None, with_notes=None)

        cursor = self.db.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        return result

    def create_new_barcodes(self, num=1):
        latest_barcode = self.get_latest_custom_barcode()
        if latest_barcode and latest_barcode['isbn']:
            start = int(latest_barcode['isbn'][:12]) - 1
            new_codes = barcode.generate_isbn_codes(str(start), num)
        else:
            new_codes = barcode.generate_isbn_codes(num=num)

        for code in new_codes:
            self.db.execute('insert into barcodes values (?, null, null)', (code,))
        self.db.commit()

    def mark_barcode_printed(self, code):
        sql = '''
            update barcodes
            set printtime=?
            where isbn=?
        '''
        self.db.execute(sql, (nu(), code))
        self.db.commit()

    def set_barcode_record(self, code, notes):
        sql = '''
            insert into barcodes(isbn, printtime, notes)
            values (?, null, ?)
            on conflict(isbn) do update
            set notes=?, printtime = null
            where isbn=?
        '''
        self.db.execute(sql, (code, notes, notes, code))
        self.db.commit()

    def delete_barcode_record(self, code):
        sql = 'delete from barcodes where isbn = ?'
        self.db.execute(sql, (code,))
        self.db.commit()

