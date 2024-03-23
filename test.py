bruh = {
    'key1': {
        'key2': {
            'key3': 'value'
        },
        'key22': {
            'key223': 'value22'
        }
    },
    '1key2': {
        '1key2': {
            '1key3': '1value'
        },
        '1key22': {
            '1key223': '1value22'
        }
    }
}

print(list(bruh['key1'].values()))