import unittest
import mock
from maxflip.tests.mongo_mock import MongoConnectionMock
from maxflip import Crawler


class MaxFlipTests(unittest.TestCase):

    def setUp(self):
        self.patched_connection = mock.patch('pymongo.Connection', new=MongoConnectionMock)
        self.patched_connection.start()

    def test_mongo_mocker(self):
        from mock_collections import basic_collection as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})
        results.run()

    def test_saving(self):
        from mock_collections import basic_collection as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})

        results.add_task('rename', 'name', 'newname')

        results.run()
        result_items = [a for a in results]
        self.assertEqual(result_items, crawler.db['test_collection'])

    def test_dryrun(self):
        from mock_collections import basic_collection as collection
        crawler = Crawler('test_db', dry_run=True)
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})

        results.add_task('rename', 'name', 'newname')

        results.run()
        result_items = [a for a in results]
        self.assertNotEqual(result_items, crawler.db['test_collection'])

    # TEST ACTIONS

    def test_rename_key(self):
        from mock_collections import basic_collection as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})

        results.add_task('rename', 'name', 'newname')

        results.run()
        self.assertIn('newname', results[0].keys())
        self.assertNotIn('name', results[0].keys())
        self.assertEqual(collection[0]['name'], results[0]['newname'])

    def test_rename_subkey(self):
        from mock_collections import collection_subkey as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})

        results.add_task('rename', 'person.surname', 'name2')

        results.run()
        self.assertIn('name2', results[0]['person'].keys())
        self.assertNotIn('surname', results[0]['person'].keys())

    def test_rename_deep_subkey(self):
        from mock_collections import collection_subkey as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})

        results.add_task('rename', 'person.address.cp', 'postal_code')

        results.run()
        self.assertIn('postal_code', results[0]['person']['address'].keys())
        self.assertNotIn('cp', results[0]['person']['address'].keys())

    def test_delete_key(self):
        from mock_collections import basic_collection as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})

        results.add_task('delete', 'name')

        results.run()
        self.assertNotIn('name', results[0].keys())

    def test_delete_multiple_keys(self):
        from mock_collections import basic_collection as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})

        results.add_task('delete', ['name', 'nickname'])

        results.run()
        self.assertNotIn('name', results[0].keys())
        self.assertNotIn('nickname', results[0].keys())

    def test_delete_all_keys_except_one(self):
        from mock_collections import basic_collection as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})

        results.add_task('clean', ['_id'])

        results.run()
        self.assertEqual(['_id'], results[0].keys())

    def test_delete_all_keys_except_one_on_subkey(self):
        from mock_collections import collection_subkey as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})

        results.add_task('clean', ['name'], onkey='person')

        results.run()
        self.assertEqual(['name'], results[0]['person'].keys())

    def test_delete_subkey(self):
        from mock_collections import collection_subkey as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})

        results.add_task('delete', 'person.surname')

        results.run()
        self.assertNotIn('surname', results[0]['person'].keys())

    def test_delete_deep_subkey(self):
        from mock_collections import collection_subkey as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})

        results.add_task('delete', 'person.address.cp')

        results.run()
        self.assertNotIn('cp', results[0]['person']['address'].keys())

    def test_set_key(self):
        from mock_collections import basic_collection as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})

        results.add_task('set', 'number', 'vuit')

        results.run()
        self.assertEqual('vuit', results[0]['number'])

    def test_set_deep_key(self):
        from mock_collections import collection_subkey as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})

        results.add_task('set', 'person.surname', 'Locke')

        results.run()
        self.assertEqual('Locke', results[0]['person']['surname'])

    def test_set_key_default_overwrite(self):
        from mock_collections import basic_collection as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})
        results.add_task('set', 'name', 'Johnny')
        results.run()
        self.assertEqual('Johnny', results[0]['name'])

    def test_set_key_dont_overwrite(self):
        from mock_collections import basic_collection as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})
        results.add_task('set', 'name', 'Johnny', overwrite=False)
        results.run()
        self.assertEqual('John', results[0]['name'])

    def test_set_key_from_key(self):
        from mock_collections import basic_collection as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})
        results.add_task('set', 'name', fromkey='nickname')
        results.run()
        self.assertEqual(collection[0]['nickname'], results[0]['name'])

    def test_set_key_from_deep_key(self):
        from mock_collections import collection_subkey as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})
        results.add_task('set', 'person.nickname', fromkey='person.name')
        results.run()
        self.assertEqual(results[0]['person']['name'], results[0]['person']['nickname'])

    def test_replace_on_value_simple(self):
        from mock_collections import collection_subkey as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})

        results.add_task('replace', 'person.homepage', 'https', 'http')

        results.run()
        self.assertTrue(not results[0]['person']['homepage'].startswith('https'))
        self.assertTrue(not results[1]['person']['homepage'].startswith('https'))
        self.assertTrue(not results[2]['person']['homepage'].startswith('https'))

    def test_replace_on_value_regex(self):
        from mock_collections import collection_subkey as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})

        results.add_task('replace', 'person.homepage', 'http[^s]', 'https')

        results.run()
        self.assertTrue(results[0]['person']['homepage'].startswith('https'))
        self.assertTrue(results[1]['person']['homepage'].startswith('https'))
        self.assertTrue(results[2]['person']['homepage'].startswith('https'))

    def test_replace_on_value_regex_with_capture(self):
        from mock_collections import collection_subkey as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})

        results.add_task('replace', 'person.homepage', 'https://(\w+)\.\w+(\d)', 'https://\\1\\2')

        results.run()
        self.assertEqual(results[0]['person']['homepage'], collection[0]['person']['homepage'])
        self.assertEqual(results[2]['person']['homepage'], collection[2]['person']['homepage'])
        self.assertEqual(results[1]['person']['homepage'], 'https://foo2')

    def test_not_stacking_results(self):
        from mock_collections import collection_bug as collection
        crawler = Crawler('test_db', dry_run=True)
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})
        skills = results.add_subtask('contexts')
        skills.add_task('set', 'name', 'renamed')
        results.run()
        self.assertEqual(len(results[0]['contexts']), len(collection[0]['contexts']))
        self.assertEqual(len(results[1]['contexts']), len(collection[1]['contexts']))
        self.assertEqual(len(results[2]['contexts']), len(collection[2]['contexts']))

    # TEST SUBTASKS - Only testing one action here, previous action tests
    # are valid inside a subtask. if this fails, all actions in a subtask also will.

    def test_subtask(self):
        from mock_collections import collection_lists as collection
        crawler = Crawler('test_db')
        crawler.db['test_collection'] = collection
        results = crawler.collect('test_collection', {})
        skills = results.add_subtask('person.skills')
        skills.add_task('rename', 'name', 'skill_name')
        results.run()
        self.assertIn('skill_name', results[0]['person']['skills'][0].keys())
        self.assertNotIn('name', results[0]['person']['skills'][0].keys())

if __name__ == '__main__':
    unittest.main()
