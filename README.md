# Algorithm Specification for Product Scoring and Brand Popularity Calculation for Algolia

## Introduction

This document outlines the algorithm for scoring products on The , aiming to predict and highlight products that are most likely to be purchased by visitors, **especially on their first visit**. It provides detailed instructions on data collection and the necessary calculations to implement the algorithm effectively.

### Why do must implement this algorithm?

Calculations such as normalization, custom weightings and specific formulas cannot be implemented directly in Algolia without data pre-processing. Although Algolia is powerful for search, it is designed to be fed with pre-processed data and cannot guess or create scores without explicit guidelines.

While Algolia's AI Personalization offers valuable features for tailoring search results to individual users, it does not replace the need for a custom scoring algorithm.
By implementing our own algorithm, we ensure that all the unique aspects of our products and marketplace are accurately reflected in search rankings and product visibility. This tailored approach enhances user satisfaction, promotes fairness among sellers, and ultimately drives higher conversion rates.

## Objectives

1. **Collect all necessary data** from various sources.
2. **Perform the required calculations** as per the specifications.
3. **Synchronize** calculation result to Algolia

# I. Product Scoring Algorithm

### Factors to Consider

1. **Sales History**
2. **Conversion Rate**
3. **User Engagement**
4. **Product Novelty**
5. **Seasonality and Trends**
6. **Stock Availability**
7. **Brand Popularity**

### Adjusted Factor Weights

- **Sales History**: **25%**
- **Conversion Rate**: **20%**
- **User Engagement**: **15%**
- **Product Novelty**: **10%**
- **Seasonality and Trends**: **10%**
- **Stock Availability**: **10%**
- **Brand Popularity**: **10%**

**Total**: 100%

### Data Collection

For each product, collect the following data:

1. **Sales History**:
   - Number of sales in the last 30 days.
2. **Conversion Rate**:
   - Number of sales divided by the number of product page visits.
3. **User Engagement**:
   - Number of adds to cart.
   - Number of adds to wishlist.
4. **Product Novelty**:
   - Number of days since the product was added to the catalog.
5. **Seasonality and Trends**:
   - Indicator if the product is currently trending (1 for Yes, 0 for No).
6. **Stock Availability**:
   - For products **not made-to-order** (`made_to_order = No`):
     - Current stock level as a percentage.
   - For products **made-to-order** (`made_to_order = Yes`):
     - Minimum delivery time in weeks (`min_delivery_time`).
     - Maximum delivery time in weeks (`max_delivery_time`).
7. **Brand Popularity**:
   - Calculated separately (see Section II).

### Calculations

For each factor, perform the following steps:

### 1. Normalization

Normalize each factor to a value between 0 and 1, where applicable.

### 2. Partial Score Calculation

Multiply each normalized factor value by its corresponding weight.

### 3. Total Product Score

Sum all the partial scores to get the total product score.

### Detailed Calculations

### 1. Sales History (25%)

- **Normalized Value**:

```
Sales_Normalized = (Product_Sales - Min_Sales) / (Max_Sales - Min_Sales)
```

**Partial Score**:

```
Sales_Score = Sales_Normalized * 0.25
```

### 2. Conversion Rate (20%)

- **Conversion Rate**:

  ```

  Conversion_Rate = Number_of_Sales / Number_of_Visits
  ```

- **Normalized Value**:
  ```
  Conversion_Normalized = (Conversion_Rate - Min_Conversion_Rate) / (Max_Conversion_Rate - Min_Conversion_Rate)
  ```
- **Partial Score**:
  ```makefile
  Conversion_Score = Conversion_Normalized * 0.20
  ```

### 3. User Engagement (15%)

- **Engagement Metric**:
  ```
  Engagement_Total = Adds_to_Cart + Adds_to_Wishlist
  ```
- **Normalized Value**:
  ```
  Engagement_Normalized = (Engagement_Total - Min_Engagement) / (Max_Engagement - Min_Engagement)
  ```
- **Partial Score**:
  ```makefile
  Engagement_Score = Engagement_Normalized * 0.15
  ```

### 4. Product Novelty (10%)

- **Normalized Value**:

```
Novelty_Normalized = 1 - (Days_Since_Added / Max_Days_Since_Added)
```

- **Partial Score**:
  ```makefile
  Novelty_Score = Novelty_Normalized * 0.10
  ```

### 5. Seasonality and Trends (10%)

```makefile
Seasonality_Score = Seasonality_Value * 0.10
```

**Determining if a Product is Trending**

### a. Calculate Growth Rates

1. **Product Growth Rate**:

   ```makefile
   Product_Growth_Rate = (Recent_Sales - Previous_Sales) / Previous_Sales
   ```

   - _Recent_Sales_: Sales in the last 7 days.
   - _Previous_Sales_: Sales in the 7 days before the recent 7 days.

2. **Number of Visits Growth Rate**:

   ```makefile
   Visits_Growth_Rate = (Recent_Visits - Previous_Visits) / Previous_Visits
   ```

   - _Recent_Visits_: Visits in the last 7 days.
   - _Previous_Visits_: Visits in the 7 days before the recent 7 days.

### b. Normalize the Metrics

To combine them effectively, normalize both metrics to a scale between 0 and 1.

1. **Normalize the Growth Rate**:

   ```scss
   Normalized_Growth_Rate = (Product_Growth_Rate - Min_Growth_Rate) / (Max_Growth_Rate - Min_Growth_Rate)
   ```

2. **Normalize the Visits Growth Rate**:

   ```scss
   Normalized_Visits_Rate = (Visits_Growth_Rate - Min_Visits_Rate) / (Max_Visits_Rate - Min_Visits_Rate)
   ```

### c. Assign Weights to the Metrics

Assign weights based on the relative importance of each metric:

- **Weight for Growth Rate (W1)**: 0.6 (60% of the composite score).
- **Weight for Visits Growth Rate (W2)**: 0.4 (40% of the composite score).

_Note_: The weights should sum up to 1 (W1 + W2 = 1).

### d. Calculate Composite Score

```scss
Composite_Score = (Normalized_Growth_Rate * W1) + (Normalized_Visits_Rate * W2)
```

### e. Determine if Product is Trending

- **Threshold**: Set a threshold of 0.6.
  - If `Composite_Score >= 0.6`, the product is considered **Trending (1)**.
  - If `Composite_Score < 0.6`, the product is **Not Trending (0)**.
- **Practical Implementation**: Update a metafield `is_trending` for each product with the result (1 for Yes, 0 for No).

### 6. Stock Availability (10%)

For Products Not Made-to-Order (`made_to_order = No`):

- **Normalized Value**:
  ```makefile
  Stock_Normalized = Stock_Percentage / 100
  ```

For Products Made-to-Order (`made_to_order = Yes`):

- **Average Delivery Time**:
  ```makefile
  Delivery_Time_Average = (Min_Delivery_Time + Max_Delivery_Time) /
  ```
- **Normalized Delivery Time**:
  ```scss
  Delivery_Time_Normalized = (Delivery_Time_Average - Min_Delivery_Time_All) / (Max_Delivery_Time_All - Min_Delivery_Time_All)
  ```
- **Stock_Normalized**:
  ```makefile
  Stock_Normalized = 1 - Delivery_Time_Normalized
  ```

<aside>
💡

_Note_: `Min_Delivery_Time_All` and `Max_Delivery_Time_All` are the minimum and maximum delivery times across all made-to-order products.

</aside>

### Partial Score (for all products):

```makefile
Stock_Score = Stock_Normalized * 0.10
```

### 7. Brand Popularity (10%)

- **Value**:
  ```css
  Brand_Popularity_Score = Calculated from Section II
  ```
- **Partial Score**:
  ```makefile
  Brand_Popularity_Score = Brand_Popularity_Score * 0.10
  ```

### Total Product Score

```makefile
Personalization_Score = Personalization_Value * 0.05
```

```makefile
Total_Score = Sales_Score + Conversion_Score + Engagement_Score + Novelty_Score + Seasonality_Score + Stock_Score + Brand_Popularity_Score
```

# II. Brand Popularity Calculation

### Factors to Consider

1. **Number of Followers (25%)**
2. **Number of Visits to Seller's Collection (15%)**
3. **Seller's Conversion Rate (40%)**
4. **Seller's Total Sales (20%)**

### Data Collection

For each seller, collect the following data:

1. **Number of Followers**
2. **Number of Visits to Seller's Collection**
3. **Seller's Conversion Rate**:

   ```makefile
   Seller_Conversion_Rate = Seller_Total_Sales / Seller_Total_Visits
   ```

4. **Seller's Total Sales**

### Calculations

### 1. Normalization

Normalize each metric to a value between 0 and 1.

- **Followers Normalized**:
  ```scss
  Followers_Normalized = (Seller_Followers - Min_Followers) / (Max_Followers - Min_Followers)
  ```
- **Visits Normalized**:
  ```scss
  Visits_Normalized = (Seller_Visits - Min_Visits) / (Max_Visits - Min_Visit
  ```
- **Conversion Rate Normalized**:
  ```scss
  Conversion_Rate_Normalized = (Seller_Conversion_Rate - Min_Conversion_Rate) / (Max_Conversion_Rate - Min_Conversion_Rate
  ```
- **Sales Normalized**:
  ```scss
  Sales_Normalized = (Seller_Total_Sales - Min_Sales) / (Max_Sales - Min_Sales)
  ```

2. Partial Scores

- **Followers Score**:
  ```makefile
  Followers_Score = Followers_Normalized * 0.2
  ```
- **Visits Score**:
  ```makefile
  Visits_Score = Visits_Normalized * 0.1
  ```
- **Conversion Rate Score**:
  ```makefile
  Conversion_Score = Conversion_Rate_Normalized * 0.4
  ```
- **Sales Score**:
  ```makefile
  Sales_Score = Sales_Normalized * 0.20
  ```

### 3. Total Brand Popularity Score

```makefile
Brand_Popularity_Score = Followers_Score + Visits_Score + Conversion_Score + Sales_Score
```

# III. Data Requirements and Sources

### 1. Sales Data

- **Source**: Shopify sales records.
- **Data Points**:
  - Number of sales per product.
  - Number of sales per seller.

### 2. Traffic Data

- **Source**: Shopify Analytics or integrated analytics tools (e.g., Google Analytics).
- **Data Points**:
  - Number of product page visits.
  - Number of visits to seller's collection pages.

### 3. Engagement Data

- **Source**: Shopify store data, plugins, or custom tracking.
- **Data Points**:
  - Adds to cart.
  - Adds to wishlist.

### 4. Product Information

- **Source**: Shopify product catalog.
- **Data Points**:
  - Date added to catalog.
  - Stock levels.
  - Made-to-order status (`made_to_order` metafield).
  - Minimum and maximum delivery times (`min_delivery_time`, `max_delivery_time`).

### 5. Trend Indicators

- **Source**: Internal tracking
- **Data Points**:
  - Whether the product is currently trending.

### 6. Seller Information

- **Source**: Shopify seller profiles, social media.
- **Data Points**:
  - Number of followers (on the platform and/or social media).
  - Seller's conversion rates.
  - Total sales per seller.

# IV. Implementation Steps

### 1. Data Collection

- **Automate data retrieval** using scripts or APIs.
- **Ensure data accuracy and freshness** by scheduling regular updates.
- **Handle missing data** appropriately (e.g., use default values or exclude from calculations).

### 2. Data Normalization

- For each metric requiring normalization:
  - **Determine minimum and maximum values** across all products/sellers.
  - **Update these values periodically** to reflect current data ranges.

### 3. Calculations

- **Implement functions** to perform normalization and partial score calculations.
- **Ensure calculations are efficient** and can handle large datasets.

### 4. Stock Availability Calculation Details

### For Products Not Made-to-Order (`made_to_order = No`):

- Use current stock levels to calculate availability.
  ```makefile
  Stock_Normalized = Stock_Percentage / 100
  ```

### For Products Made-to-Order (`made_to_order = Yes`):

- Calculate the average delivery time:
  ```makefile
  Delivery_Time_Average = (Min_Delivery_Time + Max_Delivery_Time) /
  ```
- Determine the overall minimum and maximum delivery times across all made-to-order products:
  ```sql
  Min_Delivery_Time_All = Minimum of all Min_Delivery_Time values
  Max_Delivery_Time_All = Maximum of all Max_Delivery_Time values
  ```
- Normalize the average delivery time:
  ```scss
  Delivery_Time_Normalized = (Delivery_Time_Average - Min_Delivery_Time_All) / (Max_Delivery_Time_All - Min_Delivery_Time_All)
  ```
- Calculate Stock Availability:
  ```makefile
  Stock_Normalized = 1 - Delivery_Time_Normalized
  ```

_Explanation_: A shorter delivery time results in a higher stock availability score.

# V. Notes for the Developer

- **Accuracy is Crucial**:
  - Double-check all calculations and data handling.
- **Performance Considerations**:
  - Optimize queries and calculations to prevent slowdowns.
- **Data Privacy**:
  - Comply with GDPR and other data protection regulations.
  - Handle personal data responsibly.
- **Scalability**:
  - Design the system to handle growth in products and traffic.
- **Documentation**:
  - Document code, data sources, and processes for future reference.
- **Communication**:
  - Keep open communication regarding any challenges or suggestions.

---

## VI. Final Step Integration with Algolia

Algolia will utilize the calculated product scores to enhance search results and product listings on our platform. By indexing these scores, Algolia can:

- **Influence Search Rankings**: Products with higher scores will appear higher in search results, making them more visible to users.
- **Improve Relevance**: The algorithm ensures that products displayed are more likely to meet user expectations and preferences.
- **Enhance User Experience**: By showcasing products that are more popular and readily available, we improve customer satisfaction.
- **Increase Conversion Rates**: Prioritizing products with higher purchase likelihood can lead to more sales.

To implement this:

- **Index Calculated Scores**: Ensure that the product scores and brand popularity scores are included in the data sent to Algolia.
- **Configure `customRanking`**: In Algolia's settings, use these scores in the `customRanking` attribute to sort products accordingly.
- **Regular Updates**: Keep the Algolia index updated with the latest scores to maintain accuracy.

_By integrating the algorithm with Algolia, we leverage its powerful search and indexing capabilities to deliver a more dynamic and effective product discovery experience._
