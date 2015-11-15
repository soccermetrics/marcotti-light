from datetime import date

from sqlalchemy.schema import CheckConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import (Column, Boolean, Integer, String, Sequence,
                        ForeignKey, Unicode, Date, case, select, cast)

from light.common import BaseSchema


class Confederations(BaseSchema):
    """
    Football Confederations data model.
    """
    __tablename__ = "confederations"

    id = Column(Integer, Sequence('confed_id_seq', start=10, increment=1), primary_key=True)
    name = Column(Unicode(10))
    countries = relationship('Countries', backref=backref('confederation'))

    def __repr__(self):
        return "<Confederation(id={0}, name={1})>".format(self.id, self.name)


class Countries(BaseSchema):
    """
    Countries data model.

    Countries are defined as FIFA-affiliated national associations.
    """
    __tablename__ = "countries"

    id = Column(Integer, Sequence('country_id_seq', start=100), primary_key=True)
    name = Column(Unicode(60))
    confederation_id = Column(Integer, ForeignKey('confederations.id'))

    def __repr__(self):
        return "<Country(id={0}, name={1}, confed={2})>".format(self.id, self.name, self.confederation.name)


class Years(BaseSchema):
    """
    Years data model.
    """
    __tablename__ = "years"

    id = Column(Integer, Sequence('year_id_seq', start=100), primary_key=True)
    yr = Column(Integer, unique=True)


class Seasons(BaseSchema):
    """
    Seasons data model.
    """
    __tablename__ = "seasons"

    id = Column(Integer, Sequence('season_id_seq', start=100), primary_key=True)

    start_year_id = Column(Integer, ForeignKey('years.id'))
    end_year_id = Column(Integer, ForeignKey('years.id'))

    start_year = relationship('Years', foreign_keys=[start_year_id])
    end_year = relationship('Years', foreign_keys=[end_year_id])

    @hybrid_property
    def name(self):
        """
        List year(s) that make up season.  Seasons over calendar year will be of form YYYY;
        seasons over two years will be of form YYYY-YYYY.
        """
        if self.start_year.yr == self.end_year.yr:
            return str(self.start_year.yr)
        else:
            return "{0}-{1}".format(self.start_year.yr, self.end_year.yr)

    @name.expression
    def name(cls):
        """
        List year(s) that make up season.  Seasons over calendar year will be of form YYYY;
        seasons over two years will be of form YYYY-YYYY.

        This expression allows `name` to be used as a query parameter.
        """
        yr1 = select([Years.yr]).where(cls.start_year_id == Years.id).as_scalar()
        yr2 = select([Years.yr]).where(cls.end_year_id == Years.id).as_scalar()
        return cast(yr1, String) + case([(yr1 == yr2, '')], else_='-'+cast(yr2, String))

    @hybrid_property
    def reference_date(self):
        """
        Define the reference date that is used to calculate player ages.

        +------------------------+---------------------+
        | Season type            | Reference date      |
        +========================+=====================+
        | European (Split years) | 30 June             |
        +------------------------+---------------------+
        | Calendar-year          | 31 December         |
        +------------------------+---------------------+

        :return: Date object that expresses reference date.
        """
        if self.start_year.yr == self.end_year.yr:
            return date(self.end_year.yr, 12, 31)
        else:
            return date(self.end_year.yr, 6, 30)

    def __repr__(self):
        return "<Season({0})>".format(self.name)


class Competitions(BaseSchema):
    """
    Competitions common data model.
    """
    __tablename__ = "competitions"

    id = Column(Integer, Sequence('competition_id_seq', start=1000), primary_key=True)
    name = Column(Unicode(80))
    level = Column(Integer)
    discriminator = Column('type', String(20))

    __mapper_args__ = {'polymorphic_on': discriminator}


class DomesticCompetitions(Competitions):
    """
    Domestic Competitions data model, inherited from Competitions model.
    """
    __mapper_args__ = {'polymorphic_identity': 'domestic'}
    country_id = Column(Integer, ForeignKey('countries.id'))
    country = relationship('Countries', backref=backref('competitions'))

    def __repr__(self):
        return "<DomesticCompetition(name={0}, country={1}, level={2})>".format(
            self.name, self.country.name, self.level)


class InternationalCompetitions(Competitions):
    """
    International Competitions data model, inherited from Competitions model.
    """
    __mapper_args__ = {'polymorphic_identity': 'international'}
    confederation_id = Column(Integer, ForeignKey('confederations.id'))
    confederation = relationship('Confederations', backref=backref('competitions'))

    def __repr__(self):
        return "<InternationalCompetition(name={0}, confederation={1})>".format(self.name, self.confederation.name)


class KnockoutRounds(BaseSchema):
    """
    Knockout Rounds data model.
    """
    __tablename__ = "knockout_rounds"

    id = Column(Integer, Sequence('koround_id_seq', start=10), primary_key=True)
    name = Column(Unicode(40))

    def __repr__(self):
        return "<KnockoutRound(name={0})>".format(self.name)


class GroupRounds(BaseSchema):
    """
    Group Rounds data model.
    """
    __tablename__ = "group_rounds"

    id = Column(Integer, Sequence('grpround_id_seq', start=10), primary_key=True)
    name = Column(Unicode(40))

    def __repr__(self):
        return "<GroupRound(name={0})>".format(self.name)


class Matches(BaseSchema):
    """
    Football Matches common data model.
    """
    __tablename__ = "matches"

    id = Column(Integer, Sequence('match_id_seq', start=1000000), primary_key=True)

    date = Column(Date)
    home_goals = Column(Integer, default=0)
    away_goals = Column(Integer, default=0)
    phase = Column(String)

    competition_id = Column(Integer, ForeignKey('competitions.id'))
    season_id = Column(Integer, ForeignKey('seasons.id'))

    competition = relationship('Competitions', backref=backref('matches', lazy='dynamic'))
    season = relationship('Seasons', backref=backref('matches'))

    __mapper_args__ = {
        'polymorphic_identity': 'matches',
        'polymorphic_on': phase
    }

    __table_args__ = (
        CheckConstraint('home_goals >= 0', name='nonneg_home_goals'),
        CheckConstraint('away_goals >= 0', name='nonneg_away_goals'),
        {}
    )


class FriendlyMatches(Matches):
    """
    Friendly Matches data model, inherited from Matches model.
    """
    __tablename__ = 'friendly_matches'
    __mapper_args__ = {'polymorphic_identity': 'friendly'}

    id = Column(Integer, ForeignKey('matches.id'), primary_key=True)


class LeagueMatches(Matches):
    """
    League Matches data model, inherited from Matches model.
    """
    __tablename__ = 'league_matches'
    __mapper_args__ = {'polymorphic_identity': 'league'}

    id = Column(Integer, ForeignKey('matches.id'), primary_key=True)
    matchday = Column(Integer)


class GroupMatches(Matches):
    """
    Group Matches data model, inherited from Matches model.
    """
    __tablename__ = 'group_matches'
    __mapper_args__ = {'polymorphic_identity': 'group'}

    id = Column(Integer, ForeignKey('matches.id'), primary_key=True)
    matchday = Column(Integer)
    group = Column(String(length=2))

    group_round_id = Column(Integer, ForeignKey('group_rounds.id'))
    group_round = relationship('GroupRounds')


class KnockoutMatches(Matches):
    """
    Knockout Matches data model, inherited from Matches model.
    """
    __tablename__ = 'knockout_matches'
    __mapper_args__ = {'polymorphic_identity': 'knockout'}

    id = Column(Integer, ForeignKey('matches.id'), primary_key=True)
    matchday = Column(Integer)
    extra_time = Column(Boolean, default=False)

    ko_round_id = Column(Integer, ForeignKey('knockout_rounds.id'))
    ko_round = relationship('KnockoutRounds')


class MatchShootouts(BaseSchema):
    """
    Match Shootouts data model.
    """
    __tablename__ = "match_shootouts"

    id = Column(Integer, ForeignKey('matches.id'), primary_key=True)

    home_shootout_goals = Column(Integer, default=0)
    away_shootout_goals = Column(Integer, default=0)

    __table_args__ = (
        CheckConstraint('home_shootout_goals >= 0', name='nonneg_home_shootout'),
        CheckConstraint('away_shootout_goals >= 0', name='nonneg_away_shootout'),
        {}
    )


class Deductions(BaseSchema):
    """
    Administrative deductions data model.
    """
    __tablename__ = "deductions"

    id = Column(Integer, Sequence('deduct_id_seq', start=10000), primary_key=True)
    date = Column(Date)
    points = Column(Integer)
    type = Column(String)

    competition_id = Column(Integer, ForeignKey('competitions.id'))
    season_id = Column(Integer, ForeignKey('seasons.id'))

    competition = relationship('Competitions', backref=backref('deductions'))
    season = relationship('Seasons', backref=backref('deductions'))

    __mapper_args__ = {
        'polymorphic_identity': 'deductions',
        'polymorphic_on': type
    }
