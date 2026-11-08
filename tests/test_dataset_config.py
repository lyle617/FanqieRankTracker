import pytest

from fanqie_datasets import get_dataset_config


def test_male_dataset_uses_existing_rank_paths():
    config = get_dataset_config("male")

    assert config["label"] == "男频"
    assert config["rank_url"] == "https://fanqienovel.com/rank/1_1_1141"
    assert config["category_prefix"] == "/rank/1_1_"
    assert config["snapshot_prefix"] == "fanqie_male_new_ranks_"
    assert config["data_dir"] == "data"


def test_female_dataset_uses_independent_rank_paths():
    config = get_dataset_config("female")

    assert config["label"] == "女频"
    assert config["rank_url"] == "https://fanqienovel.com/rank/0_1_1139"
    assert config["category_prefix"] == "/rank/0_1_"
    assert config["snapshot_prefix"] == "fanqie_female_new_ranks_"
    assert config["data_dir"] == "data/female"


def test_unknown_dataset_has_a_clear_error():
    with pytest.raises(ValueError, match="Unknown dataset"):
        get_dataset_config("children")
