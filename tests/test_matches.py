# coding=utf-8
from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError, DataError

from light.common.models import Competitions, Seasons, Years, GroupRounds, KnockoutRounds
from light.common.models import (Matches, FriendlyMatches, LeagueMatches,
                                 GroupMatches, KnockoutMatches, MatchShootouts, Deductions)


def test_match_generic_insert(session):
    match = Matches(
        date=date(2015, 1, 1),
        competition=Competitions(name=u'Test Competition', level=1),
        season=Seasons(start_year=Years(yr=2014), end_year=Years(yr=2015))
    )
    session.add(match)

    match_from_db = session.query(Matches).one()

    assert match_from_db.date == date(2015, 1, 1)
    assert match_from_db.home_goals == 0
    assert match_from_db.away_goals == 0
    assert match_from_db.phase == "matches"
    assert match_from_db.competition.name == u'Test Competition'
    assert match_from_db.season.name == '2014-2015'


def test_match_negative_home_goal_error(session):
    match = Matches(
        date=date(2015, 1, 1),
        competition=Competitions(name=u'Test Competition', level=1),
        season=Seasons(start_year=Years(yr=2014), end_year=Years(yr=2015)),
        home_goals=-1
    )
    with pytest.raises(IntegrityError):
        session.add(match)
        session.commit()


def test_match_negative_away_goal_error(session):
    match = Matches(
        date=date(2015, 1, 1),
        competition=Competitions(name=u'Test Competition', level=1),
        season=Seasons(start_year=Years(yr=2014), end_year=Years(yr=2015)),
        away_goals=-1
    )
    with pytest.raises(IntegrityError):
        session.add(match)
        session.commit()


def test_friendly_match_generic_insert(session):
    match = FriendlyMatches(
        date=date(2015, 1, 1),
        competition=Competitions(name=u'Test Competition', level=1),
        season=Seasons(start_year=Years(yr=2014), end_year=Years(yr=2015))
    )
    session.add(match)

    friendly_match_from_db = session.query(FriendlyMatches).one()
    assert friendly_match_from_db.phase == "friendly"

    match_from_db = session.query(Matches).one()
    assert match_from_db.id == friendly_match_from_db.id


def test_league_match_generic_insert(session):
    match = LeagueMatches(
        date=date(2015, 1, 1),
        competition=Competitions(name=u'Test Competition', level=1),
        season=Seasons(start_year=Years(yr=2014), end_year=Years(yr=2015)),
        matchday=10
    )
    session.add(match)

    league_match_from_db = session.query(LeagueMatches).one()
    assert league_match_from_db.phase == "league"
    assert league_match_from_db.matchday == 10

    match_from_db = session.query(Matches).one()
    assert match_from_db.id == league_match_from_db.id


def test_league_match_nonnumeric_matchday_error(session):
    match = LeagueMatches(
        date=date(2015, 1, 1),
        competition=Competitions(name=u'Test Competition', level=1),
        season=Seasons(start_year=Years(yr=2014), end_year=Years(yr=2015)),
        matchday='A'
    )
    with pytest.raises(DataError):
        session.add(match)
        session.commit()


def test_group_match_generic_insert(session):
    match = GroupMatches(
        date=date(2015, 1, 1),
        competition=Competitions(name=u'Test Competition', level=1),
        season=Seasons(start_year=Years(yr=2014), end_year=Years(yr=2015)),
        group_round=GroupRounds(name=u"Group Stage"),
        group='A',
        matchday=1
    )
    session.add(match)

    group_match_from_db = session.query(GroupMatches).one()
    assert group_match_from_db.phase == "group"
    assert group_match_from_db.group_round.name == u"Group Stage"
    assert group_match_from_db.group == 'A'
    assert group_match_from_db.matchday == 1

    match_from_db = session.query(Matches).one()
    assert match_from_db.id == group_match_from_db.id


def test_group_match_group_error(session):
    match = GroupMatches(
        date=date(2015, 1, 1),
        competition=Competitions(name=u'Test Competition', level=1),
        season=Seasons(start_year=Years(yr=2014), end_year=Years(yr=2015)),
        group_round=GroupRounds(name=u"Group Stage"),
        group='ABC',
        matchday=1
    )
    with pytest.raises(DataError):
        session.add(match)
        session.commit()


def test_knockout_match_generic_insert(session):
    match = KnockoutMatches(
        date=date(2015, 1, 1),
        competition=Competitions(name=u'Test Competition', level=1),
        season=Seasons(start_year=Years(yr=2014), end_year=Years(yr=2015)),
        ko_round=KnockoutRounds(name=u"First Round"),
        matchday=1
    )
    session.add(match)

    knockout_match_from_db = session.query(KnockoutMatches).one()
    assert knockout_match_from_db.phase == "knockout"
    assert knockout_match_from_db.ko_round.name == u"First Round"
    assert knockout_match_from_db.matchday == 1

    match_from_db = session.query(Matches).one()
    assert match_from_db.id == knockout_match_from_db.id


def test_match_shootouts_generic_insert(session):
    match = Matches(
        date=date(2015, 1, 1),
        competition=Competitions(name=u'Test Competition', level=1),
        season=Seasons(start_year=Years(yr=2014), end_year=Years(yr=2015)),
    )
    session.add(match)

    match_from_db = session.query(Matches).one()
    shootout = MatchShootouts(
        id=match_from_db.id,
        home_shootout_goals=5,
        away_shootout_goals=3
    )
    session.add(shootout)

    shootout_from_db = session.query(MatchShootouts).one()
    assert shootout_from_db.home_shootout_goals == 5
    assert shootout_from_db.away_shootout_goals == 3

    assert match_from_db.id == shootout_from_db.id


def test_match_shootout_negative_home_goal_error(session):
    match = Matches(
        date=date(2015, 1, 1),
        competition=Competitions(name=u'Test Competition', level=1),
        season=Seasons(start_year=Years(yr=2014), end_year=Years(yr=2015)),
    )
    session.add(match)
    match_from_db = session.query(Matches).one()

    shootout = MatchShootouts(
        id=match_from_db.id,
        home_shootout_goals=-1,
        away_shootout_goals=3
    )
    with pytest.raises(IntegrityError):
        session.add(shootout)
        session.commit()


def test_match_shootout_negative_away_goal_error(session):
    match = Matches(
        date=date(2015, 1, 1),
        competition=Competitions(name=u'Test Competition', level=1),
        season=Seasons(start_year=Years(yr=2014), end_year=Years(yr=2015)),
    )
    session.add(match)
    match_from_db = session.query(Matches).one()

    shootout = MatchShootouts(
        id=match_from_db.id,
        home_shootout_goals=1,
        away_shootout_goals=-3
    )
    with pytest.raises(IntegrityError):
        session.add(shootout)
        session.commit()


def test_point_deduction_insert(session):
    deduction = Deductions(
        date=date(2014, 10, 31),
        points=3,
        competition=Competitions(name=u'Test Competition', level=1),
        season=Seasons(start_year=Years(yr=2014), end_year=Years(yr=2015))
    )
    session.add(deduction)

    deduction_from_db = session.query(Deductions).one()

    assert deduction_from_db.date == date(2014, 10, 31)
    assert deduction_from_db.points == 3
    assert deduction_from_db.competition.name == u"Test Competition"
    assert deduction_from_db.season.name == '2014-2015'
