# import os
# import pandas as pd
# import itertools
# from datetime import datetime, timedelta
# from google.api_core import exceptions

# from google.analytics.data_v1beta import BetaAnalyticsDataClient
# from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

# Boost_Value = 0.2

# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'testmedium.json'

# client = BetaAnalyticsDataClient()

# enddate = (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d")
# enddate_datetime = datetime.strptime(enddate, "%Y-%m-%d")
# start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# request_api = RunReportRequest(
#     property="properties/352578491",
#     dimensions=[
#         Dimension(name="itemBrand") 
#     ],
#     metrics=[
#         Metric(name="itemsViewed"),
#         Metric(name="itemsPurchased"),
#         Metric(name="itemsAddedToCart"),
#         Metric(name="itemRevenue")
#         ],
#         date_ranges=[DateRange(start_date=enddate, end_date=start_date)],
#     )

# try:
#     response = client.run_report(request_api, timeout=30)  
# except exceptions.DeadlineExceeded:
#     print("Deadline exceeded.")



# def query_data(api_response):
#     dimension_headers = [header.name for header in api_response.dimension_headers]
#     metric_headers = [header.name for header in api_response.metric_headers]
#     dimensions = []
#     metrics = []

#     for i in range(len(dimension_headers)):
#         dimensions.append([row.dimension_values[i].value for row in api_response.rows])
    
#     for i in range(len(metric_headers)):
#         metrics.append([row.metric_values[i].value for row in api_response.rows])
    
#     headers = dimension_headers, metric_headers
#     headers = list(itertools.chain.from_iterable(headers))
#     data = dimensions, metrics
#     data = list(itertools.chain.from_iterable(data))
#     df = pd.DataFrame(data)
#     df = df.transpose()
#     df.columns = headers

#     # df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
#     # df = df.sort_values(by=["date"], ascending=False)

#     # df.insert(0, "date", df.pop("date")


#     return df

# #query_data(response)

# final_data = query_data(response)
# print(final_data)

# def safe_divide(numerator, denominator):
#     return numerator / denominator if denominator not in (0, None) else 0
# #Visits_score Calcualtion
# #Vsits Normlized
# final_data['itemsViewed'] = pd.to_numeric(final_data['itemsViewed'], errors='coerce')
# min_visits=final_data['itemsViewed'].min()
# max_visits=final_data['itemsViewed'].max()
# delta_visits=max_visits-min_visits
# final_data['VisitsScore']=final_data.apply(lambda row: 0.1*safe_divide(row['itemsViewed']-min_visits, delta_visits),axis=1)
# print(final_data)

# #ConversionRate Calculation
# final_data['itemsPurchased'] = pd.to_numeric(final_data['itemsPurchased'], errors='coerce')
# final_data['ConversionRate']=final_data.apply(lambda row: safe_divide(row['itemsViewed'],row['itemsPurchased']), axis=1)

# min_CVR=final_data['ConversionRate'].min()
# max_CVR=final_data['ConversionRate'].max()
# delta_CVR=max_CVR-min_CVR
# final_data['ConversionScore']=final_data.apply(lambda row: 0.4*safe_divide(row['ConversionRate']-min_CVR, delta_CVR),axis=1)

# #Sales Score
# min_sales=final_data['itemsPurchased'].min()
# max_sales=final_data['itemsPurchased'].max()
# delta_sales=max_sales-min_sales
# final_data['SalesScore']=final_data.apply(lambda row: 0.2*safe_divide(row['itemsPurchased']-min_sales, delta_sales),axis=1)
# final_data['Popularity']=final_data.apply(lambda row: row['ConversionScore']+row['SalesScore']+row['VisitsScore'],axis=1)


# print(final_data)
# final_data.to_csv('BrandPopularity.csv',index=False)  
# BrandPopularity.py

import os
import pandas as pd
import itertools
from datetime import datetime, timedelta
from google.api_core import exceptions
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

Boost_Value = 0.2

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'testmedium.json'
client = BetaAnalyticsDataClient()

enddate = (datetime.now() - timedelta(days=28)).strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

def get_final_data():
    request_api = RunReportRequest(
        property="properties/352578491",
        dimensions=[Dimension(name="itemBrand")],
        metrics=[
            Metric(name="itemsViewed"),
            Metric(name="itemsPurchased"),
            Metric(name="itemsAddedToCart"),
            Metric(name="itemRevenue")
        ],
        date_ranges=[DateRange(start_date=enddate, end_date=start_date)]
    )

    try:
        response = client.run_report(request_api, timeout=30)
    except exceptions.DeadlineExceeded:
        print("Deadline exceeded.")
        return None

    def query_data(api_response):
        # Extract headers
        dimension_headers = [header.name for header in api_response.dimension_headers]
        metric_headers = [header.name for header in api_response.metric_headers]
        
        # Combine dimension and metric headers into one list of columns
        headers = dimension_headers + metric_headers

        # Initialize lists to store rows of data
        rows = []
        
        # Loop through each row of the response
        for row in api_response.rows:
            # Get dimension values for this row
            dimension_values = [dimension_value.value for dimension_value in row.dimension_values]
            
            # Get metric values for this row
            metric_values = [metric_value.value for metric_value in row.metric_values]
            
            # Combine dimension and metric values into a single row
            rows.append(dimension_values + metric_values)

        # Create a DataFrame using the rows and headers
        df = pd.DataFrame(rows, columns=headers)
        
        return df

    final_data = query_data(response)

    # Add additional calculations
    final_data['itemsViewed'] = pd.to_numeric(final_data['itemsViewed'], errors='coerce')
    min_visits = final_data['itemsViewed'].min()
    max_visits = final_data['itemsViewed'].max()
    delta_visits = max_visits - min_visits
    final_data['VisitsScore'] = final_data.apply(lambda row: 0.1 * safe_divide(row['itemsViewed'] - min_visits, delta_visits), axis=1)

    # Conversion Rate calculation
    final_data['itemsPurchased'] = pd.to_numeric(final_data['itemsPurchased'], errors='coerce')
    final_data['ConversionRate'] = final_data.apply(lambda row: safe_divide(row['itemsViewed'], row['itemsPurchased']), axis=1)

    min_CVR = final_data['ConversionRate'].min()
    max_CVR = final_data['ConversionRate'].max()
    delta_CVR = max_CVR - min_CVR
    final_data['ConversionScore'] = final_data.apply(lambda row: 0.4 * safe_divide(row['ConversionRate'] - min_CVR, delta_CVR), axis=1)

    # Sales Score
    min_sales = final_data['itemsPurchased'].min()
    max_sales = final_data['itemsPurchased'].max()
    delta_sales = max_sales - min_sales
    final_data['SalesScore'] = final_data.apply(lambda row: 0.2 * safe_divide(row['itemsPurchased'] - min_sales, delta_sales), axis=1)

    final_data['Popularity'] = final_data.apply(lambda row: row['ConversionScore'] + row['SalesScore'] + row['VisitsScore'], axis=1)

    return final_data

def safe_divide(numerator, denominator):
    return numerator / denominator if denominator not in (0, None) else 0


