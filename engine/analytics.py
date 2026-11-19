"""Pulls everything we track from the YouTube Data + Analytics APIs, on demand (the API keeps the history,
so there is no need to collect daily). Analytics rows lag ~48 h behind; Data API counters are live.
Usage: python -m engine.analytics          -> prints a summary and writes data/analytics/YYYY-MM-DD.json"""
import json, datetime
from pathlib import Path
from googleapiclient.discovery import build
from engine.yt_auth import youtube, credentials

ROOT = Path(__file__).resolve().parents[1]
START = "2026-11-17"   # day before the first upload

def _q(ya, dims, metrics, **kw):
    try:
        r = ya.reports().query(ids="channel==MINE", startDate=START, endDate=datetime.date.today().isoformat(),
                               dimensions=dims, metrics=metrics, **kw).execute()
        return {"cols": [h["name"] for h in r["columnHeaders"]], "rows": r.get("rows", [])}
    except Exception as e:
        return {"error": str(e)[:300]}

def pull():
    yt = youtube(); ya = build("youtubeAnalytics", "v2", credentials=credentials())
    ch = yt.channels().list(part="statistics,contentDetails", mine=True).execute()["items"][0]
    ids, tok = [], None
    while True:
        p = yt.playlistItems().list(part="contentDetails", playlistId=ch["contentDetails"]["relatedPlaylists"]["uploads"],
                                    maxResults=50, pageToken=tok).execute()
        ids += [i["contentDetails"]["videoId"] for i in p["items"]]; tok = p.get("nextPageToken")
        if not tok: break
    videos = {}
    for i in range(0, len(ids), 50):
        for v in yt.videos().list(part="snippet,statistics,contentDetails,status", id=",".join(ids[i:i + 50])).execute()["items"]:
            videos[v["id"]] = {"title": v["snippet"]["title"], "published": v["snippet"]["publishedAt"],
                               "duration": v["contentDetails"]["duration"], "privacy": v["status"]["privacyStatus"],
                               **{k: int(x) for k, x in v["statistics"].items()}}
    core = "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,likes,comments,shares"
    out = {"pulled_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "channel": {k: int(x) for k, x in ch["statistics"].items() if isinstance(x, str) and x.isdigit()},
           "videos": videos,
           "by_video": _q(ya, "video", core, sort="-views", maxResults=50),
           "by_day": _q(ya, "day", core),
           # Impressions and CTR: the API rejected videoThumbnailImpressions* in every shape tried (2026-11-18,
           # "query is not supported"), so those two numbers have to be read in Studio > Analytics > Reach.
           "traffic": _q(ya, "insightTrafficSourceType", "views,estimatedMinutesWatched", sort="-views"),
           "traffic_by_video": _q(ya, "video,insightTrafficSourceType", "views,estimatedMinutesWatched"),
           "search_terms": _q(ya, "insightTrafficSourceDetail", "views", filters="insightTrafficSourceType==YT_SEARCH", sort="-views", maxResults=25),
           "countries": _q(ya, "country", "views,estimatedMinutesWatched", sort="-views", maxResults=15),
           "retention": {vid: _q(ya, "elapsedVideoTimeRatio", "audienceWatchRatio,relativeRetentionPerformance", filters=f"video=={vid}")
                         for vid in ids}}
    return out

if __name__ == "__main__":
    d = pull()
    dest = ROOT / "data/analytics"; dest.mkdir(parents=True, exist_ok=True)
    f = dest / f"{datetime.date.today().isoformat()}.json"; f.write_text(json.dumps(d, indent=1))
    print("channel", d["channel"])
    for vid, v in d["videos"].items():
        print(f"  {vid}  {v.get('viewCount', 0):>6} views  {v.get('likeCount', 0):>3} likes  {v.get('commentCount', 0):>3} comments  {v['duration']:>9}  {v['title']}")
    for k in ("by_video", "traffic", "search_terms", "countries"):
        r = d[k]; print(k, r.get("error") or r["cols"], *(r.get("rows") or ["(sem linhas ainda)"]), sep="\n   ")
    for vid, r in d["retention"].items():
        rows = r.get("rows") or []
        if rows:
            at = lambda x: min(rows, key=lambda row: abs(row[0] - x))[1]
            print(f"retention {vid}: 5% {at(.05):.2f}  25% {at(.25):.2f}  50% {at(.5):.2f}  90% {at(.9):.2f}")
    print("saved", f)
