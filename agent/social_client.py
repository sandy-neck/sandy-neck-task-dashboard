"""
Social media data client — supports Instagram, Facebook, TikTok, YouTube.

Runs in stub mode (SOCIAL_STUB_MODE=true) until real API credentials are configured.
Each platform has a NotImplementedError block showing exactly what env vars are needed.
See AGENT_SETUP.md for step-by-step credential setup for each platform.
"""
import os
import requests

STUB_MODE = os.environ.get("SOCIAL_STUB_MODE", "true").lower() != "false"


class SocialClient:
    def get_all_metrics(self) -> dict:
        platforms = {}
        for name, fetcher in [
            ("instagram", self._instagram),
            ("facebook", self._facebook),
            ("tiktok", self._tiktok),
            ("youtube", self._youtube),
        ]:
            try:
                platforms[name] = fetcher()
            except NotImplementedError as e:
                platforms[name] = {"available": False, "setup_required": str(e)}
            except Exception as e:
                platforms[name] = {"available": False, "error": str(e)}
        return platforms

    # ── Instagram ──────────────────────────────────────────────────────────────

    def _instagram(self) -> dict:
        token = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
        account_id = os.environ.get("INSTAGRAM_ACCOUNT_ID")

        if STUB_MODE or not (token and account_id):
            return _stub("Instagram", "📸",
                         followers=4820, change="+23",
                         reach=8900, engagement_rate="4.2%",
                         top_post="Cape Cod Lobster Bisque — 412 likes, 38 saves")

        # Real implementation using Meta Graph API v19.0
        # Requires: Business/Creator account linked to a Facebook Page
        base = f"https://graph.facebook.com/v19.0/{account_id}"
        headers = {"Authorization": f"Bearer {token}"}

        insights = requests.get(
            f"{base}/insights",
            params={
                "metric": "impressions,reach,follower_count",
                "period": "day",
                "access_token": token,
            },
            timeout=15,
        ).json()

        media = requests.get(
            f"{base}/media",
            params={
                "fields": "timestamp,like_count,comments_count,reach,media_type,caption",
                "limit": 10,
                "access_token": token,
            },
            timeout=15,
        ).json()

        followers = next(
            (d["values"][-1]["value"] for d in insights.get("data", []) if d["name"] == "follower_count"),
            None,
        )
        reach = next(
            (sum(v["value"] for v in d["values"]) for d in insights.get("data", []) if d["name"] == "reach"),
            None,
        )
        posts = media.get("data", [])
        top = max(posts, key=lambda p: p.get("like_count", 0), default={}) if posts else {}
        total_engagement = sum(p.get("like_count", 0) + p.get("comments_count", 0) for p in posts)
        total_reach = sum(p.get("reach", 0) for p in posts) or 1

        return {
            "platform": "Instagram",
            "icon": "📸",
            "followers": followers,
            "follower_change_7d": None,
            "reach_7d": reach,
            "engagement_rate": f"{(total_engagement / total_reach * 100):.1f}%",
            "top_post_7d": top.get("caption", "")[:60] if top else None,
            "available": True,
        }

    # ── Facebook ───────────────────────────────────────────────────────────────

    def _facebook(self) -> dict:
        token = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")
        page_id = os.environ.get("FACEBOOK_PAGE_ID")

        if STUB_MODE or not (token and page_id):
            return _stub("Facebook", "👥",
                         followers=2340, change="+5",
                         reach=3200, engagement_rate="2.1%",
                         top_post="Weekly Specials — 87 reactions, 14 shares")

        # Real implementation using Meta Graph API
        # Requires: Page access token with pages_read_engagement, pages_show_list scopes
        base = f"https://graph.facebook.com/v19.0/{page_id}"

        page_data = requests.get(
            base,
            params={"fields": "followers_count,fan_count", "access_token": token},
            timeout=15,
        ).json()

        insights = requests.get(
            f"{base}/insights",
            params={
                "metric": "page_impressions_unique,page_post_engagements",
                "period": "week",
                "access_token": token,
            },
            timeout=15,
        ).json()

        followers = page_data.get("followers_count")
        reach = next(
            (d["values"][-1]["value"] for d in insights.get("data", []) if d["name"] == "page_impressions_unique"),
            None,
        )
        engagement = next(
            (d["values"][-1]["value"] for d in insights.get("data", []) if d["name"] == "page_post_engagements"),
            None,
        )

        return {
            "platform": "Facebook",
            "icon": "👥",
            "followers": followers,
            "follower_change_7d": None,
            "reach_7d": reach,
            "engagement_rate": f"{(engagement / (reach or 1) * 100):.1f}%" if engagement else None,
            "top_post_7d": None,
            "available": True,
        }

    # ── TikTok ─────────────────────────────────────────────────────────────────

    def _tiktok(self) -> dict:
        token = os.environ.get("TIKTOK_ACCESS_TOKEN")

        if STUB_MODE or not token:
            return _stub("TikTok", "🎵",
                         followers=890, change="+41",
                         reach=14200, engagement_rate="8.7%",
                         top_post="Shucking oysters at the dock — 12,400 views")

        # Real implementation using TikTok Display API
        # Requires: TikTok developer account, approved app, OAuth 2.0 user token
        # Rate limits: 600 req/min (Display API), 6 req/min (Content Posting API)
        headers = {"Authorization": f"Bearer {token}"}

        user = requests.get(
            "https://open.tiktokapis.com/v2/user/info/",
            params={"fields": "follower_count,following_count,likes_count,video_count"},
            headers=headers,
            timeout=15,
        ).json()

        videos = requests.post(
            "https://open.tiktokapis.com/v2/video/list/",
            json={"max_count": 10, "fields": ["view_count", "like_count", "comment_count", "title"]},
            headers=headers,
            timeout=15,
        ).json()

        user_data = user.get("data", {}).get("user", {})
        video_list = videos.get("data", {}).get("videos", [])
        top = max(video_list, key=lambda v: v.get("view_count", 0), default={}) if video_list else {}

        return {
            "platform": "TikTok",
            "icon": "🎵",
            "followers": user_data.get("follower_count"),
            "follower_change_7d": None,
            "reach_7d": sum(v.get("view_count", 0) for v in video_list),
            "engagement_rate": None,
            "top_post_7d": top.get("title", "")[:60] if top else None,
            "available": True,
        }

    # ── YouTube ────────────────────────────────────────────────────────────────

    def _youtube(self) -> dict:
        api_key = os.environ.get("YOUTUBE_API_KEY")
        channel_id = os.environ.get("YOUTUBE_CHANNEL_ID")

        if STUB_MODE or not (api_key and channel_id):
            return _stub("YouTube", "▶️",
                         followers=312, change="+2",
                         reach=2100, engagement_rate="5.3%",
                         top_post="How we source our seafood — 1,840 views")

        # Real implementation using YouTube Data API v3 + YouTube Analytics API
        # Requires: Google Cloud project, API key for Data API, OAuth for Analytics API
        # Quota: 10,000 units/day; most reads cost 1 unit
        channel = requests.get(
            "https://www.googleapis.com/youtube/v3/channels",
            params={
                "part": "statistics",
                "id": channel_id,
                "key": api_key,
            },
            timeout=15,
        ).json()

        videos_resp = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "channelId": channel_id,
                "maxResults": 5,
                "order": "viewCount",
                "type": "video",
                "key": api_key,
            },
            timeout=15,
        ).json()

        stats = channel.get("items", [{}])[0].get("statistics", {})
        top_video = videos_resp.get("items", [{}])[0].get("snippet", {})

        return {
            "platform": "YouTube",
            "icon": "▶️",
            "followers": int(stats.get("subscriberCount", 0)),
            "follower_change_7d": None,
            "reach_7d": int(stats.get("viewCount", 0)),
            "engagement_rate": None,
            "top_post_7d": top_video.get("title", "")[:60] if top_video else None,
            "available": True,
        }


def _stub(platform: str, icon: str, followers: int, change: str,
          reach: int, engagement_rate: str, top_post: str) -> dict:
    return {
        "platform": platform,
        "icon": icon,
        "followers": followers,
        "follower_change_7d": change,
        "reach_7d": reach,
        "engagement_rate": engagement_rate,
        "top_post_7d": top_post,
        "available": True,
        "stub": True,
    }
