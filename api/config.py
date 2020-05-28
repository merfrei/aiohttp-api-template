"""
Very basic config example
"""

import os


DEFAULT_ENVIRON = 'dev'


DEFAULT_CONFIG = {
    'API_URL': '/api/v1.0/',
    'DEBUG': False,
    'TESTING': False,
    'DATABASE_URI': 'postgresql://foo:1234@localhost:5432/foo',
    'API_KEY': 'AhHee~y5eip>oquo',
}


PRODUCTION = DEFAULT_CONFIG.copy()

DEVELOPMENT = DEFAULT_CONFIG.copy()
DEVELOPMENT['DEBUG'] = True

TESTING = DEFAULT_CONFIG.copy()
TESTING['TESTING'] = True
TESTING['DATABASE_URI'] = 'postgresql://foo:1234@localhost:5432/foo_testing'


CONFIG = {
    'dev': DEVELOPMENT,
    'test': TESTING,
    'prod': PRODUCTION,
}


def get_config():
    '''Get config object'''
    environ = DEFAULT_ENVIRON
    if 'API_ENVIRON' in os.environ:
        environ = os.environ['API_ENVIRON']
    return CONFIG[environ]
