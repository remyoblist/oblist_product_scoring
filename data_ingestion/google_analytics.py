from googleapiclient.discovery import build
from utils.config import GOOGLE_ANALYTICS_VIEW_ID, GOOGLE_API_KEY

def fetch_traffic_data():
    analytics = build('analytics', 'v3', developerKey=GOOGLE_API_KEY)
    response = analytics.data().ga().get(
        ids=f'ga:{GOOGLE_ANALYTICS_VIEW_ID}',
        start_date='30daysAgo',
        end_date='today',
        metrics='ga:pageviews'
    ).execute()
    return response