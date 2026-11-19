"""One-time OAuth for the channel. Writes token.json (gitignored).
Usage: python -m engine.yt_auth      -> prints a URL; open it, pick the Simulated Societies channel, Allow.
Then:  python -m engine.yt_auth --check"""
import sys, json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parents[1]
SECRET, TOKEN = ROOT / "client_secret.json", ROOT / "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.force-ssl",      # thumbnails, captions, metadata
          "https://www.googleapis.com/auth/yt-analytics.readonly"]

def credentials():
    c = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if not c.valid:
        c.refresh(Request()); TOKEN.write_text(c.to_json())
    return c

def youtube(): return build("youtube", "v3", credentials=credentials())

if __name__ == "__main__":
    if "--check" in sys.argv:
        r = youtube().channels().list(part="snippet,statistics", mine=True).execute()
        for ch in r.get("items", []):
            print(ch["id"], ch["snippet"]["title"], ch["snippet"].get("customUrl"), ch["statistics"])
        sys.exit(0)
    flow = InstalledAppFlow.from_client_secrets_file(str(SECRET), SCOPES)
    c = flow.run_local_server(port=8765, open_browser=False, prompt="consent",
                              authorization_prompt_message="AUTH_URL {url}", success_message="Autorizado. Pode fechar esta aba.")
    TOKEN.write_text(c.to_json()); print("token.json salvo")
