from normalization import normalize

def calculate_product_score(sales, visits, engagement, novelty, stock, trend, brand_popularity):
    sales_score = normalize(sales, min_sales, max_sales) * 0.25
    conversion_score = normalize(conversion_rate, min_conversion, max_conversion) * 0.20
    engagement_score = normalize(engagement, min_engagement, max_engagement) * 0.15
    novelty_score = normalize(novelty, min_novelty, max_novelty) * 0.10
    stock_score = normalize(stock, min_stock, max_stock) * 0.10
    trend_score = trend * 0.10
    brand_score = brand_popularity * 0.10

    total_score = sales_score + conversion_score + engagement_score + novelty_score + stock_score + trend_score + brand_score
    return total_score
