import pytest
from deuxpots.pdf_tax_parser import _parse_line, _read_pdf_lines, parse_tax_pdf


@pytest.mark.parametrize("box", ["1BJ", "8UY"])
def test__parse_tax_pdf(box):
    assert list(_parse_line(f"{box} xxxx : 7348")) == [(box, 7348)]


@pytest.mark.parametrize("box", ["911", "PAM"])
def test__parse_tax_pdf_false_positive(box):
    assert not list(_parse_line(f"{box} xxxx : 7348"))


def test__read_pdf_lines():
    clean_lines = []
    with open("test/dummy.pdf", "rb") as f:
        pdf_content = f.read()
    for line in _read_pdf_lines(pdf_content):
        line = line.strip()
        if line:
            clean_lines.append(line)
    assert clean_lines == ["Lorem ipsum", "dolor sit amet,", "consectetur adipiscing", "élit."]


def test_parse_tax_pdf():
    # TODO: test with some real family_box_coords
    with open("test/dummy.pdf", "rb") as f:
        pdf_content = f.read()
    parse_tax_pdf(pdf_content, family_box_coords={})
