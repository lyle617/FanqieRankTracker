import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_frontend_manifest_has_isolated_male_and_female_urls():
    manifest = json.loads((ROOT / "data/datasets.json").read_text())
    assert manifest["default"] == "male"
    assert set(manifest["datasets"]) == {"male", "female"}

    male = manifest["datasets"]["male"]
    female = manifest["datasets"]["female"]
    assert male["label"] == "男频"
    assert female["label"] == "女频"
    assert male["latest"] != female["latest"]
    assert male["dates"] != female["dates"]
    assert male["api_all"] != female["api_all"]
    assert male["snapshot_prefix"] != female["snapshot_prefix"]


def test_pages_load_shared_dataset_helper_before_page_scripts():
    for page, script in [("index.html", "js/app.js"), ("trend.html", "js/trend.js"), ("book.html", "js/book.js")]:
        html = (ROOT / page).read_text()
        assert "js/datasets.js" in html
        assert html.index("js/datasets.js") < html.index(script)
