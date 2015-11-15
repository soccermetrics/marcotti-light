# coding=utf-8

import pytest
from sqlalchemy.exc import DataError
from datetime import date

import light.club as lc
import light.common.models as lcm


club_only = pytest.mark.skipif(
    pytest.config.getoption("--schema") != "club",
    reason="Test only valid for club databases"
)


@pytest.fixture
def club_data():
    return {
        'date': date(2015, 1, 1),
        'competition': lcm.Competitions(name=u'Test Competition', level=1),
        'season': lcm.Seasons(start_year=lcm.Years(yr=2014), end_year=lcm.Years(yr=2015)),
        'home_team': lc.Clubs(name=u"Arsenal FC",
                              country=lcm.Countries(name=u"England", confederation=lcm.Confederations(name=u"UEFA"))),
        'away_team': lc.Clubs(name=u"Lincoln City FC",
                              country=lcm.Countries(name=u"England", confederation=lcm.Confederations(name=u"UEFA")))
    }


@club_only
def test_club_insert(session):
    club = lc.Clubs(name=u"Arsenal",
                    country=lcm.Countries(name=u"England", confederation=lcm.Confederations(name=u"UEFA")))
    session.add(club)

    result = session.query(lc.Clubs).one()
    assert result.name == u"Arsenal"
    assert repr(result) == "<Club(name=Arsenal, country=England)>"


@club_only
def test_club_unicode_insert(session):
    club = lc.Clubs(name=u"Фк Спартак Москва",
                    country=lcm.Countries(name=u"Russia", confederation=lcm.Confederations(name=u"UEFA")))
    session.add(club)

    result = session.query(lc.Clubs).join(lcm.Countries).filter(lcm.Countries.name == u"Russia").one()

    assert result.name == u"Фк Спартак Москва"
    assert unicode(result) == u"<Club(name=Фк Спартак Москва, country=Russia)>"


@club_only
def test_club_name_overflow(session):
    too_long_name = "blahblah" * 8
    too_long_club = lc.Clubs(name=too_long_name,
                             country=lcm.Countries(name=u"foo", confederation=lcm.Confederations(name=u"bar")))
    with pytest.raises(DataError):
        session.add(too_long_club)
        session.commit()


@club_only
def test_club_friendly_match_insert(session, club_data):
    match = lc.ClubFriendlyMatches(**club_data)
    session.add(match)

    friendly_match_from_db = session.query(lc.ClubFriendlyMatches).one()
    assert friendly_match_from_db.phase == "friendly"
    assert friendly_match_from_db.home_team.name == club_data['home_team'].name
    assert friendly_match_from_db.away_team.name == club_data['away_team'].name

    match_from_db = session.query(lcm.FriendlyMatches).one()
    assert match_from_db.id == friendly_match_from_db.id


@club_only
def test_club_league_match_insert(session, club_data):
    match = lc.ClubLeagueMatches(matchday=10, **club_data)
    session.add(match)

    league_match_from_db = session.query(lc.ClubLeagueMatches).one()
    assert league_match_from_db.phase == "league"
    assert league_match_from_db.home_team.name == club_data['home_team'].name
    assert league_match_from_db.away_team.name == club_data['away_team'].name
    assert league_match_from_db.matchday == 10

    match_from_db = session.query(lcm.LeagueMatches).one()
    assert match_from_db.id == league_match_from_db.id


@club_only
def test_club_group_match_insert(session, club_data):
    match = lc.ClubGroupMatches(
        group_round=lcm.GroupRounds(name=u"Group Stage"),
        group='A',
        matchday=1,
        **club_data
    )
    session.add(match)

    group_match_from_db = session.query(lc.ClubGroupMatches).one()
    assert group_match_from_db.phase == "group"
    assert group_match_from_db.home_team.name == club_data['home_team'].name
    assert group_match_from_db.away_team.name == club_data['away_team'].name
    assert group_match_from_db.group == 'A'
    assert group_match_from_db.matchday == 1

    match_from_db = session.query(lcm.GroupMatches).one()
    assert match_from_db.id == group_match_from_db.id


@club_only
def test_club_knockout_match_insert(session, club_data):
    match = lc.ClubKnockoutMatches(
        ko_round=lcm.KnockoutRounds(name=u"Semifinal"),
        matchday=1,
        **club_data
    )
    session.add(match)

    knockout_match_from_db = session.query(lc.ClubKnockoutMatches).one()
    assert knockout_match_from_db.phase == "knockout"
    assert knockout_match_from_db.home_team.name == club_data['home_team'].name
    assert knockout_match_from_db.away_team.name == club_data['away_team'].name
    assert knockout_match_from_db.matchday == 1

    match_from_db = session.query(lcm.KnockoutMatches).one()
    assert match_from_db.id == knockout_match_from_db.id


@club_only
def test_club_shootout_match_insert(session, club_data):
    match = lc.ClubKnockoutMatches(
        ko_round=lcm.KnockoutRounds(name=u"Semifinal"),
        matchday=1,
        **club_data
    )
    session.add(match)

    match_from_db = session.query(lcm.Matches).one()
    shootout = lc.ClubShootoutMatches(
        id=match_from_db.id,
        opener=club_data['home_team'],
        home_shootout_goals=5,
        away_shootout_goals=3
    )
    session.add(shootout)

    shootout_from_db = session.query(lc.ClubShootoutMatches).one()
    assert shootout_from_db.opener.name == club_data['home_team'].name
    assert match_from_db.id == shootout_from_db.id


@club_only
def test_club_deduction(session, club_data):
    deduction = lc.ClubDeductions(
        date=date(2014, 10, 31),
        points=3,
        competition=club_data['competition'],
        season=club_data['season'],
        team=club_data['home_team']
    )
    session.add(deduction)

    deduction_from_db = session.query(lc.ClubDeductions).one()
    assert deduction_from_db.team.name == club_data['home_team'].name
