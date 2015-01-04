# -*- coding: utf-8 -*-
"""Tests for pyneric.util"""

from unittest import TestCase

import pyneric


class AddToAllTestMixin(object):

    func = staticmethod(pyneric.add_to_all)

    def tearDown(self):
        del globals()['__all__']

    def test_function(self):
        @self.func
        def a_test_function():
            return 'success'
        self.assertIn('a_test_function', globals()['__all__'])
        self.assertEqual('success', a_test_function())

    def test_class(self):
        @self.func
        class TestClass(object):
            result = property(lambda self: 'success')
        self.assertIn('TestClass', globals()['__all__'])
        self.assertIs(type, type(TestClass))
        self.assertEqual('success', TestClass().result)


class AddToAllListTestCase(AddToAllTestMixin, TestCase):

    def setUp(self):
        globals()['__all__'] = []


class AddToAllSetTestCase(AddToAllTestMixin, TestCase):

    def setUp(self):
        globals()['__all__'] = set()


class AddToAllTupleTestCase(AddToAllTestMixin, TestCase):

    def setUp(self):
        globals()['__all__'] = ()


class AddToAllInvalidTestCase(AddToAllTestMixin, TestCase):

    def setUp(self):
        globals()['__all__'] = object()

    def test_function(self):
        def a_test_function():
            return 'success'
        self.assertRaises(TypeError, self.func, a_test_function)

    def test_class(self):
        class TestClass(object):
            result = property(lambda self: 'success')
        self.assertRaises(TypeError, self.func, TestClass)


class GetFromDictOrObjectsTestCase(TestCase):

    func = staticmethod(pyneric.get_from_dict_or_objects)

    def setUp(self):
        self.data = dict(a='x')
        self.objects = (AddToAllListTestCase, AddToAllSetTestCase)

    def test_from_dict(self):
        self.assertEqual('x', self.func('a', self.data, self.objects))
        self.assertEqual(['a'], list(self.data.keys()))

    def test_pop_from_dict(self):
        self.assertEqual('x', self.func('a', self.data, self.objects, True))
        self.assertEqual({}, self.data)

    def test_from_objects(self):
        import inspect
        from future import utils
        method = inspect.ismethod if utils.PY2 else inspect.isfunction
        self.assertTrue(method(self.func('test_class', self.data,
                                         self.objects)))
        self.assertEqual(['a'], list(self.data.keys()))

    def test_not_found(self):
        self.assertRaises(KeyError, self.func, 'nonexistent', self.data,
                          self.objects)


class ModuleAttributesTestCase(TestCase):

    func = staticmethod(pyneric.module_attributes)

    def test_default(self):
        import module_for_testing_attributes as test_module
        expected = {'a', '_x'}
        self.assertEqual(expected, self.func(test_module))

    def test_use_all_true(self):
        import module_for_testing_attributes as test_module
        expected = {'a', '_x'}
        self.assertEqual(expected, self.func(test_module, use_all=True))

    def test_use_all_true__include_underscored(self):
        import module_for_testing_attributes as test_module
        expected = {'a', '_x'}
        self.assertEqual(expected, self.func(test_module, use_all=True,
                                             include_underscored=True))

    def test_use_all_false(self):
        import module_for_testing_attributes as test_module
        expected = {'a', 'b'}
        self.assertEqual(expected, self.func(test_module, use_all=False))

    def test_use_all_false__include_underscored(self):
        from future import utils
        import module_for_testing_attributes as test_module
        expected = {'a', 'b', '_x', '_y'}
        expected |= {'__all__', '__builtins__', '__doc__', '__file__',
                     '__name__', '__package__'}
        if not utils.PY2:
            expected |= {'__cached__', '__loader__'}
        actual = self.func(test_module, use_all=False,
                           include_underscored=True)
        if not utils.PY2:
            for possibility in ('__spec__', '__initializing__'):
                pyneric.tryf(actual.remove, possibility, _except=KeyError)
        self.assertEqual(expected, actual)

    def test_use_all_without_all(self):
        import importlib
        module = importlib.import_module(__name__)
        self.assertRaises(AttributeError, self.func, module, use_all=True)


class PascalizeTestCase(TestCase):

    func = staticmethod(pyneric.pascalize)

    def test_basic(self):
        name = 'basic_python_identifier'
        self.assertEqual('BasicPythonIdentifier', self.func(name))

    def test_validate_false(self):
        name = 'b@sic_python_identifier'
        self.assertEqual('B@sicPythonIdentifier',
                         self.func(name, validate=False))

    def test_no_underscore(self):
        name = 'nounderscore'
        self.assertEqual('Nounderscore', self.func(name))

    def test_type(self):
        name = str('basic_python_identifier')
        result = self.func(name)
        self.assertEqual('BasicPythonIdentifier', result)
        self.assertTrue(isinstance(result, str))

    def test_type_native_str(self):
        # for Python 2
        from future.utils import native_str
        self.assertEqual('Abc', self.func(native_str('abc')))

    def test_type_invalid(self):
        self.assertRaises(TypeError, self.func, object(), validate=False)


class TryfTestCase(TestCase):

    func = staticmethod(pyneric.tryf)

    def test_base_exception(self):
        # exception is caught
        self.assertIsNone(self.func(list, object))
        # no exception occurs
        self.assertEqual([], self.func(list, ()))

    def test_single_exception(self):
        # exception is caught
        self.assertIsNone(self.func(list, object, _except=TypeError))
        # no exception occurs
        self.assertEqual([], self.func(list, (), _except=TypeError))

    def test_multiple_exceptions(self):
        _except = (TypeError, ValueError)
        # exception is caught
        self.assertIsNone(self.func(int, 'a', _except=_except))
        self.assertIsNone(self.func(list, object, _except=_except))
        # no exception occurs
        self.assertEqual(1, self.func(int, '1', _except=_except))
        self.assertEqual([], self.func(list, (), _except=TypeError))

    def test_custom_return(self):
        value = object()
        # exception is caught
        self.assertEqual(value, self.func(list, object, _return=value))
        # no exception occurs
        self.assertEqual([], self.func(list, (), _return=value))


class UnderscoreTestCase(TestCase):

    func = staticmethod(pyneric.underscore)

    def test_basic(self):
        name = 'BasicPythonIdentifier'
        self.assertEqual('basic_python_identifier', self.func(name))

    def test_validate_false(self):
        name = 'B@sicPythonIdentifier'
        self.assertEqual('b@sic_python_identifier',
                         self.func(name, validate=False))

    def test_no_underscore(self):
        name = 'Nounderscore'
        self.assertEqual('nounderscore', self.func(name))

    def test_consecutive_uppercase(self):
        name = 'IdentifierWITHMultipleUppers'
        self.assertEqual('identifier_with_multiple_uppers', self.func(name))

    def test_consecutive_uppercase_multicap_false(self):
        name = 'IdentifierWITHMultipleUppers'
        self.assertEqual('identifier_w_i_t_h_multiple_uppers',
                         self.func(name, multicap=False))

    def test_consecutive_uppercase_start(self):
        name = 'UPPERSAtStart'
        self.assertEqual('uppers_at_start', self.func(name))

    def test_consecutive_uppercase_end(self):
        name = 'UppersAtEND'
        self.assertEqual('uppers_at_end', self.func(name))

    def test_type(self):
        name = str('BasicPythonIdentifier')
        result = self.func(name)
        self.assertEqual('basic_python_identifier', result)
        self.assertTrue(isinstance(result, str))

    def test_type_native_str(self):
        # for Python 2
        from future.utils import native_str
        self.assertEqual('abc', self.func(native_str('Abc')))

    def test_type_invalid(self):
        self.assertRaises(TypeError, self.func, object(), validate=False)


class ValidPythonIdentifierTestCase(TestCase):

    func = staticmethod(pyneric.valid_python_identifier)
    valid = 'valid_identifier', 'ValidIdentifier', 'inv2e_8vnvAnK', '__VaLiD'
    invalid = 'invalid ', 'isnt valid', '$invalid', 'inva.lid'

    def test_valid(self):
        for value in self.valid:
            self.assertTrue(self.func(value))
        self.assertTrue(self.func('.'.join(self.valid), dotted=True))
        self.assertTrue(self.func('isnt.a.keyword', dotted=True))

    def test_invalid(self):
        for value in self.invalid:
            self.assertFalse(self.func(value))
        self.assertFalse(self.func('is.a.keyword', dotted=True))

    def test_type_invalid(self):
        self.assertRaises(TypeError, self.func, object())

    def test_exception(self):
        value = self.invalid[0]
        self.assertRaises(ValueError, self.func, value, exception=True)
        class CustomException(Exception): pass
        self.assertRaises(CustomException, self.func, value,
                          exception=CustomException)
        class NotAnException(object): pass
        self.assertRaises(ValueError, self.func, value,
                          exception=NotAnException)
        NotAnException = 'true, but not an exception'
        self.assertRaises(ValueError, self.func, value,
                          exception=NotAnException)
