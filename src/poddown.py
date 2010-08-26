#!/usr/bin/env python

## STDLIB
import os

## LOCAL
import feedparser
from models import get_table, Entry

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

        ##TODO: manage formats different from mp3

        try:
            os.makedirs(self._path) ## check if exists
        except OSError:
            if not (os.path.exists(self._path) and os.path.isdir(self._path)):
                ## TODO: exit in a more elegant manner
                raise OSError, "%s or one of his parent is not a directory" % (
                    self._path,)
        for entry in session.query(Entry).filter(
            Entry.podcast == self._name).filter(Entry.status == 0).all():
            ##TODO: print only in verbose mode
            url = entry.url
            title = entry.title
            print 'downloading', title
            path = os.path.join(self._path, title+".mp3")
            try:
                ##TODO: manage 404
                urlretrieve(url, path)

                entry.status = 1
                session.commit()
            except ContentTooShortError:
                print 'Content too short for podcast', entry.podcast
                continue
            except IOError:
                print 'Can not connect to the server of podcast', entry.podcast


def main():
    from ConfigParser import ConfigParser

    cp = ConfigParser()
    cp.read("poddown.cfg")

    _, Session = get_table(cp.get('poddown', 'database'))
    path = cp.get('poddown', 'path')
    for section in (section for section in cp.sections() if
                    section not in ('poddown',)):
        podcast = Podcast(section, path, cp.items(section), Session)
        podcast.feed_to_store()
        podcast.download()

if __name__ == "__main__":
    main()