# -*- coding: utf-8 -*-
from inspect import isfunction
import pymongo
import sys
import re


def safe_del_key(dic, key):
    if isinstance(dic, dict) and key in dic:
        del dic[key]


class Item(dict):
    """
    """

    def __init__(self, item, result_set):
        self.update(item)
        self.result_set = result_set
        self.variables = {}

    def delKey(self, key):
        leaf, key = self.getLeaf(key)
        safe_del_key(leaf, key)

    def getKeyValue(self, key):
        leaf, key = self.getLeaf(key)
        if leaf is key is None:
            return None
        return leaf.get(key, None)

    def setKeyValue(self, key, value):
        leaf, key = self.getLeaf(key)
        leaf[key] = value

    def getLeaf(self, key):
        parts = key.split('.')
        item = None
        for part in parts[:-1]:
            if item is None:
                if part not in self.keys():
                    return (None, None)
                item = self[part]
            else:
                if part not in item.keys():
                    return (None, None)
                item = item[part]

        return (self if item is None else item, parts[-1])

    def rename(self, old, new):
        leaf, key = self.getLeaf(old)
        if key in leaf:
            leaf[new] = leaf[key]
            del leaf[key]
            return True
        return False

    def set(self, key, *args, **kwargs):
        overwrite = kwargs.get('overwrite', True)
        fromkey = kwargs.get('fromkey', None)
        fromvar = kwargs.get('fromvar', None)
        if fromkey is not None:
            value = self.getKeyValue(fromkey)
        if fromvar is not None:
            params = fromvar.split('::')
            value = self.result_set.getVariable(*params)
        value = args[0] if fromkey is fromvar is None else value
        leaf, key = self.getLeaf(key)
        val = value
        if isfunction(value):
            val = value(self)
        if overwrite:
            leaf[key] = val
        else:
            leaf.setdefault(key, val)
        return True

    def replace(self, key, source, replacement):
        value = self.getKeyValue(key)
        source_regex = r'{}'.format(source)
        replacement_regex = r'{}'.format(replacement)
        if re.match(source_regex, value):
            newvalue = re.sub(source_regex, replacement_regex, value)
            return self.set(key, newvalue)
        return False

    def clean(self, keys_to_keep, onkey=None):
        dic = self if onkey is None else self.getKeyValue(onkey)
        for key in dic.keys():
            if key not in keys_to_keep:
                safe_del_key(dic, key)
        return True

    def delete(self, keys):
        if not isinstance(keys, list):
            keys = [keys, ]
        for key in keys:
            leaf, key = self.getLeaf(key)
            safe_del_key(leaf, key)
        return True

    def subtask(self, results, key):
        items = self.getKeyValue(key)
        if items:
            results.setItems(items)
            results.setParentItem(self)
            task_results = results.run()
            self.variables.update(results.variables)
            self.setKeyValue(key, results.getItems())
            return task_results

    def max(self, key):
        value = self.getKeyValue(key)
        last_value = self.result_set.getVariable('max', key)
        if last_value is None:
            self.result_set.setVariable('max', key, value)

        elif value > last_value:
            self.result_set.setVariable('max', key, value)

    def run_task(self, task):
        taskname, args, kwargs = task
        task_method = getattr(self, taskname)
        return task_method(*args, **kwargs)


class ResultSet(list):
    """
    """

    def __init__(self, database=None, collection=None, crawler=None):
        """
        """
        self.database = database
        self.collection = collection
        self.crawler = crawler
        self.parentItem = None
        self.tasks = []
        self.variables = {}

    def setParentItem(self, item):
        self.parentItem = item

    def setItems(self, items):
        del self[:]
        self.extend([Item(item, self) for item in items])

    def getItems(self):
        return [item for item in self]

    def getVariable(self, method, key):
        return self.variables.get('{}::{}'.format(method, key), None)

    def setVariable(self, method, key, value):
        self.variables['{}::{}'.format(method, key)] = value

    def clearVariable(self, method, key):
        safe_del_key(self.variables, '{}::{}'.format(method, key))

    def add_task(self, task, *args, **kwargs):
        self.tasks.append((task, args, kwargs))

    def save(self):
        if not self.crawler.dry_run:
            for item in self:
                self.database[self.collection].save(item)
            print 'Changes saved'
        else:
            print 'DRY RUN: Not saving any changes'

    def run(self):
        task_results = {}
        for itemnum, item in enumerate(self):
            item.variables.clear()
            for tasknum, task in enumerate(self.tasks):
                task_result = item.run_task(task)
                success = task_result not in [None, False, {}, []]
                self.variables.update(item.variables)
                task_target = task[1][1] if task[0] == 'subtask' else task[1][0]
                task_id = '{}_{}_{}'.format(tasknum, task[0], task_target)

                task_results.setdefault(task_id, {
                    True: 0,
                    False: 0,
                    'name': task[0],
                    'arguments': [task_target] if task[0] == 'subtask' else task[1]
                })
                task_results[task_id][success] += 1

        # Save only if the ResultSet is a root ResultSet
        # All the others result sets will end here after recursion

        if self.crawler:
            for taskid, taskdata in task_results.items():
                print 'Results of task {} "{}": Found: {}, Not found: {}'.format(taskdata['name'], taskdata['arguments'][0], taskdata[True], taskdata[False])
            self.save()
        else:
            return task_results

    def add_subtask(self, key):
        results_set = ResultSet()
        self.tasks.append(('subtask', (results_set, key), {}))
        return results_set


class Crawler(object):
    """
    """

    def __init__(self, database, hosts='localhost', port=27017, replica_set=None, dry_run=False):
        """
        """
        self.dry_run = dry_run
        self.cluster = isinstance(hosts, list) and replica_set is not None
        if isinstance(hosts, list) and replica_set is None:
            print 'You need to specify replica_set in cluster mode'
            sys.exit(1)

        # Check if we're connecting to a cluster
        if self.cluster:
            self.hosts = ','.join(hosts)
            self.replica_set = replica_set
            print 'Connecting to database @ cluster "{}" ...'.format(self.replica_set)
            self.connection = pymongo.MongoReplicaSetClient(','.join(hosts), replicaSet=replica_set)

        #Otherwise make a single connection
        else:
            self.uri = '{}:{}'.format(hosts, port)
            print 'Connecting to database @ {} ...'.format(self.uri)
            self.connection = pymongo.Connection(self.uri)

        self.db = self.connection[database]

    def collect(self, collection, query):
        """
        """
        results = self.db[collection].find(query)
        results_set = ResultSet(database=self.db, collection=collection, crawler=self)
        results_set.setItems(results)
        print '\nAdded {} items from {}/{}'.format(len(results_set), self.db.name, collection)
        return results_set
