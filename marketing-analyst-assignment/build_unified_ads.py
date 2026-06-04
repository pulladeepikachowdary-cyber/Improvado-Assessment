import argparse
from pathlib import Path

import pandas as pd


def _safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    denominator = denominator.replace({0: pd.NA})
    return numerator / denominator


def load_facebook(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    df["platform"] = "facebook"
    df = df.rename(
        columns={
            "ad_set_id": "ad_group_id",
            "ad_set_name": "ad_group_name",
            "spend": "spend",
        }
    )

    df["conversion_value"] = pd.NA
    df["cost"] = pd.NA
    df["ctr"] = _safe_divide(df["clicks"], df["impressions"])
    df["avg_cpc"] = _safe_divide(df["spend"], df["clicks"])
    df["quality_score"] = pd.NA
    df["search_impression_share"] = pd.NA

    df["likes"] = pd.NA
    df["shares"] = pd.NA
    df["comments"] = pd.NA
    df["video_watch_25"] = pd.NA
    df["video_watch_50"] = pd.NA
    df["video_watch_75"] = pd.NA
    df["video_watch_100"] = pd.NA

    return df


def load_google(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    df["platform"] = "google"
    df = df.rename(
        columns={
            "cost": "spend",
        }
    )

    df["video_views"] = pd.NA
    df["engagement_rate"] = pd.NA
    df["reach"] = pd.NA
    df["frequency"] = pd.NA

    df["likes"] = pd.NA
    df["shares"] = pd.NA
    df["comments"] = pd.NA
    df["video_watch_25"] = pd.NA
    df["video_watch_50"] = pd.NA
    df["video_watch_75"] = pd.NA
    df["video_watch_100"] = pd.NA

    return df


def load_tiktok(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    df["platform"] = "tiktok"
    df = df.rename(
        columns={
            "adgroup_id": "ad_group_id",
            "adgroup_name": "ad_group_name",
            "cost": "spend",
        }
    )

    df["conversion_value"] = pd.NA
    df["ctr"] = _safe_divide(df["clicks"], df["impressions"])
    df["avg_cpc"] = _safe_divide(df["spend"], df["clicks"])
    df["quality_score"] = pd.NA
    df["search_impression_share"] = pd.NA

    df["engagement_rate"] = pd.NA
    df["reach"] = pd.NA
    df["frequency"] = pd.NA

    return df


UNIFIED_COLUMNS = [
    "date",
    "platform",
    "campaign_id",
    "campaign_name",
    "ad_group_id",
    "ad_group_name",
    "impressions",
    "clicks",
    "spend",
    "conversions",
    "conversion_value",
    "video_views",
    "reach",
    "frequency",
    "engagement_rate",
    "likes",
    "shares",
    "comments",
    "video_watch_25",
    "video_watch_50",
    "video_watch_75",
    "video_watch_100",
    "ctr",
    "avg_cpc",
    "quality_score",
    "search_impression_share",
]


def build_unified(base_dir: Path) -> pd.DataFrame:
    fb = load_facebook(base_dir / "01_facebook_ads.csv")
    g = load_google(base_dir / "02_google_ads.csv")
    tt = load_tiktok(base_dir / "03_tiktok_ads.csv")

    unified = pd.concat([fb, g, tt], ignore_index=True, sort=False)
    unified = unified.reindex(columns=UNIFIED_COLUMNS)

    numeric_cols = [
        "impressions",
        "clicks",
        "spend",
        "conversions",
        "conversion_value",
        "video_views",
        "reach",
        "frequency",
        "engagement_rate",
        "likes",
        "shares",
        "comments",
        "video_watch_25",
        "video_watch_50",
        "video_watch_75",
        "video_watch_100",
        "ctr",
        "avg_cpc",
        "quality_score",
        "search_impression_share",
    ]
    for col in numeric_cols:
        if col in unified.columns:
            unified[col] = pd.to_numeric(unified[col], errors="coerce")

    unified = unified.sort_values(["date", "platform", "campaign_id"]).reset_index(drop=True)
    return unified


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-dir", type=str, default=".")
    parser.add_argument("--out", type=str, default="unified_ads.csv")
    args = parser.parse_args()

    base_dir = Path(args.base_dir).resolve()
    out_path = Path(args.out).resolve()

    unified = build_unified(base_dir)
    unified.to_csv(out_path, index=False)
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

