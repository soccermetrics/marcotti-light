Marcotti-Light
==============

This is the implementation of the Light version of the Marcotti (formerly Football Match Result Database) models. The models are implemented as backend-independent SQLAlchemy objects, and club and national team databases are 
built from these objects.

Marcotti-Light captures full-time scorelines (and penalty shootout results if applicable) for teams participating 
in league, knockout, and group stage competitions, as well as friendly matches.  It also captures administrative
point deductions to teams, which is more applicable to league competitions but is kept general here.

Installation
------------

Marcotti-Light is written in Python and uses the SQLAlchemy package heavily.  Alembic is used to manage database
migrations.

While not required, [virtualenv](https://pypi.python.org/pypi/virtualenv) is strongly recommended and
[virtualenvwrapper](https://pypi.python.org/pypi/virtualenvwrapper) is very convenient.

Installation instructions:

1. Grab latest repo, setup the virtual environment, and install the dependent packages into it:

        $ git clone git://github.com/soccermetrics/marcotti-light.git
        $ cd marcotti-light
        $ mkvirtualenv light
        (light) $ pip install -r requirements.txt
    
2. Copy `light\config\local.skel` to `light\config\local.py` and populate it.  Alternative configuration
   settings can be created by subclassing `LocalConfig` and overwriting the attributes.
    
   ```python
   class LocalConfig(Config):
        # At a minimum, these variables must be defined.
        DIALECT = ''
        DBNAME = ''
        
        # For all other non-SQLite databases, these variables must be set.
        DBUSER = ''
        DBPASSWD = ''
        HOSTNAME = ''
        PORT = 5432
   ```
    
Common Tables
-------------

- Countries
- Confederations
- DomesticCompetitions
- InternationalCompetitions
- Seasons
- Years
- GroupRounds
- KnockoutRounds

Club Tables
-----------

- Clubs
- ClubFriendlyMatches
- ClubLeagueMatches
- ClubGroupMatches
- ClubKnockoutMatches
- ClubShootoutMatches
- ClubDeductions

National Team Tables
--------------------

- NationalFriendlyMatches
- NationalGroupMatches
- NationalKnockoutMatches
- NationalShootoutMatches
- NationalDeductions

To Do
-----

* Transition to Python 3

License
-------

(c) 2015-2016 Soccermetrics Research, LLC.  Created under MIT license.  See `LICENSE` file for details.
