from unittest import TestCase
from alpine_formatter.formatter import RE_PATTERN


class TestPattern(TestCase):
    def test_num_of_matches(self):
        content = """
        <div x-data='{"key": "value"}'>
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_matches_multiline(self):
        content = """
        <div x-data='
        {"key": "value"}
        '>
        <div x-data="
        {'key': 'value'}
        ">
        <div x-data=
        "
            {'key': 'value'}
        "
        >
        <div x-data=
        "
            {'key': 'value'}">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 4)

    def test_matches_ignoring_case(self):
        content = """
        <div X-dAtA='{"key": "value"}'>
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_matches_escaped_double_quotes(self):
        content = """
        <div x-data="{\"key\": \"value\"}">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].group("quote"), '"')

    def test_matches_escaped_single_quotes(self):
        content = """
        <div x-data='{\'key\': \'value\'}'>
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].group("quote"), "'")

    def test_matches_directives_without_spaces(self):
        content = """
        <div x-data="{"key": "value"}"x-data="">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 2)

    def test_matches_directives_on_first_line(self):
        content = """<div x-data="{"key": "value"}">"""
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)

    def test_do_not_match_different_quotes(self):
        content = """
        <div x-data='">
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 0)

    def test_groups_have_expected_content(self):
        content = """
        <div x-data='{"key": "value"}'>
        """
        matches = list(RE_PATTERN.finditer(content))
        self.assertEqual(len(matches), 1)
        match = matches[0]
        self.assertEqual(match.group("directive"), "x-data")
        self.assertEqual(match.group("quote"), "'")
        self.assertEqual(match.group("code"), '{"key": "value"}')
