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
        "analysis_label": "男频",
        "genre_groups": [
            {"name": "玄幻仙侠", "categories": ["传统玄幻", "玄幻脑洞", "东方仙侠", "西方奇幻"]},
            {"name": "都市现实", "categories": ["都市日常", "都市修真", "都市高武", "都市种田", "都市脑洞"]},
            {"name": "历史军事", "categories": ["历史古代", "历史脑洞", "抗战谍战"]},
            {"name": "悬疑灵异", "categories": ["悬疑脑洞", "悬疑灵异"]},
            {"name": "科幻末世", "categories": ["科幻末世"]},
            {"name": "战神赘婿", "categories": ["战神赘婿"]},
            {"name": "游戏体育", "categories": ["游戏体育"]},
            {"name": "动漫衍生", "categories": ["动漫衍生", "男频衍生"]},
        ],
        "market_keywords": [
            "穿越", "系统", "开局", "觉醒", "重生", "天赋", "降临", "求生", "全民",
            "副本", "属性", "面板", "签到", "推演", "升级", "修炼", "修仙", "功法", "灵根",
            "无敌", "逆袭", "打脸", "爽文", "神级", "最强", "至尊", "顶级",
            "赘婿", "战神", "兵王", "神医", "总裁", "校花", "女神", "老婆", "千金",
            "玄幻", "洪荒", "都市", "历史", "三国", "大唐", "大明", "皇帝", "年代", "四合院",
            "抗战", "谍战", "军旅", "悬疑", "灵异", "盗墓", "无限流",
            "末世", "废土", "天灾", "囤货", "入侵", "怪物", "全球",
            "游戏", "直播", "曝光", "娱乐圈", "病娇", "动漫", "衍生",
        ],
    },
    "female": {
        "label": "女频",
        "rank_url": "https://fanqienovel.com/rank/0_1_1139",
        "category_prefix": "/rank/0_1_",
        "snapshot_prefix": "fanqie_female_new_ranks_",
        "data_dir": "data/female",
        "api_dir": "api/female/lastest",
        "analysis_label": "女频",
        "genre_groups": [
            {"name": "古风言情", "categories": ["古风世情", "古言脑洞", "宫斗宅斗", "种田"]},
            {"name": "现代言情", "categories": ["现言脑洞", "豪门总裁", "职场婚恋", "青春甜宠"]},
            {"name": "幻想言情", "categories": ["玄幻言情", "科幻末世", "悬疑脑洞", "女频悬疑"]},
            {"name": "快穿衍生", "categories": ["快穿", "女频衍生"]},
            {"name": "年代民国", "categories": ["年代", "民国言情"]},
            {"name": "娱乐星光", "categories": ["星光璀璨"]},
            {"name": "游戏体育", "categories": ["游戏体育"]},
        ],
        "market_keywords": [
            "重生", "穿书", "快穿", "系统", "空间", "团宠", "萌宝", "幼崽", "女配", "炮灰",
            "反派", "权臣", "宅斗", "宫斗", "和离", "替嫁", "逃荒", "种田", "美食", "经商",
            "年代", "七零", "八零", "军婚", "豪门", "总裁", "真假千金", "先婚后爱", "追妻",
            "甜宠", "双洁", "强制爱", "无CP", "末世", "废土", "天灾", "囤货", "异能",
            "国运", "星际", "修仙", "玄学", "无限流", "悬疑", "直播", "综艺", "娱乐圈",
            "校园", "暗恋", "青梅竹马", "民国", "兽世", "远古", "基建",
        ],
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
