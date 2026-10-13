"""Clinical formula, validation, and file-processing regression tests."""
import csv
import json
import pytest
from til_scorer import calculate_metrics, process_batch, main


@pytest.mark.parametrize(("total", "occupied", "expected"), [
    (100, 0, 0), (100, 100, 100), (200, 55, 27.5),
    (0.5, 0.125, 25), (3, 1, 33.33),
])
def test_area_percentage(total, occupied, expected):
    assert calculate_metrics(stromal_area=total, til_area=occupied)["score"] == expected


@pytest.mark.parametrize(("total", "occupied"), [
    (0, 0), (-1, 0), (1, -0.1), (1, 1.1),
    ("garbage", 1), (100, None), (float("inf"), 1),
    (1, float("nan")),
])
def test_invalid_areas(total, occupied):
    with pytest.raises(ValueError):
        calculate_metrics(stromal_area=total, til_area=occupied)


def test_requires_explicit_parameters():
    with pytest.raises(TypeError):
        calculate_metrics(v1=10, v2=5)


def test_batch_preserves_ids(tmp_path):
    inp, out = tmp_path / "input.csv", tmp_path / "nested" / "result.csv"
    inp.write_text('sample_id,stromal_area,til_area\n"Study, case",40,10\nTwo,100,0\n')
    process_batch(inp, out)
    with out.open(newline="") as f:
        data = list(csv.DictReader(f))
    assert data[0]["sample_id"] == "Study, case"
    assert data[0]["stromal_til_percent"] == "25.0"
    assert data[1]["stromal_til_percent"] == "0.0"


def test_batch_rejects_partial_data_without_writing(tmp_path):
    inp, out = tmp_path / "input.csv", tmp_path / "result.csv"
    inp.write_text('stromal_area,til_area\n40,10\n40,99\n')
    with pytest.raises(ValueError, match="row 3"):
        process_batch(inp, out)
    assert not out.exists()


def test_batch_missing_columns(tmp_path):
    inp = tmp_path / "input.csv"
    inp.write_text('v1,v2\n10,5\n')
    with pytest.raises(ValueError, match="must contain"):
        process_batch(inp, tmp_path / "out.csv")


def test_batch_same_file_protection(tmp_path):
    inp = tmp_path / "input.csv"
    inp.write_text('stromal_area,til_area\n10,5\n')
    with pytest.raises(ValueError, match="must differ"):
        process_batch(inp, inp)


def test_cli_single(capsys):
    assert main(["single", "--stromal-area", "80", "--til-area", "20"]) == 0
    assert json.loads(capsys.readouterr().out)["stromal_til_percent"] == 25.0
