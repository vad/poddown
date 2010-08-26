#!/usr/bin/env python

## STDLIB
import os

## DEPS
from sqlalchemy import Table, Column, Integer, String, Date, \
         Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

## IN REPO
import feedparser

class Podcast(object):
    _name = None
    _source = None
    _open = None
    Entry = None

    def __init__(self, name, path, opts, Session):
        self._name = name
        dopts = dict(opts)

        if 'podcast' not in dopts:
            raise Exception, \
                  'You must specify podcast option for every podcast'

        if 'path' not in dopts:
            raise Exception, \
                  'You must specify "path" option for every podcast'

        self._source = dopts['podcast']
        self.Session = Session
        self._path = os.path.join(path, dopts['path'])

    def feed_to_store(self):
        data = feedparser.parse(self._source)
        session = self.Session()

        for entry in data['entries']:
            if session.query(Entry).filter(Entry.url == entry.link
                                    ).filter(Entry.podcast == self._name
                                    ).all():
                continue
            db_entry = Entry(entry.link, self._name, entry.title,
                             entry.description)
            session.add(db_entry)
            session.commit()

    def download(self):
        from urllib import urlretrieve, ContentTooShortError
        session = self.Session()

        ##TODO: status
        ##TODO: mkdir
        ##TODO: manage formats different from mp3
        for entry in session.query(Entry).filter(
            Entry.podcast == self._name).filter(Entry.status == 0).all():
            url = entry.url
            title = entry.title
            path = os.path.join(self._path, title+".mp3")
            try:
                urlretrieve(url, path)

                entry.status = 1
                session.commit()
            except ContentTooShortError:
                print 'Content too short for podcast', entry.podcast
                continue
            except IOError:
                print 'Can not connect to the server of podcast', entry.podcast

def get_engine():
    from sqlalchemy import create_engine
    return create_engine('sqlite:///prova.sqlite')#, echo=True)

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

def get_table():

    metadata = Entry.metadata
    metadata.bind = get_engine()
    metadata.create_all()

    Session = sessionmaker(bind=metadata.bind)
    return (Entry, Session)


def main():
    from ConfigParser import ConfigParser

    cp = ConfigParser()
    cp.read("poddown.cfg")

    Entry, Session = get_table()
    path = cp.get('poddown', 'path')
    for section in (section for section in cp.sections() if
                    section not in ('poddown',)):
        podcast = Podcast(section, path, cp.items(section), Session)
        podcast.feed_to_store()
        podcast.download()

if __name__ == "__main__":
    main()