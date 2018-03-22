from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
user = Table('user', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('social_id', String(length=64), nullable=False),
    Column('nickname', String(length=64), nullable=False),
    Column('email', String(length=120)),
    Column('about_me', String(length=140)),
    Column('last_seen', DateTime),
    Column('password', String(length=64)),
    Column('failed_to_login', Integer),
    Column('deny_login', DateTime),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['deny_login'].create()
    post_meta.tables['user'].columns['failed_to_login'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['user'].columns['deny_login'].drop()
    post_meta.tables['user'].columns['failed_to_login'].drop()
