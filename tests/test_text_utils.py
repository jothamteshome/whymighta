from utils.text_utils import convert_binary, spongebob_case


# ---------------------------------------------------------------------------
# spongebob_case
# ---------------------------------------------------------------------------

def test_spongebob_case_alternates():
    result = spongebob_case("hello")
    assert result == "hElLo"


def test_spongebob_case_empty():
    assert spongebob_case("") == ""


def test_spongebob_case_single_char():
    assert spongebob_case("a") == "a"
    assert spongebob_case("A") == "a"


def test_spongebob_case_preserves_length():
    text = "Hello, World!"
    assert len(spongebob_case(text)) == len(text)


def test_spongebob_case_non_alpha_unchanged():
    # Non-alpha chars have no case so upper/lower doesn't change them,
    # but the toggle still advances: a(lower) 1(upper-but-unchanged) b(lower) -> "a1b"
    result = spongebob_case("a1b")
    assert result == "a1b"


# ---------------------------------------------------------------------------
# convert_binary
# ---------------------------------------------------------------------------

def test_convert_binary_single_char():
    # 'A' == 65 == 0b01000001
    assert convert_binary("A") == "01000001"


def test_convert_binary_space_separated():
    result = convert_binary("hi")
    parts = result.split(" ")
    assert len(parts) == 2
    assert all(len(p) == 8 for p in parts)


def test_convert_binary_empty():
    assert convert_binary("") == ""


def test_convert_binary_known_values():
    # 'a' == 97 == 01100001, 'b' == 98 == 01100010
    assert convert_binary("ab") == "01100001 01100010"
