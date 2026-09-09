import pytest
from pathlib import Path
from engine_a11y.immutability import (
    assert_not_same_path,
    assert_source_unchanged,
    get_remediated_path,
    sha256_file,
    verify_immutability,
    verify_remediation_output,
)

def test_sha256_file(tmp_path):
    f = tmp_path / "sample.txt"
    f.write_text("hello accessibility")
    h = sha256_file(f)
    assert len(h) == 64
    assert isinstance(h, str)

def test_assert_source_unchanged(tmp_path):
    f = tmp_path / "sample.txt"
    f.write_text("hello")
    expected = sha256_file(f)
    assert verify_immutability(f, expected) is True

    f.write_text("mutated")
    with pytest.raises(RuntimeError, match="immutability violation"):
        assert_source_unchanged(f, expected)

def test_assert_not_same_path(tmp_path):
    f1 = tmp_path / "source.docx"
    f1.touch()
    f2 = tmp_path / "out.docx"
    assert_not_same_path(f1, f2)

    with pytest.raises(ValueError, match="Destination path cannot equal source path"):
        assert_not_same_path(f1, f1)

def test_get_remediated_path():
    in_p = Path("/tmp/report.pdf")
    out_p = get_remediated_path(in_p)
    assert out_p == Path("/tmp/report-remediated.pdf")

    custom = get_remediated_path(in_p, out_path="/tmp/custom.pdf")
    assert custom == Path("/tmp/custom.pdf")

def test_verify_remediation_output(tmp_path):
    f1 = tmp_path / "source.docx"
    f1.write_text("source content")
    f2 = tmp_path / "out.docx"
    f2.write_text("remediated content")

    h1, h2 = verify_remediation_output(f1, f2)
    assert len(h1) == 64
    assert len(h2) == 64
    assert h1 != h2
