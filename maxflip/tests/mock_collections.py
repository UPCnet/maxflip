basic_collection = [
    {
        '_id': 1,
        'name': 'John',
        'nickname': 'JL'
     }
]

collection_subkey = [
    {
        '_id': 1,
        'person': {
            'name': 'John',
            'surname': 'Dow',
            'address': {
                'city': 'Town',
                'cp': '01234'
            },
            'homepage': 'http://foo.bar'
        }
    },
    {
        '_id': 2,
        'person': {
            'name': 'John',
            'surname': 'Dow',
            'address': {
                'city': 'Town',
                'cp': '01234'
            },
            'homepage': 'https://foo.bar2'
        }
    },
    {
        '_id': 3,
        'person': {
            'name': 'John',
            'surname': 'Dow',
            'address': {
                'city': 'Town',
                'cp': '01234'
            },
            'homepage': 'http://foo.bar3'
        }
    }
]

collection_lists = [
    {
        '_id': 1,
        'person': {
            'skills': [
                {
                    'name': 'eat',
                    'level': 7,
                }
                ]
        }
    }
]


collection_bug = [
    {
        '_id': 1,
        'contexts': [{
            'url': 'a',
            'name': 'a',
        }]
    },
    {
        '_id': 2,
        'contexts': [{
            'url': 'b',
            'name': 'c',
        }]
    },
    {
        '_id': 3    ,
        'contexts': [{
            'url': 'c',
            'name': 'c',
        }]
    }
]
