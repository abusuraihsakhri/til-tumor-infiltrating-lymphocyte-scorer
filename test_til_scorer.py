import pytest
from til_scorer import calculate_metrics, process_batch, main


def test_til_scorer_single():
    res = calculate_metrics(v1=12.0, v2=4.0)
    assert "score" in res
    assert "classification" in res
    assert res["score"] > 0


def test_til_scorer_batch(tmp_path):
    csv_in = tmp_path / "in.csv"
    csv_out = tmp_path / "out.csv"
    csv_in.write_text("Patient,v1,v2\nPat_001,15.0,3.0\nPat_002,5.0,1.0\n", encoding="utf-8")

    process_batch(str(csv_in), str(csv_out))
    assert csv_out.exists()
    content = csv_out.read_text(encoding="utf-8")
    assert "Pat_001" in content
    assert "score" in content


def test_calculate_metrics_classification_low():
    res = calculate_metrics(v1=5.0)
    assert res["classification"] == "Low / Standard"
    assert res["score"] == 5.0


def test_calculate_metrics_classification_moderate():
    res = calculate_metrics(v1=15.0)
    assert res["classification"] == "Moderate / Intermediate"


def test_calculate_metrics_classification_high():
    res = calculate_metrics(v1=30.0)
    assert res["classification"] == "High / Severe"


def test_calculate_metrics_empty():
    res = calculate_metrics()
    assert res["score"] == 1.0
    assert res["inputs_evaluated"] == 0


def test_calculate_metrics_string_input():
    res = calculate_metrics(v1="test", v2=5.0)
    assert res["score"] == 5.0
    # String "test" is kept as-is (not converted to float), so both params are counted
    assert res["inputs_evaluated"] == 2


def test_process_batch_file_not_found():
    with pytest.raises(FileNotFoundError):
        process_batch("/nonexistent/path.csv", "/tmp/out.csv")


def test_process_batch_empty_csv(tmp_path):
    csv_in = tmp_path / "empty.csv"
    csv_out = tmp_path / "out.csv"
    csv_in.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="empty or has no headers"):
        process_batch(str(csv_in), str(csv_out))


def test_process_batch_creates_output_dir(tmp_path):
    csv_in = tmp_path / "in.csv"
    csv_out = tmp_path / "subdir" / "nested" / "out.csv"
    csv_in.write_text("v1,v2\n10.0,5.0\n", encoding="utf-8")
    process_batch(str(csv_in), str(csv_out))
    assert csv_out.exists()


def test_main_single_command(capsys):
    main(["single", "--v1", "10.0", "--v2", "5.0"])
    captured = capsys.readouterr()
    assert "score" in captured.out
    assert "classification" in captured.out


def test_main_batch_command(tmp_path):
    csv_in = tmp_path / "in.csv"
    csv_out = tmp_path / "out.csv"
    csv_in.write_text("v1,v2\n10.0,5.0\n", encoding="utf-8")
    main(["batch", "-i", str(csv_in), "-o", str(csv_out)])
    assert csv_out.exists()
