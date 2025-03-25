import os
import pandas as pd
import itertools
from datetime import datetime, timedelta
from google.api_core import exceptions
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
from algoliasearch.search_client import SearchClient
from BrandPopularity import get_final_data

BOOST_VALUE = 0.2
ALGOLIA_APP_ID = "4YZ76ZGKZ7"
ALGOLIA_SEARCH_API_KEY = "4fbb2527c9f1061791ec1052a21a0b7b"
ALGOLIA_WRITE_API_KEY = "a2bfce7e551baabf7c45454a9a649cfc"

def setup_google_credentials(credentials_file: str):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file

def create_analytics_client() -> BetaAnalyticsDataClient:
    return BetaAnalyticsDataClient()

def run_google_analytics_report(client, start_date: str, end_date: str) -> pd.DataFrame:
    request = RunReportRequest(
        property="properties/352578491",
        dimensions=[Dimension(name="itemName")],
        metrics=[
            Metric(name="itemsViewed"),
            Metric(name="itemsPurchased"),
            Metric(name="itemsAddedToCart"),
            Metric(name="itemRevenue")
        ],
        date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
    )
    try:
        response = client.run_report(request, timeout=30)
    except exceptions.DeadlineExceeded:
        print("Deadline exceeded.")
        return pd.DataFrame()

    return parse_google_analytics_response(response)

def parse_google_analytics_response(response) -> pd.DataFrame:
    dimension_headers = [header.name for header in response.dimension_headers]
    metric_headers = [header.name for header in response.metric_headers]
    headers = dimension_headers + metric_headers

    data = []
    for row in response.rows:
        dimension_values = [dim.value for dim in row.dimension_values]
        metric_values = [met.value for met in row.metric_values]
        data.append(dimension_values + metric_values)

    return pd.DataFrame(data, columns=headers)

def fetch_algolia_data(market_name: str) -> pd.DataFrame:
    client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_SEARCH_API_KEY)
    index = client.init_index(market_name)
    records = index.browse_objects(
        {"attributesToRetrieve": [
            'title', 'created_at', 'meta.maxdeliverytime.maxdeltime',
            'meta.mindeliverytime.mindeltime', 'meta.custom.soldout',
            'meta.custom.curators_product', 'vendor', 'inventory_available', 'inventory_policy'
        ]}
    )
    return pd.DataFrame(list(records))

def initialize_dataframe_columns(df: pd.DataFrame, required_columns: dict):
    for column, default_value in required_columns.items():
        if column not in df.columns:
            df[column] = default_value
    return df

def parse_meta(meta_value, key_path: list, default_value=None):
    try:
        if pd.notna(meta_value):
            meta_dict = json.loads(meta_value) if isinstance(meta_value, str) else meta_value
            for key in key_path:
                meta_dict = meta_dict.get(key, {})
            return meta_dict or default_value
    except (ValueError, TypeError):
        pass
    return default_value

def add_meta_columns(df: pd.DataFrame):
    df['curators_product'] = df['meta'].apply(lambda meta: parse_meta(meta, ['custom', 'curators_product'], False))
    df['soldout'] = df['meta'].apply(lambda meta: parse_meta(meta, ['custom', 'soldout'], False))
    df['maxdeltime'] = df['meta'].apply(lambda meta: parse_meta(meta, ['maxdeliverytime', 'maxdeltime'], -1))
    df['mindeltime'] = df['meta'].apply(lambda meta: parse_meta(meta, ['mindeliverytime', 'mindeltime'], -1))
    return df

def safe_divide(numerator, denominator):
    return numerator / denominator if denominator not in (0, None) else 0

def calculate_conversion_rate(df: pd.DataFrame):
    df['itemsPurchased'] = pd.to_numeric(df['itemsPurchased'], errors='coerce')
    df['itemsViewed'] = pd.to_numeric(df['itemsViewed'], errors='coerce')
    df['ConversionRate'] = df.apply(lambda row: safe_divide(row['itemsPurchased'], row['itemsViewed']), axis=1)
    return df

def fetch_and_process_data(market_name: str, credentials_file: str) -> pd.DataFrame:
    # Set up environment and clients
    setup_google_credentials(credentials_file)
    analytics_client = create_analytics_client()

    # Define date ranges
    start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    end_date = (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d")

    # Fetch data from Google Analytics
    final_data = run_google_analytics_report(analytics_client, start_date, end_date)

    # Fetch data from Algolia
    algolia_df = fetch_algolia_data(market_name)
    algolia_df = initialize_dataframe_columns(algolia_df, {
        'meta': None,
        'created_at': None,
        'vendor': '',
        'inventory_available': False,
        'inventory_policy': 'deny'
    })
    algolia_df = add_meta_columns(algolia_df)

    # Merge Algolia data with Google Analytics data
    merged_df = merge_data(algolia_df, final_data)

    # Calculate additional scores
    merged_df = calculate_conversion_rate(merged_df)
    
    # Additional score calculations can go here
    
    return merged_df

def merge_data(algolia_df: pd.DataFrame, final_data: pd.DataFrame) -> pd.DataFrame:
    # Define merging logic and return the resulting DataFrame
    return algolia_df  # Example return; needs real merging logic

def sync_with_algolia(calc_df: pd.DataFrame, market_name: str):
    write_client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_WRITE_API_KEY)
    write_index = write_client.init_index(market_name)
    updates = [{'objectID': row['objectID'], 'product_score': row['ProductScore']} for _, row in calc_df.iterrows()]
    write_index.partial_update_objects(updates)

def main():
    main_markets = [
        "shopify_theoblistproducts", "shopify_theoblistproducts_france_fr",
        "shopify_theoblistproducts_australia_en", "shopify_theoblistproducts_australia_fr",
        # Add more market names here
    ]
    credentials_file = 'testmedium.json'
    
    for market in main_markets:
        print(f"Processing market: {market}")
        product_scores_df = fetch_and_process_data(market, credentials_file)
        sync_with_algolia(product_scores_df, market)
        print(f"Market {market} synced successfully.")

if __name__ == "__main__":
    main()