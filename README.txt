This is a Plock, a Grok-based front-end for Plone CMS using contentmirror to update content in a relational database.

Using it you can quickly deploy a purely SQL-based front-end to a Plone site quickly developed using Grok and Zope 3.

test.db is a SQLLite database for testing purposes.

Why not Plok? Plock is a song by the band Plone.

RUNNING THE EXAMPLE
-------------------

$ bin/buildout -v
$ cp test.db /tmp/contentmirror.db
$ bin/paster serve parts/etc/deploy.ini

Login and create a plock application.

RUNNING TESTS
-------------

bin/test -s plock 

AUTHOR
------

Jordan Baker <jbb@scryent.com>

TODO
----

- currently uses a private copy of megrok.rdb that allows for models to be based on SQLAlchemy's polymorphism.  Need to get this integrated into the public SVN.

- test.db needs to have a record for atdocument added to it so its complete.

