# -*- coding: utf-8 -*-
"""Tests for pyneric.django.db.models.fields.pguuid"""

import uuid
import warnings

try:
    from django.db import connection
    from django.test import TestCase
    from django_test_app import models
except ImportError:
    warnings.warn("The tests for pyneric.django.db.models.fields.pguuid will "
                  "not be run since the module is not functional in the "
                  "current Python environment.  Install the django-pguuid "
                  "dependencies to enable these tests.",
                  ImportWarning)
else:
    class AutoPgUuidTestCase(TestCase):

        def test_automatic_fill(self):
            obj = models.AutoPgUuidTest()
            obj.full_clean()
            obj.save()
            uuid.UUID(obj.uuid_field)
            self.assertEqual(obj.uuid_field, obj.pk)

        def test_foreign_key(self):
            obj = models.AutoPgUuidTest()
            obj.full_clean()
            obj.save()
            obj_with_fk = models.AutoPgUuidFkTest(autopguuid=obj)
            obj_with_fk.full_clean()
            obj_with_fk.save()
            self.assertEqual(obj.pk, obj_with_fk.autopguuid_id)

        def test_foreign_key_regression(self):
            obj = models.FkPatchTest(posint_field=2112)
            obj.full_clean()
            obj.save()
            self.assertIsInstance(obj.auto_field, int)
            self.assertEqual(obj.auto_field, obj.pk)
            obj_with_fk = models.AutoPgUuidFkTest(fk_auto=obj, fk_posint=obj)
            obj_with_fk.full_clean()
            obj_with_fk.save()
            self.assertEqual(obj_with_fk.fk_auto_id, obj.auto_field)
            self.assertEqual(obj_with_fk.fk_posint_id, obj.posint_field)

        def test_database_types(self):
            cursor = connection.cursor()

            expected = 'uuid'
            actual = sql_column_data_type(
                cursor, models.AutoPgUuidTest._meta.db_table,
                'uuid_field')
            self.assertEqual(expected, actual)
            actual = sql_column_data_type(
                cursor, models.AutoPgUuidFkTest._meta.db_table,
                'autopguuid_id')
            self.assertEqual(expected, actual)

            expected = 'smallint'
            actual = sql_column_data_type(
                cursor, models.FkPatchTest._meta.db_table,
                'posint_field')
            self.assertEqual(expected, actual)

            expected = 'integer'
            actual = sql_column_data_type(
                cursor, models.FkPatchTest._meta.db_table,
                'auto_field')
            self.assertEqual(expected, actual)
            actual = sql_column_data_type(
                cursor, models.AutoPgUuidFkTest._meta.db_table,
                'fk_auto_id')
            self.assertEqual(expected, actual)
            actual = sql_column_data_type(
                cursor, models.AutoPgUuidFkTest._meta.db_table,
                'fk_posint_id')
            self.assertEqual(expected, actual)


    def sql_column_data_type(cursor, table, column):
        sql = ("SELECT data_type FROM information_schema.columns"
               " WHERE table_name = %s AND column_name = %s;")
        cursor.execute(sql, (table, column))
        result = cursor.fetchall()
        count = len(result)
        if count != 1:
            raise Exception("{} columns matching table {!r} and column {!r}"
                            .format(count or "No", table, column))
        return result[0][0]
