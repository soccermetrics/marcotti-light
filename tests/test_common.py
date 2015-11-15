# coding=utf-8
from datetime import date

import pytest
from sqlalchemy.exc import DataError, IntegrityError

import light.common.models as lcm


def test_confederation_insert(session):
    """Confederation 001: Insert a single record into Confederation table and verify data."""
    uefa = lcm.Confederations(name=u"UEFA")
    session.add(uefa)

    result = session.query(lcm.Confederations).filter_by(name=u"UEFA").one()
    assert result.name == u"UEFA"
    assert repr(result) == "<Confederation(id={0}, name=UEFA)>".format(result.id)


def test_confederation_overflow_error(session):
    """Confederation 002: Verify error if confederation name exceeds field length."""
    too_long_confederation = lcm.Confederations(name=u'ABCDEFGHIJKL')
    with pytest.raises(DataError):
        session.add(too_long_confederation)
        session.commit()


def test_country_insert(session):
        """Country 001: Insert a single record into Countries table and verify data."""
        england = lcm.Countries(name=u'England', confederation=lcm.Confederations(name=u'UEFA'))
        session.add(england)

        country = session.query(lcm.Countries).all()

        assert country[0].name == u'England'
        assert country[0].confederation.name == u'UEFA'
        assert repr(country[0]) == "<Country(id={0}, name=England, confed=UEFA)>".format(country[0].id)


def test_country_unicode_insert(session):
    """Country 002: Insert a single record with Unicode characters into Countries table and verify data."""
    ivory_coast = lcm.Countries(name=u"Côte d'Ivoire", confederation=lcm.Confederations(name=u'CAF'))
    session.add(ivory_coast)

    country = session.query(lcm.Countries).join(lcm.Confederations).filter(lcm.Confederations.name == u'CAF').one()

    assert country.name == u"Côte d'Ivoire"
    assert country.confederation.name == u'CAF'


def test_country_name_overflow_error(session):
    """Country 003: Verify error if country name exceeds field length."""
    too_long_name = "blahblah" * 8
    too_long_country = lcm.Countries(name=unicode(too_long_name), confederation=lcm.Confederations(name=u'CONCACAF'))
    with pytest.raises(DataError):
        session.add(too_long_country)
        session.commit()


def test_competition_insert(session):
    """Competition 001: Insert a single record into Competitions table and verify data."""
    record = lcm.Competitions(name=u"English Premier League", level=1)
    session.add(record)

    competition = session.query(lcm.Competitions).filter_by(level=1).one()

    assert competition.name == u"English Premier League"
    assert competition.level == 1


def test_competition_unicode_insert(session):
    """Competition 002: Insert a single record with Unicode characters into Competitions table and verify data."""
    record = lcm.Competitions(name=u"Süper Lig", level=1)
    session.add(record)

    competition = session.query(lcm.Competitions).one()

    assert competition.name == u"Süper Lig"


def test_competition_name_overflow_error(session):
    """Competition 003: Verify error if competition name exceeds field length."""
    too_long_name = "leaguename" * 9
    record = lcm.Competitions(name=unicode(too_long_name), level=2)
    with pytest.raises(DataError):
        session.add(record)
        session.commit()


def test_domestic_competition_insert(session):
    """Domestic Competition 001: Insert domestic competition record and verify data."""
    comp_name = u"English Premier League"
    comp_country = u"England"
    comp_confed = u"UEFA"
    comp_level = 1
    record = lcm.DomesticCompetitions(name=comp_name, level=comp_level, country=lcm.Countries(
        name=comp_country, confederation=lcm.Confederations(name=comp_confed)))
    session.add(record)

    competition = session.query(lcm.DomesticCompetitions).one()

    assert repr(competition) == "<DomesticCompetition(name={0}, country={1}, level={2})>".format(
        comp_name, comp_country, comp_level)
    assert competition.name == comp_name
    assert competition.level == comp_level
    assert competition.country.name == comp_country


def test_international_competition_insert(session):
    """International Competition 001: Insert international competition record and verify data."""
    comp_name = u"UEFA Champions League"
    comp_confed = u"UEFA"
    record = lcm.InternationalCompetitions(name=comp_name, level=1,
                                           confederation=lcm.Confederations(name=comp_confed))
    session.add(record)

    competition = session.query(lcm.InternationalCompetitions).one()

    assert repr(competition) == "<InternationalCompetition(name={0}, confederation={1})>".format(
        comp_name, comp_confed
    )
    assert competition.name == comp_name
    assert competition.level == 1
    assert competition.confederation.name == comp_confed


def test_year_insert(session):
    """Year 001: Insert multiple years into Years table and verify data."""
    years_list = range(1990, 1994)
    for yr in years_list:
        record = lcm.Years(yr=yr)
        session.add(record)

    years = session.query(lcm.Years.yr).all()
    years_from_db = [x[0] for x in years]

    assert set(years_from_db) & set(years_list) == set(years_list)


def test_year_duplicate_error(session):
    """Year 002: Verify error if year is inserted twice in Years table."""
    for yr in range(1992, 1995):
        record = lcm.Years(yr=yr)
        session.add(record)

    duplicate = lcm.Years(yr=1994)
    with pytest.raises(IntegrityError):
        session.add(duplicate)
        session.commit()


def test_season_insert(session):
    """Season 001: Insert records into Seasons table and verify data."""
    yr_1994 = lcm.Years(yr=1994)
    yr_1995 = lcm.Years(yr=1995)

    season_94 = lcm.Seasons(start_year=yr_1994, end_year=yr_1994)
    season_9495 = lcm.Seasons(start_year=yr_1994, end_year=yr_1995)
    session.add(season_94)
    session.add(season_9495)

    seasons_from_db = [repr(obj) for obj in session.query(lcm.Seasons).all()]
    seasons_test = ["<Season(1994)>", "<Season(1994-1995)>"]

    assert set(seasons_from_db) & set(seasons_test) == set(seasons_test)


def test_season_multiyr_search(session):
    """Season 002: Retrieve Season record using multi-year season name."""
    yr_1994 = lcm.Years(yr=1994)
    yr_1995 = lcm.Years(yr=1995)
    season_9495 = lcm.Seasons(start_year=yr_1994, end_year=yr_1995)
    session.add(season_9495)

    record = session.query(lcm.Seasons).filter(lcm.Seasons.name == '1994-1995').one()
    assert repr(season_9495) == repr(record)


def test_season_multiyr_reference_date(session):
    """Season 003: Verify that reference date for season across two years is June 30."""
    yr_1994 = lcm.Years(yr=1994)
    yr_1995 = lcm.Years(yr=1995)
    season_9495 = lcm.Seasons(start_year=yr_1994, end_year=yr_1995)
    session.add(season_9495)

    record = session.query(lcm.Seasons).filter(lcm.Seasons.start_year == yr_1994).one()
    assert record.reference_date == date(1995, 6, 30)


def test_season_singleyr_search(session):
    """Season 002: Retrieve Season record using multi-year season name."""
    yr_1994 = lcm.Years(yr=1994)
    season_94 = lcm.Seasons(start_year=yr_1994, end_year=yr_1994)
    session.add(season_94)

    record = session.query(lcm.Seasons).filter(lcm.Seasons.name == '1994').one()
    assert repr(season_94) == repr(record)


def test_season_singleyr_reference_date(session):
    """Season 005: Verify that reference date for season over one year is December 31."""
    yr_1994 = lcm.Years(yr=1994)
    season_94 = lcm.Seasons(start_year=yr_1994, end_year=yr_1994)
    session.add(season_94)

    record = session.query(lcm.Seasons).filter(lcm.Seasons.start_year == yr_1994).one()
    assert record.reference_date == date(1994, 12, 31)


def test_group_round_insert(session):
    """Group Rounds 001: Insert a single record into Group Rounds table and verify data."""
    grp_stage_name = u"Group Stage"
    grp_stage = lcm.GroupRounds(name=grp_stage_name)
    session.add(grp_stage)

    result = session.query(lcm.GroupRounds).filter_by(name=grp_stage_name).one()
    assert result.name == grp_stage_name
    assert repr(result) == "<GroupRound(name={0})>".format(grp_stage_name)


def test_group_round_name_overflow_error(session):
    """Group Rounds 002: Verify error if group round name exceeds field length."""
    too_long_name = "groupround" * 5
    record = lcm.GroupRounds(name=unicode(too_long_name))
    with pytest.raises(DataError):
        session.add(record)
        session.commit()


def test_knockout_round_insert(session):
    """Knockout Rounds 001: Insert a single record into Knockout Rounds table and verify data."""
    qfinal_name = u"Quarterfinal (1/4)"
    qfinal = lcm.KnockoutRounds(name=qfinal_name)
    session.add(qfinal)

    result = session.query(lcm.KnockoutRounds).filter_by(name=qfinal_name).one()
    assert result.name == qfinal_name
    assert repr(result) == "<KnockoutRound(name={0})>".format(qfinal_name)


def test_knockout_round_name_overflow_error(session):
    """Knockout Rounds 002: Verify error if knockout round name exceeds field length."""
    too_long_name = "knockoutround" * 5
    record = lcm.KnockoutRounds(name=unicode(too_long_name))
    with pytest.raises(DataError):
        session.add(record)
        session.commit()
