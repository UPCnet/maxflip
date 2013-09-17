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
            }
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
