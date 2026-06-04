# Video Walkthrough Script — Senior Marketing Analyst Assignment

## 0) Opening (0:00–0:20)

Hi everyone, my name is ____. In this video I’ll walk through my solution for the Senior Marketing Analyst technical assignment.

The goal of the project is to unify raw advertising data from Facebook, Google Ads, and TikTok into a single cross-channel data model, and then use that unified model to build a one-page dashboard that highlights performance, trends, and efficiency across channels.


## 1) What data we received (0:20–0:55)

We start with three CSV files:

- `01_facebook_ads.csv` with Facebook campaign and ad set performance metrics
- `02_google_ads.csv` with Google Ads campaign and ad group performance plus search-specific fields like quality score and impression share
- `03_tiktok_ads.csv` with TikTok campaign and ad group performance plus video engagement depth metrics like watch quartiles, likes, shares, and comments

All three datasets are daily-grain, and each has its own naming conventions and platform-specific metrics, which is exactly why we need a unified table for cross-channel analysis.


## 2) Approach overview (0:55–1:25)

I split the work into two deliverables:

1. A unified data model that can be created in a cloud database, using a SQL script that defines raw tables and then inserts into a standardized `unified_ads` table.
2. A one-page dashboard built on top of the unified model to compare performance by day, by platform, and by campaign.

Even though the assignment suggests uploading to a cloud database, I also included a reproducible local workflow: a Python script that reads the three CSVs, standardizes the schema, and exports a single `unified_ads.csv` you can upload as the unified table.


## 3) Unified data model (1:25–2:40)

The central idea is to create a table called `unified_ads` with a consistent set of columns that work across all platforms:

- Dimensions: `date`, `platform`, `campaign_id`, `campaign_name`, `ad_group_id`, `ad_group_name`
- Core paid media metrics: `impressions`, `clicks`, `spend`, `conversions`
- Value metrics when available: `conversion_value`
- Video engagement when available: `video_views` and TikTok watch quartiles
- Social engagement when available: `likes`, `shares`, `comments`
- Platform-specific fields when available: `quality_score`, `search_impression_share`

The important detail is that not every platform provides every metric. In the unified table, platform-specific metrics are stored as NULL for platforms that don’t have them. This keeps the schema stable and makes it easy to write one set of queries that works across the entire dataset.

I also compute consistent derived metrics where possible, like:

- CTR = clicks divided by impressions
- Avg CPC = spend divided by clicks

For platforms that already provide CTR and Avg CPC, we keep the provided values; for others, we compute them from raw fields.


## 4) How the unified table is built (2:40–3:35)

There are two equivalent ways to build the unified table:

First option is SQL-first in Postgres:

- Create three raw tables: `facebook_ads_raw`, `google_ads_raw`, and `tiktok_ads_raw`
- Load each CSV into its matching raw table
- Run an `INSERT INTO unified_ads` that UNION ALLs the three sources and maps their columns into the standardized schema

Second option is local Python-to-CSV:

- Run the script `build_unified_ads.py`
- It reads all three CSVs, standardizes naming like ad set vs ad group, and outputs `unified_ads.csv`

This makes the solution portable: you can either do everything in a database, or create the unified table file first and then upload just one dataset to your BI tool.


## 5) Dashboard walkthrough (3:35–6:10)

Now I’ll walk through the dashboard.

At the top, I have global KPIs based on the selected filters:

- Spend
- Impressions
- Clicks
- CTR
- Conversions
- CPA

The key point is that these KPIs are aggregated across platforms, so we can quickly answer: how much did we spend, what volume did we drive, and what efficiency did we achieve across the full channel mix.

On the left side, the dashboard focuses on trends:

- Daily spend by platform, so we can see budget allocation over time
- Daily conversions by platform, so we can see where results are coming from and whether there are spikes or consistency issues

On the right side, I show the platform mix and efficiency:

- Spend by platform as a bar chart
- A small efficiency table with CTR, CPC, and CPA by platform

This answers the typical cross-channel questions:

- Which platform is taking most of the budget?
- Which platform is most efficient at driving clicks and conversions?
- Do we see a trade-off where one platform is high volume but worse CPA?

Finally, at the bottom I include a “Top Campaigns” table:

- Grouped by platform and campaign
- Includes spend, conversions, clicks, impressions, plus derived CTR, CPC, and CPA
- If conversion value exists, we also show ROAS

This is useful for quickly identifying which campaigns are driving results and which ones are costly relative to the outcomes.


## 6) Key insights to call out (6:10–7:10)

When you present insights, keep them consistent with what the dashboard shows. Here’s a clean structure to speak through:

1) Budget mix
“The budget is concentrated in ____ platform(s). This is visible in the platform spend chart and the daily spend trend.”

2) Efficiency
“In terms of CTR and CPC, ____ performs best, while in terms of CPA, ____ is more efficient. This suggests ____ platform is better for awareness/traffic, while ____ is stronger for conversion efficiency.”

3) Campaign drivers
“The Top Campaigns table highlights that ____ campaign(s) are responsible for a large portion of spend and/or conversions. These are candidates for scaling, while the bottom performers are candidates for optimization or budget reallocation.”

If you want to be more specific, you can also call out:

- TikTok’s richer video engagement metrics (views, watch depth, likes/shares/comments) and how those are useful for creative performance
- Google’s search quality score and impression share, which are diagnostic metrics for auction competitiveness


## 7) Assumptions and data considerations (7:10–7:50)

I made a few practical assumptions:

- All three sources are at daily grain and can be unioned by date and campaign identifiers without requiring user-level joins.
- Platform-specific fields are allowed to be NULL in the unified schema.
- CTR and CPC are safe to compute with protection against division by zero.

If this were production, I’d also add:

- A standard currency and timezone policy
- A campaign mapping layer for consistent naming across platforms
- Automated validation checks like row counts and metric totals before and after transformation


## 8) How to run it (7:50–8:20)

To generate the unified dataset locally:

- Run: `python build_unified_ads.py --out unified_ads.csv`

To run the dashboard:

- Run: `streamlit run app.py`
- Open the URL printed in the terminal, typically `http://localhost:8501`


## 9) Closing (8:20–8:40)

That’s the full walkthrough: I unified the three platform datasets into a standardized model and built a one-page dashboard to analyze cross-channel performance, trends, and efficiency, with drill-down to the campaign level.

Thanks for watching, and I’m happy to answer any questions or walk through additional analysis if needed.

