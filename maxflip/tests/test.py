import unittest
import mock
from maxflip.tests.mongo_mock import MongoConnectionMock
from maxflip import Crawler
from functools import partial

class MaxFlipTests(unittest.TestCase):

    def setUp(self):
        self.patched_connection = mock.patch('pymongo.Connection', new=MongoConnectionMock)
        self.patched_connection.start()

    def test_mongo_mocker(self):
        from mock_collections import basic_collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = basic_collection
        results = crawler.collect('test_collection', {})
        results.run()

    def test_saving(self):
        from mock_collections import basic_collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = basic_collection
        results = crawler.collect('test_collection', {})
        results.add_task('rename', 'name', 'newname')
        results.run()
        result_items = [a.item for a in results.items]
        self.assertEqual(result_items, crawler.db['test_collection'])

    def test_dryrun(self):
        from mock_collections import basic_collection
        crawler = Crawler('test_db', dry_run=True)
        crawler.db['test_collection'] = basic_collection
        results = crawler.collect('test_collection', {})
        results.add_task('rename', 'name', 'newname')
        results.run()
        result_items = [a.item for a in results.items]
        self.assertNotEqual(result_items, crawler.db['test_collection'])

    def test_rename_key(self):
        from mock_collections import basic_collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = basic_collection
        results = crawler.collect('test_collection', {})
        results.add_task('rename', 'name', 'newname')
        results.run()
        self.assertIn('newname', results.items[0].item.keys())
        self.assertNotIn('name', results.items[0].item.keys())



if __name__ == '__main__':
    unittest.main()
