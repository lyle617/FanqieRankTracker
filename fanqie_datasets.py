"""Shared configuration for the male and female Fanqie datasets."""

from copy import deepcopy


_DATASETS = {
    "male": {
        "label": "男频",
        "rank_url": "https://fanqienovel.com/rank/1_1_1141",
        "category_prefix": "/rank/1_1_",
        "snapshot_prefix": "fanqie_male_new_ranks_",
        "data_dir": "data",
        "api_dir": "api/lastest",
    },
    "female": {
        "label": "女频",
        "rank_url": "https://fanqienovel.com/rank/0_1_1139",
        "category_prefix": "/rank/0_1_",
        "snapshot_prefix": "fanqie_female_new_ranks_",
        "data_dir": "data/female",
        "api_dir": "api/female/lastest",
    },
}


def get_dataset_config(name: str) -> dict:
    """Return a copy of the named dataset configuration.

    A copy prevents a caller that adds derived paths or runtime state from
    mutating the process-wide defaults used by another dataset.
    """
    try:
        return deepcopy(_DATASETS[name])
    except KeyError as exc:
        available = ", ".join(sorted(_DATASETS))
        raise ValueError(f"Unknown dataset {name!r}; choose one of: {available}") from exc


def dataset_names() -> tuple[str, ...]:
    """Return the stable dataset names exposed to scripts and the UI."""
    return tuple(_DATASETS)
