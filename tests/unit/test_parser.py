import pytest
from app.csv_parser import parse_geiger_csv

def test_parse_normal_line():
    line = "CPS, 1, CPM, 21, uSv/hr, 0.11, SLOW"
    rec = parse_geiger_csv(line)
    assert rec["cps"] == 1
    assert rec["cpm"] == 21
    assert rec["usv"] == 0.11
    assert rec["mode"] == "SLOW"


def test_parse_fast_mode():
    line = "CPS, 5, CPM, 50, uSv/hr, 0.05, FAST"
    rec = parse_geiger_csv(line)
    assert rec["mode"] == "FAST"


def test_parse_inst_mode():
    line = "CPS, 12, CPM, 120, uSv/hr, 0.12, INST"
    rec = parse_geiger_csv(line)
    assert rec["mode"] == "INST"


def test_parse_negative_usv_rejected():
    line = "CPS, 1, CPM, 21, uSv/hr, -0.11, SLOW"
    assert parse_geiger_csv(line) is None


def test_parse_malformed_returns_none():
    assert parse_geiger_csv("garbage") is None
    assert parse_geiger_csv("") is None
    assert parse_geiger_csv("CPS,1") is None


def test_valid_modes():
    for mode in ["SLOW", "FAST", "INST"]:
        line = f"CPS, 1, CPM, 2, uSv/hr, 0.01, {mode}"
        result = parse_geiger_csv(line)
        assert result["mode"] == mode


def test_invalid_mode():
    line = "CPS, 1, CPM, 2, uSv/hr, 0.01, UNKNOWN"
    assert parse_geiger_csv(line) is None


def test_malformed_line_missing_fields():
    line = "CPS, 14, CPM, 120"
    assert parse_geiger_csv(line) is None


def test_non_numeric_values():
    line = "CPS, X, CPM, Y, uSv/hr, Z, SLOW"
    assert parse_geiger_csv(line) is None


def test_extra_whitespace():
    line = "  CPS ,   14 , CPM , 120 , uSv/hr , 0.12 , SLOW   "
    result = parse_geiger_csv(line)
    assert result["cps"] == 14
    assert result["cpm"] == 120
    assert result["usv"] == 0.12
    assert result["mode"] == "SLOW"


def test_non_string_input():
    assert parse_geiger_csv(None) is None
    assert parse_geiger_csv(123) is None


def test_lowercase_mode_rejected():
    line = "CPS, 1, CPM, 2, uSv/hr, 0.01, slow"
    assert parse_geiger_csv(line) is None
