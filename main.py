import os
import pandas as pd
import itertools
from datetime import datetime, timedelta
from google.api_core import exceptions
import json
import tempfile

# Try to load .env file for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, skip
    pass

from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

def fetch_product_score(market_name) :
    import pandas as pd
    Boost_Value = 0.2
    # Reconstruct the credentials JSON from individual env variables
    google_creds = {
        "type": os.getenv("GOOGLE_TYPE"),
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n') if os.getenv("GOOGLE_PRIVATE_KEY") else None,
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": os.getenv("GOOGLE_AUTH_URI"),
        "token_uri": os.getenv("GOOGLE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("GOOGLE_AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
        "universe_domain": os.getenv("GOOGLE_UNIVERSE_DOMAIN"),    }
    if not all(google_creds.values()):
        print("Missing environment variables:")
        for key, value in google_creds.items():
            if value is None:
                print(f"  {key.upper().replace('_', '_')}: Not set")
        print("Full credentials dict:", google_creds)
        raise EnvironmentError("One or more Google credential environment variables are not set.")
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_cred_file:
        json.dump(google_creds, temp_cred_file)
        temp_cred_file_path = temp_cred_file.name
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_cred_file_path


    client = BetaAnalyticsDataClient()

    enddate = (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d")
    enddate_datetime = datetime.strptime(enddate, "%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    request_api = RunReportRequest(
        property="properties/352578491",
        dimensions=[
            Dimension(name="itemName") 
        ],
        metrics=[
            Metric(name="itemsViewed"),
            Metric(name="itemsPurchased"),
            Metric(name="itemsAddedToCart"),
            Metric(name="itemRevenue")
            ],
            date_ranges=[DateRange(start_date=enddate, end_date=start_date)],
        )

    try:
        response = client.run_report(request_api, timeout=30)  
    except exceptions.DeadlineExceeded:
        print("Deadline exceeded.")



    def query_data(api_response):
        import pandas as pd
        dimension_headers = [header.name for header in api_response.dimension_headers]
        metric_headers = [header.name for header in api_response.metric_headers]
        dimensions = []
        metrics = []

        for i in range(len(dimension_headers)):
            dimensions.append([row.dimension_values[i].value for row in api_response.rows])
        
        for i in range(len(metric_headers)):
            metrics.append([row.metric_values[i].value for row in api_response.rows])
        
        headers = dimension_headers, metric_headers
        headers = list(itertools.chain.from_iterable(headers))
        data = dimensions, metrics
        data = list(itertools.chain.from_iterable(data))
        df = pd.DataFrame(data)
        df = df.transpose()
        df.columns = headers

        # df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
        # df = df.sort_values(by=["date"], ascending=False)

        # df.insert(0, "date", df.pop("date")


        return df

    #query_data(response)

    final_data = query_data(response)
    # print(final_data)


    from algoliasearch.search_client import SearchClient

    # Connect and authenticate with your Algolia app
    client = SearchClient.create("4YZ76ZGKZ7", "4fbb2527c9f1061791ec1052a21a0b7b")

    # Create a new index and add a record
    index = client.init_index(market_name)

    # Perform a search query and retrieve specific attributes
    records = index.browse_objects(
        {"attributesToRetrieve": ['title', 'created_at','meta.maxdeliverytime.maxdeltime','meta.mindeliverytime.mindeltime','meta.custom.soldout', 'meta.custom.curators_product', 'vendor','inventory_available','inventory_policy',]}
    )

    data_list = list(records)
    # # # Convert the list of dictionaries to a Pandas DataFrame

    algolia_df = pd.DataFrame(data_list)
    print(algolia_df)
    # Check if 'meta' contains JSON-like data
    def parse_meta_column(meta_value):
        try:
            # Assuming 'meta' is a JSON string or dictionary
            if pd.notna(meta_value):  # Check if 'meta' is not NaN
                meta_dict = json.loads(meta_value) if isinstance(meta_value, str) else meta_value
                if meta_dict.get('custom', {}).get('curators_product', None) != True:
                    return False
                else:
                    return True
            return False
        except (ValueError, TypeError):
            return False
    def parse_meta_column_soldout(meta_value):
        try:
            # Assuming 'meta' is a JSON string or dictionary
            if pd.notna(meta_value):  # Check if 'meta' is not NaN
                if isinstance(meta_value, str):
                    meta_dict = json.loads(meta_value)
                else:
                    meta_dict = meta_value
                return meta_dict.get('custom', {}).get('soldout', None)
            return False
        except (ValueError, TypeError):
            return False
        
    def parse_meta_column_maxdeltime(meta_value):
        try:
            # Assuming 'meta' is a JSON string or dictionary
            if pd.notna(meta_value):  # Check if 'meta' is not NaN
                meta_dict = json.loads(meta_value) if isinstance(meta_value, str) else meta_value
                if meta_dict.get('maxdeliverytime', {}).get('maxdeltime', None) != None:
                    return meta_dict.get('maxdeliverytime', {}).get('maxdeltime', None)
                else:
                    return -1
            return -1
        except (ValueError, TypeError):
            return -1
    def parse_meta_column_mindeltime(meta_value):
        try:
            # Assuming 'meta' is a JSON string or dictionary
            if pd.notna(meta_value):  # Check if 'meta' is not NaN
                meta_dict = json.loads(meta_value) if isinstance(meta_value, str) else meta_value
                if meta_dict.get('mindeliverytime', {}).get('mindeltime', None) != None:
                    return meta_dict.get('mindeliverytime', {}).get('mindeltime', None)
                else:
                    return -1
            return -1
        except (ValueError, TypeError):
            return -1
    # Apply the function to extract 'curators_product'
    if 'meta' not in algolia_df.columns:
        algolia_df['meta'] = None
    if 'created_at' not in algolia_df.columns:
        algolia_df['created_at'] = None
    if 'vendor' not in algolia_df.columns:
        algolia_df['vendor'] = ''
    if 'inventory_available' not in algolia_df.columns:
        algolia_df['inventory_available'] = False
    if 'inventory_policy' not in algolia_df.columns:
        algolia_df['inventory_policy'] = 'deny'
    algolia_df['curators_product'] = algolia_df['meta'].apply(parse_meta_column)
    algolia_df['soldout'] = algolia_df['meta'].apply(parse_meta_column_soldout)
    algolia_df['maxdeltime'] = algolia_df['meta'].apply(parse_meta_column_maxdeltime)
    algolia_df['mindeltime'] = algolia_df['meta'].apply(parse_meta_column_mindeltime)


    # Save the DataFrame to CSV
    # algolia_df.to_csv('Algolia_data.csv', index=False)

    # Set the 'title' column as the index
    # algolia_df.set_index('title', inplace=True)

    # print(algolia_df)

    # Adjust the partial match function to avoid regex issues
    def partial_string_match(row, final_data):
    # Ensure both 'itemName' and 'title' are treated as strings
        if pd.notna(row['title']):
            title = str(row['title'])
        else:
            title = ""

        # Perform the string match
        matches = final_data[final_data['itemName'].astype(str).str.contains(title, case=False, na=False, regex=False)]
        
        if not matches.empty:
            # Return the first match, handle multiple matches if needed
            return pd.Series(matches.iloc[0])
        else:
            return pd.Series([None] * len(final_data.columns), index=final_data.columns)
    # Apply the function row-wise on algolia_df
    merged_df = algolia_df.apply(lambda row: partial_string_match(row, final_data), axis=1)

    # Concatenate the new columns from final_data with the original algolia_df
    calc_df = pd.concat([algolia_df, merged_df], axis=1)
    calc_df = calc_df.drop(columns=['itemName'])
    # print(algolia_df[])

    calc_df=calc_df.fillna(0)

    # Sample function for safe division
    def safe_divide(numerator, denominator):
        return numerator / denominator if denominator not in (0, None) else 0

    # First, ensure the columns 'itemsPurchased' and 'itemsViewed' are numeric
    calc_df['itemsPurchased'] = pd.to_numeric(calc_df['itemsPurchased'], errors='coerce')
    calc_df['itemsViewed'] = pd.to_numeric(calc_df['itemsViewed'], errors='coerce')

    # Calculate the ConversionRate using safe_divide
    calc_df['ConversionRate'] = calc_df.apply(lambda row: safe_divide(row['itemsPurchased'], row['itemsViewed']), axis=1)



    # Display the updated DataFrame All Basic Data for Calculate Product Score
    print(calc_df)
    # calc_df.to_csv('basic_data_calc_df.csv',index=False)

    #Calculate Sales Score
    max_sales=calc_df['itemsPurchased'].max()
    min_sales=calc_df['itemsPurchased'].min()
    tvalue_sales=max_sales-min_sales
    #print(tvalue_sales)
    calc_df['SalesScore'] = calc_df.apply(lambda row: 0.25 * safe_divide(row['itemsPurchased']-min_sales, tvalue_sales), axis=1)


    #Calculate ConversionRate
    max_conversion_rate=calc_df['ConversionRate'].max()
    min_conversion_rate=calc_df['ConversionRate'].min()
    tvalue_conversion_rate=max_conversion_rate-min_conversion_rate
    #print(tvalue_conversion_rate)
    calc_df['ConversionScore'] = calc_df.apply(lambda row: 0.2 * safe_divide(row['ConversionRate']-min_conversion_rate, tvalue_conversion_rate), axis=1)

    #UserEngement Calculate
    calc_df['itemsAddedToCart'] = pd.to_numeric(calc_df['itemsAddedToCart'], errors='coerce')
    min_add_cart=calc_df['itemsAddedToCart'].min()
    max_add_cart=calc_df['itemsAddedToCart'].max()
    tvalue_add_cart=max_add_cart-min_add_cart
    calc_df['UserEngagementScore'] = calc_df.apply(lambda row: 0.15 * safe_divide(row['itemsAddedToCart']-min_add_cart, tvalue_add_cart), axis=1)

    #Clculate Product Novelty Score
    calc_df['created_at'] = pd.to_datetime(calc_df['created_at'], errors = 'coerce')
    calc_df['created_at'] = calc_df['created_at'].dt.tz_localize(None)
    calc_df['ProductNoveltyScore'] = (datetime.now() - calc_df['created_at']).dt.days.fillna(0)

    max_product_novelty_days=calc_df['ProductNoveltyScore'].max()
    min_product_novelty_days=calc_df['ProductNoveltyScore'].min()
    tvalue_product_novelty_days=max_product_novelty_days-min_product_novelty_days
    #print(tvalue_product_novelty_days)
    calc_df['ProductNoveltyScore'] = calc_df.apply(lambda row: 0.1 * (1 - safe_divide(row['ProductNoveltyScore'], max_product_novelty_days)), axis=1)




    #Get the data Recent_sales and Previouse_sales
    client = BetaAnalyticsDataClient()
    enddate = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    enddate_datetime = datetime.strptime(enddate, "%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    request_api = RunReportRequest(
        property="properties/352578491",
        dimensions=[
            Dimension(name="itemName") 
        ],
        metrics=[
            Metric(name="itemsViewed"),
            Metric(name="itemsPurchased"),
            Metric(name="itemsAddedToCart"),
            Metric(name="itemRevenue")
            ],
            date_ranges=[DateRange(start_date=enddate, end_date=start_date)],
        )

    try:
        response = client.run_report(request_api, timeout=30)  
    except exceptions.DeadlineExceeded:
        print("Deadline exceeded.")

    #Data of recent 7days
    recent_data = query_data(response)

    enddate = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
    enddate_datetime = datetime.strptime(enddate, "%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d")

    request_api = RunReportRequest(
        property="properties/352578491",
        dimensions=[
            Dimension(name="itemName") 
        ],
        metrics=[
            Metric(name="itemsViewed"),
            Metric(name="itemsPurchased"),
            Metric(name="itemsAddedToCart"),
            Metric(name="itemRevenue")
            ],
            date_ranges=[DateRange(start_date=enddate, end_date=start_date)],
        )

    try:
        response = client.run_report(request_api, timeout=30)  
    except exceptions.DeadlineExceeded:
        print("Deadline exceeded.")

    #previouse_data 7 days before last week
    previouse_data = query_data(response)

    # import pandas as pd

    # previouse_df = {
    #     'itemName': [1, 2, 3, 4, 7, 6, 5],
    #     'ItemViewed': [6, 2, 6, 1, 3, 4, 5]
    # }

    # recent_df = {
    #     'itemName': [1, 2, 3, 4, 5, 6, 8, 9],
    #     'ItemViewed': [5, 1, 5, 0, 2, 3, 4, 10]
    # }

    # previouse_data = pd.DataFrame(previouse_df)
    # recent_data = pd.DataFrame(recent_df)

    # Convert itemName columns to string for both DataFrames
    previouse_data['itemName'] = previouse_data['itemName'].astype(str)
    recent_data['itemName'] = recent_data['itemName'].astype(str)

    def partial_string_match_seasonality(row, previouse_data):
        # Perform string match
        matches = previouse_data[previouse_data['itemName'].str.contains(row['itemName'], case=False, na=False, regex=False)]
        if not matches.empty:
            return pd.Series(matches.iloc[0])
        else:
            result = {col: 0 for col in previouse_data.columns}
            result['itemName'] = row['itemName']
            return pd.Series(result)

    # Apply the function
    previouse_data_updated = recent_data.apply(lambda row: partial_string_match_seasonality(row, previouse_data), axis=1)

    print(recent_data)
    print(previouse_data_updated)

    previouse_data_updated = previouse_data_updated.rename(columns = {'itemsViewed' : 'prvItemsViewed',
                                                                        'itemName' : 'prvItemName',
                                                                    'itemsPurchased' : 'prvItemsPurchased',
                                                                    'itemsAddedToCart' : 'prvItemsAddedToCart',
                                                                    'itemRevenue' : 'prvItemRevenue'  })
    calc_seasonality = pd.concat([recent_data,previouse_data_updated], axis = 1)
    calc_seasonality = calc_seasonality.drop(columns=['prvItemName'])

    calc_seasonality['ProductGrowthRate'] = calc_seasonality.apply(
        lambda row: safe_divide(
            (float(row['itemsPurchased']) - float(row['prvItemsPurchased'])), 
            float(row['prvItemsPurchased'])
        ) , axis=1
    )
    calc_seasonality['VisitsGrowthRate'] = calc_seasonality.apply(
        lambda row: safe_divide(
            (float(row['itemsViewed']) - float(row['prvItemsViewed'])), 
            float(row['prvItemsViewed'])
        ), axis=1
    )
    print(calc_seasonality)

    def partial_string_match_calcdf(row, calc_seasonality):
        # Ensure both 'itemName' and 'title' are treated as strings
        if pd.notna(row['title']):
            title = str(row['title'])
        else:
            title = ""

        # Convert 'itemName' to string and perform the string match
        matches = calc_seasonality[calc_seasonality['itemName'].astype(str).str.contains(title, case=False, na=False, regex=False)]
        
        if not matches.empty:
            # Return the first match, handle multiple matches if needed
            return pd.Series(matches.iloc[0])
        else:
            result = {col: 0 for col in calc_seasonality.columns}
            result['itemName'] = row['title']
            return pd.Series(result)


    # Apply the function row-wise on algolia_df
    filtered_seasonality_data = calc_df.apply(lambda row: partial_string_match_calcdf(row, calc_seasonality), axis=1)

    print(filtered_seasonality_data)


    # filtered_seasonality_data.to_csv('calculated_seasonality.csv',index=False)

    calc_df['ProductGrowthRate'] = filtered_seasonality_data['ProductGrowthRate']
    calc_df['VisitsGrowthRate'] = filtered_seasonality_data['VisitsGrowthRate']

    #Calculate CompositeScore
    max_visitsrate=calc_df['VisitsGrowthRate'].max()
    min_visitsrate=calc_df['VisitsGrowthRate'].min()
    max_productrate=calc_df['ProductGrowthRate'].max()
    min_productrate=calc_df['ProductGrowthRate'].min()
    delta_visitsrate=max_visitsrate-min_visitsrate
    delta_productrate=max_productrate-min_productrate

    calc_df['ProductGrowthRateNomalized']=calc_df.apply(lambda row: (row['ProductGrowthRate']-min_productrate)/delta_productrate,axis=1)
    calc_df['VisitGrowthRateNomalized']=calc_df.apply(lambda row: (row['VisitsGrowthRate']-min_visitsrate)/delta_visitsrate,axis=1)

    calc_df['CompositScore']=calc_df.apply(lambda row: (0.6*(row['ProductGrowthRate']-min_productrate)/delta_productrate)+(0.4*(row['VisitsGrowthRate']-min_visitsrate)/delta_visitsrate), axis=1)
    calc_df['CompositScoreBoosted'] = calc_df.apply(
        lambda row: row['CompositScore'] if row['curators_product'] == False else (row['CompositScore'] + Boost_Value), 
        axis=1
    )
    calc_df['CompositScoreFinal']=calc_df.apply(lambda row: min(row['CompositScoreBoosted'],1), axis=1)
    calc_df['isTrending']=calc_df.apply(lambda row: 1 if row['CompositScoreFinal']>= 0.6 else 0, axis=1)
    calc_df['SeasonalityScore']=calc_df.apply(lambda row: row['isTrending']*0.10, axis=1)

    print(calc_df)

    #Calculate BrandPopularity
    from BrandPopularity import get_final_data
    import pandas as pd

    # Get the brand data from the BrandPopularity module
    brand_df = get_final_data()

    def get_brand_popularityscore(row, brand_data):
        # Check if 'vendor' is NaN or 0
        if pd.isna(row['vendor']) or row['vendor'] == 0:
            return 0
        else:
            value = row['vendor']
            result = brand_data[brand_data['itemBrand'] == value]
            # Ensure that 'Popularity' exists and is not empty
            if not result.empty:
                return result['Popularity'].values[0]  # Use .values[0] to get the value from the series
            else:
                return 0  # If no match is found, return 0

    # Assuming calc_df is the dataframe you're applying the function to
    calc_df['BrandPopularityScore'] = calc_df.apply(lambda row: 0.1*get_brand_popularityscore(row, brand_df), axis=1)



    #Calculate the Logistic Perfermance
    calc_df['maxdeltime'] = pd.to_numeric(calc_df['maxdeltime'], errors='coerce')
    calc_df['mindeltime'] = pd.to_numeric(calc_df['mindeltime'], errors='coerce')
    max_totalmaxdeltime=calc_df['maxdeltime'].max()
    min_totalmindeltime = calc_df.loc[calc_df['mindeltime'] >= 0, 'mindeltime'].min()
    delta_totaldeltime=max_totalmaxdeltime-min_totalmindeltime
    calc_df['DeliveryTimeNormalized']=calc_df.apply(lambda row: 1-safe_divide((row['maxdeltime']-row['mindeltime']),delta_totaldeltime), axis=1)
    calc_df['DeliveryTimeNormalized']=calc_df['DeliveryTimeNormalized'].fillna(0)
    def calc_stockscore(row):
        if row['inventory_available']== True:
            return 1
        if row['inventory_policy']=="continue":
            return 0.7
        if row['soldout']==True:
            return 0
        else :
            return 0

    calc_df['StockScore']=calc_df.apply(lambda row: calc_stockscore(row), axis=1)

    calc_df['LogisticsPerformanceScore']=calc_df.apply(lambda row: 0.1*((row['StockScore']*0.4)+(row['DeliveryTimeNormalized']*0.3)),axis=1)

    #CalculateProductScore
    calc_df['ProductScore']=calc_df.apply(lambda row: row['UserEngagementScore']+row['SalesScore']+row['ConversionScore']+row['ProductNoveltyScore']+row['SeasonalityScore']+row['BrandPopularityScore']+row['LogisticsPerformanceScore'], axis=1)
    print(calc_df)
    print(market_name)
    save2csv_df = calc_df.loc[:, ['objectID','title','SalesScore', 'ConversionScore','UserEngagementScore','ProductNoveltyScore','SeasonalityScore','LogisticsPerformanceScore','BrandPopularityScore','ProductScore']]
    # Assuming calc_df is your DataFrame and you want to keep 'SalesScore', 'ConversionScore', 'ProductScore'
    calc_df = calc_df.loc[:, ['objectID', 'ProductScore']]
    return calc_df

def sync_with_algolia(calc_df,market_name):

    from algoliasearch.search_client import SearchClient
    partialObjects = list(calc_df)

    listOfReading= [{'objectID': row['objectID'], 'product_score': row['ProductScore']} for index, row in calc_df.iterrows() ]  


    # Connect and authenticate with your Algolia app
    write_client = SearchClient.create("4YZ76ZGKZ7", "a2bfce7e551baabf7c45454a9a649cfc")

    # Create a new index and add a record
    write_index = write_client.init_index(market_name)
    write_index.partial_update_objects(listOfReading)


from apscheduler.schedulers.blocking import BlockingScheduler
scheduler = BlockingScheduler()
# from algoliasearch.search_client import SearchClient
# admin_client = SearchClient.create("4YZ76ZGKZ7", "4cbb3c9578155c8e6b6e739703560726")

# indices = admin_client.list_indices()
# Print all index names
# @scheduler.scheduled_job('interval', hours=24)
# def update_product_scores():
# for market in main_markets:
#     products = fetch_product_score(market)
#     # Perform calculations here
#     sync_with_algolia(products,market)
# scheduler.start()
import concurrent.futures
def process_market(market_name: str, credentials_file: str):
    # Fetch and process product score for a given market
    try:
        products = fetch_product_score(market_name)
        sync_with_algolia(products, market_name)
        print(f"Market {market_name} processed and synced successfully.")
    except Exception as e:
        print(f"Error processing market {market_name}: {e}")

def main():
    main_markets=[
    "shopify_theoblistproducts",
    "shopify_theoblistproducts_france_fr",
    "shopify_theoblistproducts_australia_en",
    "shopify_theoblistproducts_australia_fr",
    "shopify_theoblistproducts_canada_en",
    "shopify_theoblistproducts_canada_fr",
    "shopify_theoblistproducts_eu_zone_en",
    "shopify_theoblistproducts_eu_zone_fr",
    "shopify_theoblistproducts_singapore_en",
    "shopify_theoblistproducts_singapore_fr",
    "shopify_theoblistproducts_south_korea_en",
    "shopify_theoblistproducts_south_korea_fr",
    "shopify_theoblistproducts_suisse_en",
    "shopify_theoblistproducts_suisse_fr",
    "shopify_theoblistproducts_uk_en",
    "shopify_theoblistproducts_uk_fr",
    "shopify_theoblistproducts_united_arab_emirates_en",
    "shopify_theoblistproducts_united_arab_emirates_fr",
    "shopify_theoblistproducts_united_states_en",
    "shopify_theoblistproducts_united_states_fr"
]
    # Remove usage of GOOGLE_APPLICATION_CREDENTIALS here, as it is now handled inside fetch_product_score

    print(" This is real main method")
    # Use ThreadPoolExecutor for threading
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit tasks to the executor for each market
        futures = [executor.submit(process_market, market, None) for market in main_markets]

        # Optionally, wait for all threads to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()