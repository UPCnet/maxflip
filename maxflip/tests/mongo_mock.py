# -*- coding: utf-8 -*-
from copy import deepcopy

class MongoCollectionMock(list):
    """
        A mock of a mongodb collection. Assumes the mock passed as the
        value of intialization is a list of dicts, each containing at least
        an _id attribute
    """
    def __init__(self, value):
        self.extend(value)

    def find(self, query):
        """
            Returns always all the items, ignores
            completely the query
        """
        return deepcopy(list(self))

    def save(self, item):
        """
            Updates the mocked collection item, matched by _id
        """
        for pos, element in enumerate(self):
            if element['_id'] == item['_id']:
                self[pos] = item


class MongoDatabaseMock(dict):
    """
    """
    def __init__(self, name):
        self.name = name

    def __getitem__(self, key):
        return dict.__getitem__(self, key)

    def __setitem__(self, key, val):
        """
            Allow only fields defined in schema to be inserted in the dict
            ignore non schema values
        """
        dict.__setitem__(self, key, MongoCollectionMock(val))


class MongoConnectionMock(dict):
    """
        PyMongo Database Connection Mock
    """

    def __init__(self, uri):
        """
        """
        self['test_db'] = MongoDatabaseMock('test_db')

