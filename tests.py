#!env/bin/python
import os
from sqlite3 import IntegrityError
import unittest
from flask import Flask
from config import basedir
from app import app, db
from app.models import Entry
from app.utils import (
    fit_regex, validate_params,
    extract_user_id_attr_pairs,
    get_entries_from_database,
    allowed_file)
from app.models import Entry


class ValidationTestCase(unittest.TestCase):

    def test_empty_user_ids(self):
        self.assertFalse(fit_regex('', app.config['USER_IDS_REGEX']))
        self.assertTrue(fit_regex('1', app.config['USER_IDS_REGEX']))
        self.assertTrue(fit_regex('1,2,3', app.config['USER_IDS_REGEX']))

    def test_commas_user_ids(self):
        self.assertFalse(fit_regex(',1,2,3', app.config['USER_IDS_REGEX']))
        self.assertFalse(fit_regex('1,2,3,', app.config['USER_IDS_REGEX']))
        self.assertFalse(fit_regex('1,3,,2', app.config['USER_IDS_REGEX']))

    def test_spaces_user_ids(self):
        self.assertFalse(fit_regex(' 1', app.config['USER_IDS_REGEX']))
        self.assertFalse(fit_regex('1 ', app.config['USER_IDS_REGEX']))
        self.assertFalse(fit_regex('1, 2, 3, 4', app.config['USER_IDS_REGEX']))
        self.assertFalse(fit_regex(' 1, 2, 3', app.config['USER_IDS_REGEX']))
        self.assertFalse(fit_regex('1, 2, 3 ', app.config['USER_IDS_REGEX']))
        self.assertFalse(fit_regex(' ', app.config['USER_IDS_REGEX']))

    def test_forbidden_values_for_user_ids(self):
        self.assertFalse(fit_regex('asd,1,2,3', app.config['USER_IDS_REGEX']))
        self.assertFalse(fit_regex('1,asdf,2', app.config['USER_IDS_REGEX']))

    def test_empty_attributes(self):
        self.assertTrue(fit_regex('name,email,name,colors',
                                  app.config['ATTRIBUTES_REGEX']))
        self.assertFalse(fit_regex('', app.config['ATTRIBUTES_REGEX']))

    def test_commas_attributes(self):
        self.assertFalse(fit_regex(',name,email',
                                   app.config['ATTRIBUTES_REGEX']))
        self.assertFalse(fit_regex('age,email,',
                                   app.config['ATTRIBUTES_REGEX']))
        self.assertFalse(fit_regex('age,name,,email',
                                   app.config['ATTRIBUTES_REGEX']))

    def test_spaces_attributes(self):
        self.assertFalse(fit_regex(' name', app.config['ATTRIBUTES_REGEX']))
        self.assertFalse(fit_regex('name ', app.config['ATTRIBUTES_REGEX']))
        self.assertFalse(fit_regex('name, age, em, color',
                                   app.config['ATTRIBUTES_REGEX']))
        self.assertFalse(fit_regex(' name, age, email, clr',
                                   app.config['ATTRIBUTES_REGEX']))
        self.assertFalse(fit_regex('name, age, email ',
                                   app.config['ATTRIBUTES_REGEX']))
        self.assertFalse(fit_regex(' ',
                                   app.config['ATTRIBUTES_REGEX']))

    def test_csv_row_match(self):
        self.assertTrue(fit_regex('1,age,31',
                                  app.config['ALLOWED_CSV_ROW_FORMAT']))
        self.assertTrue(fit_regex('1,name,Ivan',
                                  app.config['ALLOWED_CSV_ROW_FORMAT']))
        self.assertFalse(fit_regex('1, name,Ivan',
                                   app.config['ALLOWED_CSV_ROW_FORMAT']))
        self.assertFalse(fit_regex('1,,name,Ivan',
                                   app.config['ALLOWED_CSV_ROW_FORMAT']))
        self.assertFalse(fit_regex('1,name,Ivan ',
                                   app.config['ALLOWED_CSV_ROW_FORMAT']))
        self.assertFalse(fit_regex('1,name,Ivan,',
                                   app.config['ALLOWED_CSV_ROW_FORMAT']))
        self.assertFalse(fit_regex('1,name, Ivan',
                                   app.config['ALLOWED_CSV_ROW_FORMAT']))
        self.assertFalse(fit_regex('1,name, name,Ivan',
                                   app.config['ALLOWED_CSV_ROW_FORMAT']))
        self.assertFalse(fit_regex('name,Ivan',
                                   app.config['ALLOWED_CSV_ROW_FORMAT']))
        self.assertFalse(fit_regex(' ',
                                   app.config['ALLOWED_CSV_ROW_FORMAT']))

    def test_allowed_filenames(self):
        self.assertTrue(allowed_file("data.csv"))
        self.assertFalse(allowed_file("data"))
        self.assertFalse(allowed_file("data.png"))
        self.assertFalse(allowed_file("data.tar"))
        self.assertFalse(allowed_file("data.png.zip.tar"))


class PairExtractionTestCase(unittest.TestCase):

    def test_extract_user_id_attr_pairs(self):
        user_ids_param = "1,2"
        attrs_param = "name,age"
        pairs = extract_user_id_attr_pairs(user_ids_param, attrs_param)
        self.assertEqual(pairs, [('1', 'name'), ('1', 'age'),
                                 ('2', 'name'), ('2', 'age')])


class DatabaseOperationsTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_integrity(self):
        e1 = Entry(1, "name", "Bob")
        e2 = Entry(1, "name", "Bob")
        db.session.add(e1)
        db.session.add(e1)
        self.assertRaises(IntegrityError, db.session.commit())

    def test_get_entries_from_database(self):
        e1 = Entry(1, "name", "Bob")
        e2 = Entry(2, "name", "Alice")
        e3 = Entry(3, "age", 31)
        e4 = Entry(3, "name", "Sam")
        e5 = Entry(1, "age", 21)
        e6 = Entry(4, "name", "Joe")
        e7 = Entry(2, "age", 19)
        db.session.add(e1)
        db.session.add(e2)
        db.session.add(e3)
        db.session.add(e4)
        db.session.add(e5)
        db.session.add(e6)
        db.session.add(e7)
        db.session.commit()
        pk_pairs = [(1, "name"), (12, "age")]
        entries = get_entries_from_database(pk_pairs)
        assert None in entries
        self.assertIsNot(None, entries)


if __name__ == '__main__':
    unittest.main()
