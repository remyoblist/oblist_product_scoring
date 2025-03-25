from apscheduler.schedulers.blocking import BlockingScheduler
from data_ingestion.shopify import fetch_sales_data
from processing.calculation import calculate_product_score
from algolia_integration.algolia_sync import sync_with_algolia

scheduler = BlockingScheduler()

@scheduler.scheduled_job('interval', hours=24)
def update_product_scores():
    products = fetch_sales_data()
    # Perform calculations here
    sync_with_algolia(products)

scheduler.start()
