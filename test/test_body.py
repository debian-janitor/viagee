# -*- coding: utf-8 -*-

import pytest
import re
from six.moves import urllib

import viagee


baseMailtoURL = "mailto:joe?body="
BASEMailtoURL = "mailto:joe?BODY="

testCaseStrings = [
    ("x", "x"),
    ("x", "<html>"),
    ("x", "</html>"),
    ("x", "<head>"),
    ("x", "</head>"),
    ("x", "<body>"),
    ("x", "</body>"),

    ("http://example.com",
        "<a href=\"http://example.com\">http://example.com</a>"),
    ("http://example.com#1",
        "<a href=\"http://example.com#1\">http://example.com#1</a>"),
    # flake8: noqa
    ("http://example.com?a=b&c=d",
        "<a href=\"http://example.com?a=b&c=d\">http://example.com?a=b&c=d</a>"),
    ("(http://example.com/)",
        "<a href=\"http://example.com/\">http://example.com/</a>)"),
    ("(http://example.com/a)",
        "<a href=\"http://example.com/a\">http://example.com/a</a>)"),

    ("a http://example.com b",
        "<a href=\"http://example.com\">http://example.com</a>"),
    ("\"http://example.com\"",
        "<a href=\"http://example.com\">http://example.com</a>"),
    ("\'http://example.com\'",
        "<a href=\"http://example.com\">http://example.com</a>"),
    ("http://example.com.",
        "<a href=\"http://example.com\">http://example.com</a>."),
    ("http://example.com,",
        "<a href=\"http://example.com\">http://example.com</a>,"),
    ("(http://example.com)",
        "<a href=\"http://example.com\">http://example.com</a>)"),

    ("http://aa.com http://example.com",
        "<a href=\"http://example.com\">http://example.com</a>"),
    ("http://aa.com http://example.com",
        "<a href=\"http://aa.com\">http://aa.com</a>"),

    ("https://example.com",
        "<a href=\"https://example.com\">https://example.com</a>"),
    ("ftp://example.com",
        "<a href=\"ftp://example.com\">ftp://example.com</a>"),

    ("mailto:joe@example.com",
        "<a href=\"mailto:joe@example.com\">mailto:joe@example.com</a>"),

    ("a b", "a b"),
    ("a  b", "a&nbsp; b"),
    ("a   b", "a&nbsp;&nbsp; b"),
    ("a    b", "a&nbsp;&nbsp;&nbsp; b"),
    ("a\tb", "a&emsp;b"),

    ("a>b", "a&gt;b"),
    ("a<b", "a&lt;b"),

    ("a\nb", "a<br>\nb"),
    ("a\nb\nc", "a<br>\nb<br>\nc"),

    # Unicode
    ("ä", "ä"),
    ("mailto:joe@exämple.com",
        "<a href=\"mailto:joe@exämple.com\">mailto:joe@exämple.com</a>"),
 ]


def get_gmapi(input):
        gm = viagee.GMailURL(input, "me")
        mail_dict = gm.mail_dict

        gmapi = viagee.GMailAPI(mail_dict)

        return gmapi


@pytest.mark.parametrize("bodycaps", [False, True])
@pytest.mark.parametrize("body, result", testCaseStrings)
def test_needs_api_yes(bodycaps, body, result):
    if bodycaps:
        gmapi = get_gmapi(BASEMailtoURL + body)
    else:
        gmapi = get_gmapi(baseMailtoURL + body)

    assert gmapi.needs_api() is True


@pytest.mark.parametrize("body, result", testCaseStrings)
@pytest.mark.parametrize("encbody", (False, True))
def test_body2html(encbody, body, result):

    if encbody:
        body = urllib.parse.quote(body)
    elif '&' in body or '#' in body:
        pytest.skip("Don't test unencoded bodies with URL special chars")

    gmapi = get_gmapi(baseMailtoURL + body)

    html_body = gmapi.body2html()

    assert result in html_body


@pytest.mark.parametrize("mailto, needs_api", (
    ("mailto:joe", True),
    ("mailto:joe?subject=hi", True),
    ("mailto:joe?body=%20", True),
    ("mailto:joe?attach=file", True),
    ("mailto:joe?attachment=file", True),
))
def test_needs_api(mailto, needs_api):
    gmapi = get_gmapi(mailto)

    assert gmapi.needs_api() == needs_api
