from unittest import TestCase

import pyneric


class PascalizeTestCase(TestCase):

    func = staticmethod(pyneric.pascalize)

    def test_basic(self):
        name = 'basic_python_identifier'
        self.assertEqual('BasicPythonIdentifier', self.func(name))

    def test_no_underscore(self):
        name = 'nounderscore'
        self.assertEqual('Nounderscore', self.func(name))


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

    def test_no_underscore(self):
        name = 'Nounderscore'
        self.assertEqual('nounderscore', self.func(name))

    def test_consecutive_uppercase(self):
        name = 'IdentifierWITHMultipleUppers'
        self.assertEqual('identifier_with_multiple_uppers', self.func(name))

    def test_consecutive_uppercase_start(self):
        name = 'UPPERSAtStart'
        self.assertEqual('uppers_at_start', self.func(name))

    def test_consecutive_uppercase_end(self):
        name = 'UppersAtEND'
        self.assertEqual('uppers_at_end', self.func(name))


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
