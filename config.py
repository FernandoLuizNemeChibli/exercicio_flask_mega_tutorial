from os import path

base_dir=path.abspath(path.dirname(__file__))

SQLALCHEMY_DATABASE_URI='sqlite:///'+path.join(base_dir,'app.db')
SQLALCHEMY_MIGRATE_REPO=path.join(base_dir,'db_repository')

WTF_CSFR_ENABLED=True
SECRET_KEY='you-will-never-guess'

OAUTH_CREDENTIALS={
    'facebook': {
        'id': '198030310617991',
        'secret': '2c5467c772dab4f1b783b7fd96e3ae0c'
    },
    'twitter': {
        'id': 'haYkr4cFLgzJ2OOXnehBFN8tr',
        'secret': 'Vv2RWrkeAoGg8afYE5iJiNIigXwvuUhSFixwil2UqTIsctlh7X'
    }
}

USERS_PER_PAGE=9
MAX_SEARCH_RESULTS=50

WHOOSH_BASE=path.join(base_dir,'search.db')
