## DEPS
from sqlalchemy import Table, Column, Integer, String, Date, \
         Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def get_engine(fn):
    from sqlalchemy import create_engine
    return create_engine('sqlite:///%s' % (fn,))#, echo=True)

Base = declarative_base()
class Entry(Base):
    __tablename__ = "entries"

    ##TODO: unique on url, podcast; index on url and podcast
    id = Column(Integer, Sequence('podcast_id_seq'), primary_key=True)

    url = Column(String(500))
    podcast = Column(String(200))

    title = Column(String(200))
    description = Column(String(10000))

    status = Column(Integer)

    def __init__(self, url, podcast, title, description):
        self.url = url
        self.podcast = podcast

        self.title = title
        self.description = description

        self.status = 0

    def __repr__(self):
        return "<Entry('%s')>" % (self.url,)

def get_table(fn):
    metadata = Entry.metadata
    metadata.bind = get_engine(fn)
    metadata.create_all()

    Session = sessionmaker(bind=metadata.bind)
    return (Entry, Session)
