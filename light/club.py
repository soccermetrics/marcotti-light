from copy import deepcopy

from sqlalchemy import Column, Integer, Sequence, ForeignKey, Unicode
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr, declarative_base

import light.common as lc
import light.common.models as lcm


ClubSchema = declarative_base(name="Clubs", metadata=lc.BaseSchema.metadata,
                              class_registry=deepcopy(lc.BaseSchema._decl_class_registry))


class Clubs(ClubSchema):
    """
    Football club data model.
    """
    __tablename__ = 'clubs'

    id = Column(Integer, Sequence('club_id_seq', start=10000), primary_key=True)

    name = Column(Unicode(60))
    country_id = Column(Integer, ForeignKey('countries.id'))
    country = relationship('Countries', backref=backref('teams'))

    def __repr__(self):
        return "<Club(name={0}, country={1})>".format(self.name, self.country.name)

    def __unicode__(self):
        return u"<Club(name={0}, country={1})>".format(self.name, self.country.name)


class ClubMixin(object):

    @declared_attr
    def team_id(cls):
        return Column(Integer, ForeignKey('clubs.id'))


class ClubMatchMixin(object):

    @declared_attr
    def home_team_id(cls):
        return Column(Integer, ForeignKey('clubs.id'))

    @declared_attr
    def away_team_id(cls):
        return Column(Integer, ForeignKey('clubs.id'))


class FriendlyMixin(object):

    @declared_attr
    def home_team(cls):
        return relationship('Clubs', foreign_keys="{}.home_team_id".format(cls.__name__),
                            backref=backref('home_friendly_matches'))

    @declared_attr
    def away_team(cls):
        return relationship('Clubs', foreign_keys="{}.away_team_id".format(cls.__name__),
                            backref=backref('away_friendly_matches'))


class LeagueMixin(object):

    @declared_attr
    def home_team(cls):
        return relationship('Clubs', foreign_keys="{}.home_team_id".format(cls.__name__),
                            backref=backref('home_league_matches'))

    @declared_attr
    def away_team(cls):
        return relationship('Clubs', foreign_keys="{}.away_team_id".format(cls.__name__),
                            backref=backref('away_league_matches'))


class GroupMixin(object):

    @declared_attr
    def home_team(cls):
        return relationship('Clubs', foreign_keys="{}.home_team_id".format(cls.__name__),
                            backref=backref('home_group_matches'))

    @declared_attr
    def away_team(cls):
        return relationship('Clubs', foreign_keys="{}.away_team_id".format(cls.__name__),
                            backref=backref('away_group_matches'))


class KnockoutMixin(object):

    @declared_attr
    def home_team(cls):
        return relationship('Clubs', foreign_keys="{}.home_team_id".format(cls.__name__),
                            backref=backref('home_knockout_matches'))

    @declared_attr
    def away_team(cls):
        return relationship('Clubs', foreign_keys="{}.away_team_id".format(cls.__name__),
                            backref=backref('away_knockout_matches'))


class ShootoutMixin(object):

    @declared_attr
    def home_team(cls):
        return relationship('Clubs', foreign_keys="{}.home_team_id".format(cls.__name__),
                            backref=backref('home_shootout_matches'))

    @declared_attr
    def away_team(cls):
        return relationship('Clubs', foreign_keys="{}.away_team_id".format(cls.__name__),
                            backref=backref('away_shootout_matches'))


class DeductionMixin(object):
    @declared_attr
    def team(cls):
        return relationship('Clubs', foreign_keys="{}.team_id".format(cls.__name__),
                            backref=backref('deductions'))


class ClubFriendlyMatches(FriendlyMixin, ClubMatchMixin, ClubSchema, lcm.FriendlyMatches):
    __tablename__ = "club_friendly_matches"
    __mapper_args__ = {'polymorphic_identity': 'friendly'}

    id = Column(Integer, ForeignKey('friendly_matches.id'), primary_key=True)


class ClubLeagueMatches(LeagueMixin, ClubMatchMixin, ClubSchema, lcm.LeagueMatches):
    __tablename__ = "club_league_matches"
    __mapper_args__ = {'polymorphic_identity': 'league'}

    id = Column(Integer, ForeignKey('league_matches.id'), primary_key=True)


class ClubGroupMatches(GroupMixin, ClubMatchMixin, ClubSchema, lcm.GroupMatches):
    __tablename__ = "club_group_matches"
    __mapper_args__ = {'polymorphic_identity': 'group'}

    id = Column(Integer, ForeignKey('group_matches.id'), primary_key=True)


class ClubKnockoutMatches(KnockoutMixin, ClubMatchMixin, ClubSchema, lcm.KnockoutMatches):
    __tablename__ = "club_knockout_matches"
    __mapper_args__ = {'polymorphic_identity': 'knockout'}

    id = Column(Integer, ForeignKey('knockout_matches.id'), primary_key=True)


class ClubShootoutMatches(ShootoutMixin, ClubMatchMixin, ClubSchema, lcm.MatchShootouts):
    __tablename__ = "club_shootout_matches"
    id = Column(Integer, ForeignKey('match_shootouts.id'), primary_key=True)

    opener_id = Column(Integer, ForeignKey('clubs.id'))
    opener = relationship('Clubs', foreign_keys="ClubShootoutMatches.opener_id", backref=backref('shootout_openers'))


class ClubDeductions(ClubMixin, ClubSchema, lcm.Deductions):
    __tablename__ = "club_deductions"
    __mapper_args__ = {'polymorphic_identity': 'club'}

    id = Column(Integer, ForeignKey('deductions.id'), primary_key=True)

    team = relationship('Clubs', foreign_keys="ClubDeductions.team_id", backref=backref('deductions'))
