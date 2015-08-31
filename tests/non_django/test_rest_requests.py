# -*- coding: utf-8 -*-
"""Tests for pyneric.rest_requests"""

from future.utils import PY2

from unittest import TestCase
if PY2:
    from urllib import quote
else:
    from urllib.parse import quote

from pyneric import rest_requests


# The test root just has to be a valid URL.
ROOT = 'http://host.net/v1'


class RestResourceTestCase(TestCase):

    def test_init_invalid_abstract(self):
        self.assertRaises(TypeError, rest_requests.RestResource, ROOT)

    def test_init_invalid_url_path_type(self):
        bases = (rest_requests.RestResource,)
        attrs = dict(url_path=object())
        self.assertRaises(TypeError, type, 'Resource', bases, attrs)

    def test_init_invalid_url_path_empty(self):
        bases = (rest_requests.RestResource,)
        attrs = dict(url_path='')
        self.assertRaises(ValueError, type, 'Resource', bases, attrs)

    def test_init_invalid_url_path_encoding(self):
        bases = (rest_requests.RestResource,)
        attrs = dict(url_path=b'ab\xcd')
        self.assertRaises(ValueError, type, 'Resource', bases, attrs)

    def test_init_invalid_url_path_leading_slash(self):
        bases = (rest_requests.RestResource,)
        attrs = dict(url_path='/something')
        self.assertRaises(ValueError, type, 'Resource', bases, attrs)

    def test_init_invalid_container_class(self):
        bases = (rest_requests.RestResource,)
        attrs = dict(container_class=object())
        self.assertRaises(TypeError, type, 'Resource', bases, attrs)

    def test_init_url_path_unicode(self):
        PATH = u'resöurce'

        class Resource(rest_requests.RestResource):
            url_path = PATH

        self.assertEqual(PATH, Resource.url_path)

    def test_init_container_url(self):
        class Resource(rest_requests.RestResource):
            url_path = 'resource'

        obj = Resource(ROOT)
        self.assertEqual('{}/{}'.format(ROOT, Resource.url_path), obj.url)

    def test_init_container_url_trailing_slash(self):
        class Resource(rest_requests.RestResource):
            url_path = 'resource'

        obj = Resource(ROOT + '/')
        self.assertEqual('{}/{}/'.format(ROOT, Resource.url_path), obj.url)

    def test_init_container_url_and_path_trailing_slash(self):
        class Resource(rest_requests.RestResource):
            url_path = 'resource/'

        obj = Resource(ROOT + '/')
        self.assertEqual('{}/{}'.format(ROOT, Resource.url_path), obj.url)

    def test_init_container_url_invalid(self):
        class Resource(rest_requests.RestResource):
            url_path = 'resource'

        for bad_container in (Resource, 123, set()):
            self.assertRaises(ValueError, Resource, bad_container)

    def test_init_container_resource(self):
        class Container(rest_requests.RestResource):
            url_path = 'container'

        class Resource(rest_requests.RestResource):
            url_path = 'resource'
            container_class = Container

        obj = Resource(Container(ROOT))
        expected = '{}/{}/{}'.format(ROOT, Container.url_path,
                                     Resource.url_path)
        self.assertEqual(expected, obj.url)

    def test_init_container_resource_trailing_slash(self):
        class Container(rest_requests.RestResource):
            url_path = 'container/'

        class Resource(rest_requests.RestResource):
            url_path = 'resource'
            container_class = Container

        obj = Resource(Container(ROOT))
        expected = '{}/{}{}/'.format(ROOT, Container.url_path,
                                     Resource.url_path)
        self.assertEqual(expected, obj.url)

    def test_init_container_resource_invalid(self):
        class Container(rest_requests.RestResource):
            url_path = 'container'

        class Resource(rest_requests.RestResource):
            url_path = 'resource'
            container_class = Container

        for bad_container in (ROOT, Container, 'abc', 123, set()):
            self.assertRaises(ValueError, Resource, bad_container)

    def test_init_base_container_attribute_resolution(self):
        class Container(rest_requests.RestResource):
            url_path = 'container'

        class Resource(rest_requests.RestResource):
            url_path = 'resource'
            container_class = Container

        container = Container(ROOT)
        obj = Resource(container)
        self.assertEqual(obj.container_, container)
        self.assertFalse(hasattr(obj, 'container__'))

        # again with "container_" existing
        class Resource1(rest_requests.RestResource):
            url_path = 'resource'
            container_class = Container
            container_ = 'blah'

        obj = Resource1(container)
        self.assertEqual(obj.container__, container)
        self.assertFalse(hasattr(Resource1(Container(ROOT)), 'container___'))

    def test_init_container_reference_attribute(self):
        class Container(rest_requests.RestResource):
            url_path = 'container'
            reference_attribute = 'the_container'

        class Resource(rest_requests.RestResource):
            url_path = 'resource'
            container_class = Container

        container = Container(ROOT)
        obj = Resource(container)
        self.assertEqual(obj.container, container)
        self.assertFalse(hasattr(obj, 'container_'))
        self.assertEqual(obj.the_container, container)

    def test_init_invalid_reference_attribute(self):
        bases = (rest_requests.RestResource,)
        attrs = dict(url_path='resource',
                     reference_attribute='not-a-python-identifier')
        self.assertRaises(ValueError, type, 'Resource', bases, attrs)
        attrs = dict(url_path='resource',
                     reference_attribute=object())
        self.assertRaises(TypeError, type, 'Resource', bases, attrs)

    def test_from_url(self):
        class Resource(rest_requests.RestResource):
            url_path = 'resource'

        url = '{}/{}'.format(ROOT, Resource.url_path)
        obj = Resource.from_url(url)
        self.assertIsInstance(obj.container, basestring if PY2 else str)
        self.assertEqual(obj.container, ROOT)

    def test_from_url_container(self):
        class Container(rest_requests.RestResource):
            url_path = 'container'

        class Resource(rest_requests.RestResource):
            url_path = 'resource'
            container_class = Container

        url = '{}/{}/{}'.format(ROOT, Container.url_path, Resource.url_path)
        obj = Resource.from_url(url)
        self.assertIsInstance(obj.container_, Container)
        self.assertEqual(obj.container_.container, ROOT)

    def test_from_url_trailing_slash_container(self):
        class Container(rest_requests.RestResource):
            url_path = 'container/'

        class Resource(rest_requests.RestResource):
            url_path = 'resource'
            container_class = Container

        url = '{}/{}{}'.format(ROOT, Container.url_path, Resource.url_path)
        obj = Resource.from_url(url)
        self.assertIsInstance(obj.container_, Container)
        self.assertEqual(obj.container_.container, ROOT)

    def test_from_url_trailing_slash_container_not_url(self):
        class Container(rest_requests.RestResource):
            url_path = 'container/'

        class Resource(rest_requests.RestResource):
            url_path = 'resource'
            container_class = Container

        url = '{}/{}{}'.format(ROOT, Container.url_path, Resource.url_path)
        obj = Resource.from_url(url.rstrip('/'))
        self.assertIsInstance(obj.container_, Container)
        self.assertEqual(obj.container_.container, ROOT)

    def test_from_url_trailing_slash_resource(self):
        class Container(rest_requests.RestResource):
            url_path = 'container'

        class Resource(rest_requests.RestResource):
            url_path = 'resource/'
            container_class = Container

        url = '{}/{}/{}'.format(ROOT, Container.url_path, Resource.url_path)
        obj = Resource.from_url(url)
        self.assertIsInstance(obj.container_, Container)
        self.assertEqual(obj.container_.container, ROOT)

    def test_from_url_trailing_slash_both(self):
        class Container(rest_requests.RestResource):
            url_path = 'container/'

        class Resource(rest_requests.RestResource):
            url_path = 'resource/'
            container_class = Container

        url = '{}/{}{}'.format(ROOT, Container.url_path, Resource.url_path)
        obj = Resource.from_url(url)
        self.assertIsInstance(obj.container_, Container)
        self.assertEqual(obj.container_.container, ROOT)

    def test_from_url_invalid(self):
        class Resource(rest_requests.RestResource):
            url_path = 'resource'

        self.assertRaises(ValueError, Resource.from_url, 'invalid://url')

    def test_methods_with_or_without_url_parameter(self):
        class Resource(rest_requests.RestResource):
            url_path = 'a'

        obj = Resource(ROOT)
        # These are valid, pass-through methods.
        for attr in ('get', 'post', 'head', 'options'):
            self.assertTrue(hasattr(obj, attr))
        # This is a function in the requests module with no "url" parameter.
        self.assertFalse(hasattr(obj, 'session'))
        # This is not a function in the requests module.
        self.assertFalse(hasattr(obj, 'refrigerator'))

    def test_metadata(self):
        class Resource0(rest_requests.RestResource):
            url_path = 'a'

        class Resource1(rest_requests.RestResource):
            url_path = 'b'

        self.assertEqual('a', Resource0.url_path)
        self.assertEqual('b', Resource1.url_path)


class RestCollectionTestCase(TestCase):

    def test_init_collection(self):
        class Collection(rest_requests.RestCollection):
            url_path = 'things'

        url = '{}/{}'.format(ROOT, Collection.url_path)
        self.assertEqual(url, Collection(ROOT).url)

    def test_init_member(self):
        class Collection(rest_requests.RestCollection):
            url_path = 'things'

        id_ = 'important thing'
        url = '{}/{}/{}'.format(ROOT, Collection.url_path, quote(id_))
        self.assertEqual(url, Collection(ROOT, id_).url)

    def test_init_member_unicode(self):
        class Collection(rest_requests.RestCollection):
            url_path = 'things'

        id_ = u'impörtant thing'
        url = u'{}/{}/{}'.format(ROOT, Collection.url_path,
                                 quote(id_.encode('utf-8') if PY2 else id_))
        self.assertEqual(url, Collection(ROOT, id_).url)

    def test_init_member_slash(self):
        class Collection(rest_requests.RestCollection):
            url_path = 'things'

        id_ = 'important/thing'
        url = '{}/{}/{}'.format(ROOT, Collection.url_path, quote(id_, safe=''))
        self.assertEqual(url, Collection(ROOT, id_).url)

    def test_init_invalid_id_type(self):
        bases = (rest_requests.RestCollection,)
        attrs = dict(id_type='not a class')
        self.assertRaises(TypeError, type, 'Collection', bases, attrs)

    def test_init_invalid_id_empty(self):
        class CustomType(object):
            def __init__(self, value):
                super(CustomType, self).__init__()

            def __str__(self):
                return ''

        class Collection(rest_requests.RestCollection):
            url_path = 'things'
            id_type = CustomType

        self.assertRaises(ValueError, Collection, ROOT, 'test')

    def test_from_url_member(self):
        class Container(rest_requests.RestCollection):
            url_path = 'things'

        class Resource(rest_requests.RestCollection):
            url_path = 'others'
            container_class = Container

        def inner_test(obj):
            self.assertIsInstance(obj.container_, Container)
            self.assertEqual(container_id, obj.container_.id)
            self.assertEqual(ROOT, obj.container_.container)
            self.assertEqual(resource_id, obj.id)

        container_id = 'a thing'
        resource_id = 'an other'
        url = '{}/{}/{}/{}/{}'.format(ROOT, Container.url_path, container_id,
                                      Resource.url_path, resource_id)
        inner_test(Resource.from_url(url))

        # Test the same thing with a properly quoted URL.
        url = '{}/{}/{}/{}/{}'.format(ROOT, Container.url_path,
                                      quote(container_id), Resource.url_path,
                                      quote(resource_id))
        inner_test(Resource.from_url(url))

    def test_from_url_member_unicode(self):
        class Container(rest_requests.RestCollection):
            url_path = 'things'

        class Resource(rest_requests.RestCollection):
            url_path = 'others'
            container_class = Container

        def inner_test(obj):
            self.assertIsInstance(obj.container_, Container)
            self.assertEqual(container_id, obj.container_.id)
            self.assertEqual(ROOT, obj.container_.container)
            self.assertEqual(resource_id, obj.id)

        container_id = u'a thĩng'
        resource_id = u'anöther'
        url = u'{}/{}/{}/{}/{}'.format(ROOT, Container.url_path, container_id,
                                       Resource.url_path, resource_id)
        inner_test(Resource.from_url(url))

        # Test the same thing with a properly quoted URL.
        url = u'{}/{}/{}/{}/{}'.format(ROOT, Container.url_path,
                                       quote(container_id.encode('utf-8')
                                             if PY2 else container_id),
                                       Resource.url_path,
                                       quote(resource_id.encode('utf-8')
                                             if PY2 else resource_id))
        inner_test(Resource.from_url(url))

    def test_from_url_member_slash(self):
        class Collection(rest_requests.RestCollection):
            url_path = 'things'

        id_ = 'important/thing'
        url = '{}/{}/{}'.format(ROOT, Collection.url_path, quote(id_, safe=''))
        obj = Collection.from_url(url)
        self.assertEqual(ROOT, obj.container)
        self.assertEqual(id_, obj.id)

    def test_from_url_member_invalid_collection(self):
        class Collection(rest_requests.RestCollection):
            url_path = 'things'

        url = '{}/x/x'.format(ROOT)
        self.assertRaises(ValueError, Collection.from_url, url)

    def test_id_type_int(self):
        class Collection(rest_requests.RestCollection):
            url_path = 'things'
            id_type = int

        id_ = 2112
        url = '{}/{}/{}'.format(ROOT, Collection.url_path, id_)
        self.assertEqual(url, Collection(ROOT, id_).url)

    def test_from_url_member_invalid_type(self):
        class Collection(rest_requests.RestCollection):
            url_path = 'things'
            id_type = int

        id_ = 'not_an_integer'
        url = '{}/{}/{}'.format(ROOT, Collection.url_path, id_)
        self.assertRaises(ValueError, Collection.from_url, url)

    def test_from_url_ambiguous(self):
        class Collection(rest_requests.RestCollection):
            url_path = 'things'

        id_ = 'things'
        interpreted_root = '{}/{}'.format(ROOT, Collection.url_path)
        url = '{}/{}'.format(interpreted_root, id_)
        self.assertRaises(ValueError, Collection.from_url, url)

    def test_from_url_unambiguous_collection(self):
        class Collection(rest_requests.RestCollection):
            url_path = 'things'

        url = '{}/{}'.format(ROOT, Collection.url_path)
        obj = Collection.from_url(url)
        self.assertIsNone(obj.id)
        self.assertEqual(ROOT, obj.container)

    def test_from_url_unambiguous_collection_due_to_id_type(self):
        class Collection(rest_requests.RestCollection):
            url_path = 'things'
            id_type = int

        id_ = 'things'
        interpreted_root = '{}/{}'.format(ROOT, Collection.url_path)
        url = '{}/{}'.format(interpreted_root, id_)
        obj = Collection.from_url(url)
        self.assertIsNone(obj.id)
        self.assertEqual(interpreted_root, obj.container)

    def test_class_properties_access_from_instance(self):
        class Collection(rest_requests.RestCollection):
            url_path = 'things'
            id_type = int

        obj = Collection(ROOT)
        self.assertEqual(Collection.is_abstract, obj.is_abstract)
        self.assertEqual(Collection.url_path, obj.url_path)
        self.assertEqual(Collection.container_class, obj.container_class)
        self.assertEqual(Collection.id_type, obj.id_type)


class RestCallTestCase(TestCase):

    """This test case contains actual calls to public APIs.

    An Internet connection is required for these tests to pass.

    """

    HTTPBIN_ROOT = 'http://httpbin.org'

    def test_get_httpbin_user_agent(self):
        class UserAgent(rest_requests.RestResource):
            url_path = 'user-agent'

        user_agent = 'Mozilla, but not really'
        headers = {'User-Agent': user_agent,
                   'Accept': 'application/json'}
        response = UserAgent(self.HTTPBIN_ROOT).get(headers=headers)
        expected = {'user-agent': user_agent}
        self.assertEqual(expected, response.json())
