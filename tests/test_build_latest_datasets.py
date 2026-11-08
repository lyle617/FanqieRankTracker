import json

from scripts.build_latest import find_snapshots, resolve_dataset_paths


def test_find_snapshots_filters_each_dataset_prefix(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "fanqie_male_new_ranks_20261108.json").write_text("{}")
    (data_dir / "fanqie_female_new_ranks_20261108.json").write_text("{}")

    male = find_snapshots(data_dir, "fanqie_male_new_ranks_")
    female = find_snapshots(data_dir, "fanqie_female_new_ranks_")

    assert [path.name for path in male] == ["fanqie_male_new_ranks_20261108.json"]
    assert [path.name for path in female] == ["fanqie_female_new_ranks_20261108.json"]


def test_resolve_dataset_paths_keeps_female_outputs_separate(tmp_path):
    paths = resolve_dataset_paths(tmp_path, "female")

    assert paths["data_dir"] == tmp_path / "data/female"
    assert paths["latest_path"] == tmp_path / "data/female/latest_ranks.json"
    assert paths["dates_path"] == tmp_path / "data/female/dates.json"
    assert paths["trends_dir"] == tmp_path / "data/female/trends"
    assert paths["api_dir"] == tmp_path / "api/female/lastest"


def test_dataset_outputs_are_json_addressable(tmp_path):
    paths = resolve_dataset_paths(tmp_path, "female")
    paths["latest_path"].parent.mkdir(parents=True)
    paths["latest_path"].write_text(json.dumps({"date": "2026-11-08"}))

    assert json.loads(paths["latest_path"].read_text())["date"] == "2026-11-08"
