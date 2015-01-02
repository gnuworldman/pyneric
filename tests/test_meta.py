# -*- coding: utf-8 -*-
"""Tests for pyneric.meta"""

import inspect
from unittest import TestCase

from future.utils import with_metaclass

import pyneric


class MetadataBehaviourTestCase(TestCase):

    def test_invalid_metadata_attr(self):
        self.assertRaises(TypeError, pyneric.MetadataBehaviour,
                          metadata_attr=object())

    def test_invalid_propagate_attr(self):
        self.assertRaises(TypeError, pyneric.MetadataBehaviour,
                          propagate_attr=object())

    def test_invalid_base_override_attr(self):
        self.assertRaises(TypeError, pyneric.MetadataBehaviour,
                          base_override_attr=object())

    def test_invalid_storage_attr(self):
        self.assertRaises(TypeError, pyneric.MetadataBehaviour,
                          storage_attr=object())

    def test_invalid_storage_class(self):
        self.assertRaises(TypeError, pyneric.MetadataBehaviour,
                          storage_class=object())


class MetaclassTestCase(TestCase):

    def test_basic(self):
        a_value = object()
        class M(pyneric.Metaclass):
            __metadata__ = dict(a=a_value)
        class C(with_metaclass(M, object)):
            pass
        self.assertTrue(inspect.isdatadescriptor(M.a))
        expected = dict(a=a_value, __propagate__=set(), __base_overrides__={})
        self.assertEqual(expected, M._get_metadata())
        self.assertEqual(expected, C._get_metadata())
        self.assertEqual(a_value, C.a)
        obj = C()
        self.assertRaises(AttributeError, getattr, obj, 'a')
        new_value = object()
        self.assertRaises(AttributeError, setattr, C, 'a', new_value)
        # Test that a non-propagated metadata attribute is not affected by an
        # object's own attribute of the same name.
        obj.a = new_value
        self.assertEqual(new_value, obj.a)
        self.assertEqual(a_value, C.a)

    def test_basic_metadata_iterable(self):
        a_value = object()
        class M(pyneric.Metaclass):
            __metadata__ = ('a',)
            a = a_value
        class C(with_metaclass(M, object)):
            pass
        self.assertTrue(inspect.isdatadescriptor(M.a))
        expected = dict(a=a_value, __propagate__=set(), __base_overrides__={})
        self.assertEqual(expected, M._get_metadata())
        self.assertEqual(expected, C._get_metadata())
        self.assertEqual(a_value, C.a)
        obj = C()
        self.assertRaises(AttributeError, getattr, obj, 'a')
        new_value = object()
        self.assertRaises(AttributeError, setattr, C, 'a', new_value)
        # Test that a non-propagated metadata attribute is not affected by an
        # object's own attribute of the same name.
        obj.a = new_value
        self.assertEqual(new_value, obj.a)
        self.assertEqual(a_value, C.a)

    def test_validation(self):
        a_value = dict()
        class CustomException(Exception):
            """Exception for validation test"""
        class M(pyneric.Metaclass):
            __metadata__ = dict(a=a_value)
            @staticmethod
            def validate_a(value):
                if not isinstance(value, dict):
                    raise CustomException("must be a dict")
        class C(with_metaclass(M, object)):
            a = {'valid': 'dict'}
        self.assertRaises(CustomException, type, 'C',
                          (with_metaclass(M, object),),
                          dict(a={'invalid', 'set', 'not', 'a', 'dict'}))
        self.assertRaises(CustomException, type, 'C1', (C,),
                          dict(a={'invalid', 'set', 'not', 'a', 'dict'}))

    def test_validate_not_callable(self):
        a_value = dict()
        v_value = object()
        class M(pyneric.Metaclass):
            __metadata__ = dict(a=a_value)
            # The "validate_a" attribute is not a function, so "a" metadata is
            # not validated.
            validate_a = v_value
        class C(with_metaclass(M, object)):
            a = {'valid': 'dict'}
        # The value of "a" is not being validated, so it can be a set.
        class C1(with_metaclass(M, object)):
            a = {'set', 'not', 'a', 'dict'}
        class C2(C):
            a = {'set', 'not', 'a', 'dict'}

    def test_valid(self):
        a_value = object()
        b_value = object()
        c_value = object()
        d_value = object()
        class M(pyneric.Metaclass):
            __metadata__ = dict(a=None, b=None, c=c_value)
            __propagate__ = ('a', 'c')
            @property
            def c(cls):
                if hasattr(cls, 'x'):
                    return "different value"
                return cls._get_metadata('c')
        class C(with_metaclass(M, object)):
            a = a_value
            d = d_value
        self.assertTrue(inspect.isdatadescriptor(M.a))
        self.assertTrue(inspect.isdatadescriptor(M.b))
        self.assertTrue(inspect.isdatadescriptor(M.c))
        self.assertRaises(AttributeError, getattr, M, 'd')
        expected = dict(a=None, b=None, c=c_value, __propagate__={'a', 'c'},
                        __base_overrides__={})
        self.assertEqual(expected, M._get_metadata())
        expected.update(a=a_value)
        self.assertEqual(expected, C._get_metadata())
        self.assertEqual(a_value, C.a)
        self.assertIsNone(C.b)
        self.assertEqual(c_value, C.c)
        self.assertEqual(d_value, C.d)
        obj = C()
        self.assertEqual(a_value, obj.a)
        self.assertRaises(AttributeError, getattr, obj, 'b')
        self.assertEqual(c_value, obj.c)
        self.assertEqual(d_value, obj.d)
        obj.b = b_value
        new_value = object()
        self.assertRaises(AttributeError, setattr, C, 'a', new_value)
        self.assertRaises(AttributeError, setattr, C, 'b', new_value)
        self.assertRaises(AttributeError, setattr, C, 'c', new_value)
        C.d = new_value
        self.assertEqual(new_value, C.d)
        self.assertEqual(a_value, obj.a)
        self.assertEqual(b_value, obj.b)
        self.assertEqual(c_value, obj.c)
        self.assertEqual(new_value, obj.d)
        self.assertRaises(AttributeError, setattr, obj, 'a', new_value)
        obj.b = new_value
        self.assertRaises(AttributeError, setattr, obj, 'c', new_value)
        newer_value = object()
        obj.d = newer_value
        self.assertEqual(new_value, obj.b)
        self.assertEqual(newer_value, obj.d)
        self.assertEqual(c_value, C.c)
        C.x = None
        self.assertEqual('different value', C.c)

    def test_invalid_metadata_attribute(self):
        class M(pyneric.Metaclass):
            pass
        self.assertRaises(AttributeError, M._get_metadata, 'x')

    def test_invalid_metadata(self):
        self.assertRaises(TypeError, type, 'M', (pyneric.Metaclass,),
                          dict(__metadata__=object()))


class MetaclassCustomBehaviourTestCase(TestCase):

    def test_no_propagate_attr(self):
        behaviour = pyneric.MetadataBehaviour(propagate_attr=None)
        a_value = object()
        b_value = dict(a=None)
        p_value = {'a'}
        class M(pyneric.Metaclass):
            __metadata_behaviour__ = behaviour
            __metadata__ = dict(a=a_value)
            # Prove that __propagate__ is not part of metadata behaviour.
            __propagate__ = p_value
            # Prove that base overrides are not affected.
            __base_overrides__ = b_value
        class C(with_metaclass(M, object)):
            pass
        self.assertTrue(inspect.isdatadescriptor(M.a))
        # Note that there is no "__propagate__" attribute in the metadata.
        expected = dict(a=a_value, __base_overrides__=b_value)
        self.assertEqual(expected, M._get_metadata())
        expected.update(a=None)
        self.assertEqual(expected, C._get_metadata())
        # Prove that __propagate__ is not part of metadata behaviour.
        self.assertEqual(p_value, M.__propagate__)
        self.assertEqual(p_value, C.__propagate__)
        # Prove that base overrides are not affected.
        self.assertEqual(None, C.a)
        # Prove that propagation of "a" does not occur.
        self.assertRaises(AttributeError, getattr, C(), 'a')

    def test_no_base_override_attr(self):
        behaviour = pyneric.MetadataBehaviour(base_override_attr=None)
        a_value = object()
        b_value = dict(a=None)
        p_value = {'a'}
        class M(pyneric.Metaclass):
            __metadata_behaviour__ = behaviour
            __metadata__ = dict(a=a_value)
            # Prove that propagation is not affected.
            __propagate__ = p_value
            # Prove that __base_overrides__ is not part of metadata behaviour.
            __base_overrides__ = b_value
        class C(with_metaclass(M, object)):
            pass
        self.assertTrue(inspect.isdatadescriptor(M.a))
        # Note that there is no "__base_overrides__" attribute in the metadata.
        expected = dict(a=a_value, __propagate__=p_value)
        self.assertEqual(expected, M._get_metadata())
        self.assertEqual(expected, C._get_metadata())
        # Prove that __base_overrides__ is not part of metadata behaviour.
        self.assertEqual(b_value, M.__base_overrides__)
        self.assertEqual(b_value, C.__base_overrides__)
        # Prove that "a" was not overridden.
        self.assertEqual(a_value, C.a)
        # Prove that propagation is not affected.
        self.assertEqual(a_value, C().a)

    def test_validation_disabled(self):
        behaviour = pyneric.MetadataBehaviour(validate_prefix=None)
        a_value = dict()
        class M(pyneric.Metaclass):
            __metadata_behaviour__ = behaviour
            __metadata__ = dict(a=a_value)
            @staticmethod
            def validate_a(value):
                if not isinstance(value, dict):
                    raise TypeError("must be a dict")
        class C(with_metaclass(M, object)):
            a = {'valid': 'dict'}
        # The value of "a" is not being validated, so it can be a set.
        class C1(with_metaclass(M, object)):
            a = {'set', 'not', 'a', 'dict'}
        class C2(C):
            a = {'set', 'not', 'a', 'dict'}

    def test_metadata_behaviour_similar_to_django_model(self):
        class CustomMetadataBehaviour(pyneric.MetadataBehaviour):
            def __init__(self, storage_class, metadata_attr='Meta',
                         storage_attr='_meta', propagate_attr=None):
                super(CustomMetadataBehaviour, self).__init__(
                    metadata_attr=metadata_attr,
                    propagate_attr=propagate_attr,
                    storage_attr=storage_attr,
                    storage_class=storage_class)
            def _get_local_metadata(self, dict, base_attrs=()):
                """Django-like metadata retrieval function."""
                try:
                    meta_class = dict[self.metadata_attr]
                except KeyError:
                    return {}
                # Django does not currently test that it is a class.
                if not inspect.isclass(meta_class):
                    raise TypeError(
                        "The '{}' attribute must be a class."
                        .format(self.metadata_attr))
                result = {}
                for k, v in meta_class.__dict__.items():
                    if (k.startswith('_') and
                        k not in (self.propagate_attr,
                                  self.base_override_attr)):
                        continue
                    result[k] = v
                return result
        class MetadataStorage(object):
            def __init__(self, **kwargs):
                for attr, value in kwargs.items():
                    setattr(self, attr, value)
        class M(pyneric.Metaclass):
            __metadata_behaviour__ = CustomMetadataBehaviour(MetadataStorage)
            class Meta:
                app_label = None
                db_table = None
                abstract = False
                __base_overrides__ = dict(abstract=False)
        class C(with_metaclass(M, object)):
            class Meta:
                db_table = 'tbl'
                abstract = True
        class C1(C):
            class Meta:
                db_table = 'tbl1'
        self.assertEqual('tbl', C.db_table)
        self.assertEqual(True, C.abstract)
        self.assertEqual('tbl1', C1.db_table)
        self.assertEqual(False, C1.abstract)
