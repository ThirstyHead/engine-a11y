import pytest
from pathlib import Path
import sys
from engine_a11y.cli import main

def test_cli_init_criteria(tmp_path, monkeypatch):
    out_file = tmp_path / "my-criteria.txt"
    monkeypatch.setattr(sys, "argv", ["engine-a11y", "--init-criteria", str(out_file)])
    ret = main()
    assert ret == 0
    assert out_file.exists()
    content = out_file.read_text()
    assert "[x] 1.1.1 Non-text Content" in content
    assert "[x] 1.4.3 Contrast (Minimum)" in content

def test_cli_help(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["engine-a11y", "--help"])
    with pytest.raises(SystemExit):
        main()
    captured = capsys.readouterr()
    assert "--init-criteria" in captured.out
    assert "--criteria" in captured.out
