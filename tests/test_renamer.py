"""Tests for placeholder matching in get_comic_name (slot 814)."""

from unittest import mock

import renamer


def _comic_info():
    return {
        "id": 123,
        "name": None,
        "name_cn": "Berserk",
    }


def _persons():
    return [{"relation": "作者", "name": "Kentaro Miura"}]


def test_format_with_namecn_does_not_require_name():
    # Only {namecn} and {author} are used, and both are available, so the
    # "name" key (a substring of the "{namecn}" placeholder) must not
    # force a None result.
    with (
        mock.patch.object(renamer, "get_comic_info", return_value=_comic_info()),
        mock.patch.object(renamer, "get_comic_person_info", return_value=_persons()),
    ):
        assert (
            renamer.get_comic_name("berserk", "{namecn} - {author}", False)
            == "Berserk - Kentaro Miura"
        )


def test_missing_placeholder_value_still_returns_none():
    info = _comic_info()
    info["name_cn"] = None
    with (
        mock.patch.object(renamer, "get_comic_info", return_value=info),
        mock.patch.object(renamer, "get_comic_person_info", return_value=_persons()),
    ):
        assert renamer.get_comic_name("berserk", "{namecn} - {author}", False) is None


def test_unknown_comic_returns_none():
    with mock.patch.object(renamer, "get_comic_info", return_value=None):
        assert renamer.get_comic_name("no-such-comic", "{name}", False) is None
