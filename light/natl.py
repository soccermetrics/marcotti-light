from copy import deepcopy

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr, declarative_base

import light.common as lc
import light.common.models as lcm


NatlSchema = declarative_base(name="National Teams", metadata=lc.BaseSchema.metadata,
                              class_registry=deepcopy(lc.BaseSchema._decl_class_registry))


class NationalMixin(object):

    @declared_attr
    def team_id(cls):
        return Column(Integer, ForeignKey('countries.id'))


class NationalMatchMixin(object):

    @declared_attr
    def home_team_id(cls):
        return Column(Integer, ForeignKey('countries.id'))

    @declared_attr
    def away_team_id(cls):
        return Column(Integer, ForeignKey('countries.id'))


class FriendlyMixin(object):

    @declared_attr
    def home_team(cls):
        return relationship('Countries', foreign_keys="{}.home_team_id".format(cls.__name__),
                            backref=backref('home_friendly_matches'))

    @declared_attr
    def away_team(cls):
        return relationship('Countries', foreign_keys="{}.away_team_id".format(cls.__name__),
                            backref=backref('away_friendly_matches'))


class GroupMixin(object):

    @declared_attr
    def home_team(cls):
        return relationship('Countries', foreign_keys="{}.home_team_id".format(cls.__name__),
                            backref=backref('home_group_matches'))

    @declared_attr
    def away_team(cls):
        return relationship('Countries', foreign_keys="{}.away_team_id".format(cls.__name__),
                            backref=backref('away_group_matches'))


class KnockoutMixin(object):

    @declared_attr
    def home_team(cls):
        return relationship('Countries', foreign_keys="{}.home_team_id".format(cls.__name__),
                            backref=backref('home_knockout_matches'))

    @declared_attr
    def away_team(cls):
        return relationship('Countries', foreign_keys="{}.away_team_id".format(cls.__name__),
                            backref=backref('away_knockout_matches'))


class ShootoutMixin(object):

    @declared_attr
    def home_team(cls):
        return relationship('Countries', foreign_keys="{}.home_team_id".format(cls.__name__),
                            backref=backref('home_shootout_matches'))

    @declared_attr
    def away_team(cls):
        return relationship('Countries', foreign_keys="{}.away_team_id".format(cls.__name__),
                            backref=backref('away_shootout_matches'))


class DeductionMixin(object):
    @declared_attr
    def team(cls):
        return relationship('Countries', foreign_keys="{}.team_id".format(cls.__name__),
                            backref=backref('deductions'))


class NationalFriendlyMatches(FriendlyMixin, NationalMatchMixin, NatlSchema, lcm.FriendlyMatches):
    __tablename__ = "natl_friendly_matches"
    __mapper_args__ = {'polymorphic_identity': 'friendly'}

    id = Column(Integer, ForeignKey('friendly_matches.id'), primary_key=True)


class NationalGroupMatches(GroupMixin, NationalMatchMixin, NatlSchema, lcm.GroupMatches):
    __tablename__ = "natl_group_matches"
    __mapper_args__ = {'polymorphic_identity': 'group'}

    id = Column(Integer, ForeignKey('group_matches.id'), primary_key=True)


class NationalKnockoutMatches(KnockoutMixin, NationalMatchMixin, NatlSchema, lcm.KnockoutMatches):
    __tablename__ = "natl_knockout_matches"
    __mapper_args__ = {'polymorphic_identity': 'knockout'}

    id = Column(Integer, ForeignKey('knockout_matches.id'), primary_key=True)


class NationalShootoutMatches(ShootoutMixin, NationalMatchMixin, NatlSchema, lcm.MatchShootouts):
    __tablename__ = "natl_shootout_matches"
    id = Column(Integer, ForeignKey('match_shootouts.id'), primary_key=True)

    opener_id = Column(Integer, ForeignKey('countries.id'))
    opener = relationship('Countries', foreign_keys="NationalShootoutMatches.opener_id",
                          backref=backref('shootout_openers'))


class NationalDeductions(NationalMixin, NatlSchema, lcm.Deductions):
    __tablename__ = "natl_deductions"
    __mapper_args__ = {'polymorphic_identity': 'national'}

    id = Column(Integer, ForeignKey('deductions.id'), primary_key=True)

    team = relationship('Countries', foreign_keys="NationalDeductions.team_id", backref=backref('deductions'))
