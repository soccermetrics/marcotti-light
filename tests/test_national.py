# coding=utf-8

import pytest
from datetime import date

import light.natl as ln
import light.common.models as lcm


natl_only = pytest.mark.skipif(
    pytest.config.getoption("--schema") != "natl",
    reason="Test only valid for national team databases"
)


@pytest.fixture
def natl_data():
    yr_2014 = lcm.Years(yr=2014)
    return {
        'date': date(2014, 7, 8),
        'competition': lcm.InternationalCompetitions(name=u'FIFA World Cup', level=1, 
                                                     confederation=lcm.Confederations(name=u"FIFA")),
        'season': lcm.Seasons(start_year=yr_2014, end_year=yr_2014),
        'home_team': lcm.Countries(name=u"Brazil", confederation=lcm.Confederations(name=u"CONMEBOL")),
        'away_team': lcm.Countries(name=u"Germany", confederation=lcm.Confederations(name=u"UEFA"))
    }


@natl_only
def test_natl_friendly_match_insert(session, natl_data):
    match = ln.NationalFriendlyMatches(**natl_data)
    session.add(match)

    friendly_match_from_db = session.query(ln.NationalFriendlyMatches).one()
    assert friendly_match_from_db.phase == "friendly"
    assert friendly_match_from_db.home_team.name == natl_data['home_team'].name
    assert friendly_match_from_db.away_team.name == natl_data['away_team'].name
    assert friendly_match_from_db.competition.name == natl_data['competition'].name

    match_from_db = session.query(lcm.FriendlyMatches).one()
    assert match_from_db.id == friendly_match_from_db.id


@natl_only
def test_natl_group_match_insert(session, natl_data):
    match = ln.NationalGroupMatches(
        group_round=lcm.GroupRounds(name=u"Group Stage"),
        group='A',
        matchday=1,
        **natl_data
    )
    session.add(match)

    group_match_from_db = session.query(ln.NationalGroupMatches).one()
    assert group_match_from_db.phase == "group"
    assert group_match_from_db.home_team.name == natl_data['home_team'].name
    assert group_match_from_db.away_team.name == natl_data['away_team'].name
    assert group_match_from_db.group == 'A'
    assert group_match_from_db.matchday == 1

    match_from_db = session.query(lcm.GroupMatches).one()
    assert match_from_db.id == group_match_from_db.id


@natl_only
def test_natl_knockout_match_insert(session, natl_data):
    match = ln.NationalKnockoutMatches(
        ko_round=lcm.KnockoutRounds(name=u"Semifinal"),
        matchday=1,
        **natl_data
    )
    session.add(match)

    knockout_match_from_db = session.query(ln.NationalKnockoutMatches).one()
    assert knockout_match_from_db.phase == "knockout"
    assert knockout_match_from_db.home_team.name == natl_data['home_team'].name
    assert knockout_match_from_db.away_team.name == natl_data['away_team'].name
    assert knockout_match_from_db.matchday == 1

    match_from_db = session.query(lcm.KnockoutMatches).one()
    assert match_from_db.id == knockout_match_from_db.id


@natl_only
def test_natl_shootout_match_insert(session, natl_data):
    match = ln.NationalKnockoutMatches(
        ko_round=lcm.KnockoutRounds(name=u"Semifinal"),
        matchday=1,
        **natl_data
    )
    session.add(match)

    match_from_db = session.query(lcm.Matches).one()
    shootout = ln.NationalShootoutMatches(
        id=match_from_db.id,
        opener=natl_data['home_team'],
        home_shootout_goals=5,
        away_shootout_goals=3
    )
    session.add(shootout)

    shootout_from_db = session.query(ln.NationalShootoutMatches).one()
    assert shootout_from_db.opener.name == natl_data['home_team'].name
    assert match_from_db.id == shootout_from_db.id


@natl_only
def test_natl_deduction(session, natl_data):
    deduction = ln.NationalDeductions(
        date=date(2014, 10, 31),
        points=3,
        competition=natl_data['competition'],
        season=natl_data['season'],
        team=natl_data['home_team']
    )
    session.add(deduction)

    deduction_from_db = session.query(ln.NationalDeductions).one()
    assert deduction_from_db.team.name == natl_data['home_team'].name
