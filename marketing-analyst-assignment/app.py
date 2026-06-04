from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


def _safe_divide(numerator: float, denominator: float) -> float | None:
    if denominator in (0, 0.0) or pd.isna(denominator):
        return None
    if pd.isna(numerator):
        return None
    return float(numerator) / float(denominator)


def _load_csv(base_dir: Path, name: str) -> pd.DataFrame:
    df = pd.read_csv(base_dir / name)
    df["date"] = pd.to_datetime(df["date"])
    return df


@st.cache_data
def load_unified(base_dir_str: str) -> pd.DataFrame:
    base_dir = Path(base_dir_str)

    fb = _load_csv(base_dir, "01_facebook_ads.csv")
    fb["platform"] = "facebook"
    fb = fb.rename(columns={"ad_set_id": "ad_group_id", "ad_set_name": "ad_group_name"})
    fb["conversion_value"] = pd.NA
    fb["ctr"] = fb["clicks"] / fb["impressions"].replace({0: pd.NA})
    fb["avg_cpc"] = fb["spend"] / fb["clicks"].replace({0: pd.NA})
    fb["quality_score"] = pd.NA
    fb["search_impression_share"] = pd.NA
    fb["likes"] = pd.NA
    fb["shares"] = pd.NA
    fb["comments"] = pd.NA
    fb["video_watch_25"] = pd.NA
    fb["video_watch_50"] = pd.NA
    fb["video_watch_75"] = pd.NA
    fb["video_watch_100"] = pd.NA

    g = _load_csv(base_dir, "02_google_ads.csv")
    g["platform"] = "google"
    g = g.rename(columns={"cost": "spend"})
    g["video_views"] = pd.NA
    g["engagement_rate"] = pd.NA
    g["reach"] = pd.NA
    g["frequency"] = pd.NA
    g["likes"] = pd.NA
    g["shares"] = pd.NA
    g["comments"] = pd.NA
    g["video_watch_25"] = pd.NA
    g["video_watch_50"] = pd.NA
    g["video_watch_75"] = pd.NA
    g["video_watch_100"] = pd.NA

    tt = _load_csv(base_dir, "03_tiktok_ads.csv")
    tt["platform"] = "tiktok"
    tt = tt.rename(
        columns={"adgroup_id": "ad_group_id", "adgroup_name": "ad_group_name", "cost": "spend"}
    )
    tt["conversion_value"] = pd.NA
    tt["ctr"] = tt["clicks"] / tt["impressions"].replace({0: pd.NA})
    tt["avg_cpc"] = tt["spend"] / tt["clicks"].replace({0: pd.NA})
    tt["quality_score"] = pd.NA
    tt["search_impression_share"] = pd.NA
    tt["engagement_rate"] = pd.NA
    tt["reach"] = pd.NA
    tt["frequency"] = pd.NA

    unified = pd.concat([fb, g, tt], ignore_index=True, sort=False)

    columns = [
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
    unified = unified.reindex(columns=columns)

    for col in columns:
        if col == "date":
            continue
        if col in ("platform", "campaign_id", "campaign_name", "ad_group_id", "ad_group_name"):
            continue
        unified[col] = pd.to_numeric(unified[col], errors="coerce")

    unified = unified.sort_values(["date", "platform", "campaign_id"]).reset_index(drop=True)
    return unified


def main() -> None:
    st.set_page_config(page_title="Cross-Channel Ads Dashboard", layout="wide")
    base_dir = Path(__file__).resolve().parent
    df = load_unified(str(base_dir))

    st.title("Cross-Channel Ads Performance")

    min_date = df["date"].min()
    max_date = df["date"].max()

    platforms = sorted(df["platform"].dropna().unique().tolist())
    campaigns = sorted(df["campaign_name"].dropna().unique().tolist())

    with st.sidebar:
        st.header("Filters")
        date_range = st.date_input(
            "Date range",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date(),
        )
        selected_platforms = st.multiselect("Platform", platforms, default=platforms)
        selected_campaigns = st.multiselect("Campaign", campaigns, default=campaigns)

    start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered = df[
        (df["date"] >= start_date)
        & (df["date"] <= end_date)
        & (df["platform"].isin(selected_platforms))
        & (df["campaign_name"].isin(selected_campaigns))
    ].copy()

    total_spend = float(filtered["spend"].sum(skipna=True))
    total_impressions = float(filtered["impressions"].sum(skipna=True))
    total_clicks = float(filtered["clicks"].sum(skipna=True))
    total_conversions = float(filtered["conversions"].sum(skipna=True))
    total_value = float(filtered["conversion_value"].sum(skipna=True))

    ctr = _safe_divide(total_clicks, total_impressions)
    cpc = _safe_divide(total_spend, total_clicks)
    cpa = _safe_divide(total_spend, total_conversions)
    roas = _safe_divide(total_value, total_spend) if total_value else None

    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    kpi1.metric("Spend", f"${total_spend:,.2f}")
    kpi2.metric("Impressions", f"{total_impressions:,.0f}")
    kpi3.metric("Clicks", f"{total_clicks:,.0f}")
    kpi4.metric("CTR", f"{ctr:.2%}" if ctr is not None else "—")
    kpi5.metric("Conversions", f"{total_conversions:,.0f}")
    kpi6.metric("CPA", f"${cpa:,.2f}" if cpa is not None else "—")

    left, right = st.columns([2, 1])

    with left:
        st.subheader("Trends")
        by_day = (
            filtered.groupby(["date", "platform"], as_index=False)[
                ["spend", "conversions", "clicks", "impressions"]
            ]
            .sum()
            .sort_values("date")
        )

        spend_pivot = by_day.pivot(index="date", columns="platform", values="spend").fillna(0)
        st.caption("Daily spend by platform")
        st.line_chart(spend_pivot)

        conv_pivot = by_day.pivot(index="date", columns="platform", values="conversions").fillna(0)
        st.caption("Daily conversions by platform")
        st.line_chart(conv_pivot)

    with right:
        st.subheader("Platform Mix")
        by_platform = (
            filtered.groupby("platform", as_index=False)[["spend", "conversions", "clicks", "impressions"]]
            .sum()
            .sort_values("spend", ascending=False)
        )
        by_platform["ctr"] = by_platform["clicks"] / by_platform["impressions"].replace({0: pd.NA})
        by_platform["cpc"] = by_platform["spend"] / by_platform["clicks"].replace({0: pd.NA})
        by_platform["cpa"] = by_platform["spend"] / by_platform["conversions"].replace({0: pd.NA})

        st.caption("Spend by platform")
        st.bar_chart(by_platform.set_index("platform")["spend"])

        st.caption("Efficiency (CPC / CPA)")
        st.dataframe(
            by_platform[["platform", "ctr", "cpc", "cpa"]].style.format(
                {"ctr": "{:.2%}", "cpc": "${:,.2f}", "cpa": "${:,.2f}"}
            ),
            use_container_width=True,
            hide_index=True,
        )

        if total_value > 0:
            st.metric("Conversion Value", f"${total_value:,.2f}")
            st.metric("ROAS", f"{roas:,.2f}x" if roas is not None else "—")

    st.subheader("Top Campaigns")
    by_campaign = (
        filtered.groupby(["platform", "campaign_name"], as_index=False)[
            ["spend", "conversions", "clicks", "impressions", "conversion_value"]
        ]
        .sum()
        .sort_values("spend", ascending=False)
    )
    by_campaign["ctr"] = by_campaign["clicks"] / by_campaign["impressions"].replace({0: pd.NA})
    by_campaign["cpc"] = by_campaign["spend"] / by_campaign["clicks"].replace({0: pd.NA})
    by_campaign["cpa"] = by_campaign["spend"] / by_campaign["conversions"].replace({0: pd.NA})
    by_campaign["roas"] = by_campaign["conversion_value"] / by_campaign["spend"].replace({0: pd.NA})

    st.dataframe(
        by_campaign.head(20).style.format(
            {
                "spend": "${:,.2f}",
                "conversion_value": "${:,.2f}",
                "ctr": "{:.2%}",
                "cpc": "${:,.2f}",
                "cpa": "${:,.2f}",
                "roas": "{:.2f}x",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("Unified data preview"):
        st.dataframe(filtered.head(200), use_container_width=True, hide_index=True)


main()

