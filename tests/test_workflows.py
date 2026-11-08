from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_workflow(name):
    return (ROOT / ".github/workflows" / name).read_text()


def test_daily_workflow_builds_both_datasets_and_keeps_chapter_fetch():
    workflow = read_workflow("scrape.yml")

    assert "--dataset male" in workflow
    assert "--dataset female" in workflow
    assert "fetch_category_chapters.py" in workflow
    assert "cancel-in-progress: false" in workflow
    assert "actions/checkout@v5" in workflow
    assert "actions/setup-python@v6" in workflow
    assert "stefanzweifel/git-auto-commit-action@v7" in workflow


def test_force_update_rebuilds_both_datasets():
    workflow = read_workflow("force_update.yml")

    assert workflow.count("--dataset male") >= 1
    assert workflow.count("--dataset female") >= 1
    assert "fetch_category_chapters.py" in workflow


def test_pages_workflow_uses_current_action_versions():
    workflow = read_workflow("pages.yml")

    assert "actions/checkout@v5" in workflow
    assert "actions/configure-pages@v6" in workflow
    assert "actions/upload-pages-artifact@v5" in workflow
    assert "actions/deploy-pages@v5" in workflow
