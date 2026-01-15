import pytest

from repren.repren import (
    _split_name,
    to_lower_camel,
    to_lower_underscore,
    to_upper_camel,
    to_upper_underscore,
)


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("ÜnicodeString", ("", ["Ünicode", "String"])),
        ("sträßleTest", ("", ["sträßle", "Test"])),
        ("ГДеловойКод", ("", ["Г", "Деловой", "Код"])),
        ("ΚαλημέραWorld", ("", ["Καλημέρα", "World"])),
        ("normalTest", ("", ["normal", "Test"])),
        ("HTTPResponse", ("", ["HTTP", "Response"])),
        ("ThisIsATest", ("", ["This", "Is", "A", "Test"])),
        ("テストCase", ("", ["テスト", "Case"])),
        ("测试案例", ("", ["测试案例"])),  # Chinese characters
    ],
)
def test_split_name(input_str, expected):
    assert _split_name(input_str) == expected


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("ÜnicodeString", "ünicodeString"),
        ("HTTPResponse", "httpResponse"),
        ("ΚαλημέραWorld", "καλημέραWorld"),
        ("sträßleTest", "sträßleTest"),
        ("ThisIsATest", "thisIsATest"),
        ("テストCase", "テストCase"),
        ("测试案例", "测试案例"),
    ],
)
def test_to_lower_camel(input_str, expected):
    assert to_lower_camel(input_str) == expected


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("ünicode_string", "ÜnicodeString"),
        ("sträßle_test", "SträßleTest"),
        ("http_response", "HttpResponse"),
        ("καλημέρα_world", "ΚαλημέραWorld"),
        ("this_is_a_test", "ThisIsATest"),
        ("テスト_case", "テストCase"),
        ("测试_案例", "测试案例"),
    ],
)
def test_to_upper_camel(input_str, expected):
    assert to_upper_camel(input_str) == expected


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("ÜnicodeString", "ünicode_string"),
        ("HTTPResponse", "http_response"),
        ("ΚαλημέραWorld", "καλημέρα_world"),
        ("sträßleTest", "sträßle_test"),
        ("ThisIsATest", "this_is_a_test"),
        ("テストCase", "テスト_case"),
        ("测试案例", "测试案例"),
    ],
)
def test_to_lower_underscore(input_str, expected):
    assert to_lower_underscore(input_str) == expected


@pytest.mark.parametrize(
    "input_str, expected",
    [
        ("ünicode_string", "ÜNICODE_STRING"),
        ("http_response", "HTTP_RESPONSE"),
        ("καλημέρα_world", "ΚΑΛΗΜΈΡΑ_WORLD"),
        ("sträßle_test", "STRÄSSLE_TEST"),
        ("this_is_a_test", "THIS_IS_A_TEST"),
        ("テスト_case", "テスト_CASE"),
        ("测试_案例", "测试_案例"),
    ],
)
def test_to_upper_underscore(input_str, expected):
    assert to_upper_underscore(input_str) == expected
