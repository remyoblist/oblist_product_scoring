import requests
import csv
import datetime

# /data-insights?pid=Dd7fSnDT9tWmrcZzcNaRORnEO10nDB%2B0ZCKCU6HvU0I%3D&start=2024-10-02&end=2024-10-09&metrics=recent_wishlist_products&limit=25&offset=0&ascending=false
# Swym API details
API_KEY = "p4HF6fKnJ2J1fbkRyXuAnLLEtDtzNnMiuYmm0WNyFcuMDh9BWe86HyBiXkidUD2j9_TAJDnqBdpYFoYOV4VVng"
PID = "Dd7fSnDT9tWmrcZzcNaRORnEO10nDB+0ZCKCU6HvU0I="
API_ENDPOINT = "https://swymstore-v3free-01.swymrelay.com/data-insights"  # Example endpoint for wishlist activity, adjust as needed

# Set the request headers, including the API key for authentication
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "PID": PID
}

# Define the date range (you can adjust these values as needed)
start_date = "2024-09-01"  # Start date (YYYY-MM-DD)
end_date = "2024-09-30"    # End date (YYYY-MM-DD)

# Fetch wishlist data with date range
def fetch_wishlist_data(start_date, end_date):
    # Construct the URL with date filters as query parameters
    url = f"https://admin.swymrelay.com/data-insights?pid=Dd7fSnDT9tWmrcZzcNaRORnEO10nDB%2B0ZCKCU6HvU0I%3D&start=2024-10-02&end=2024-10-09&metrics=recent_wishlist_products&limit=25&offset=0&ascending=false"
    print(url)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print(response.json())
        return response.json()
    else:
        print(f"Failed to fetch data: {response.status_code}, {response.text}")
        return None

# Export data to CSV
def export_to_csv(data):
    filename = f'wishlist_data_{datetime.datetime.now().strftime("%Y-%m-%d")}.csv'
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Write header row (adjust based on the API response structure)
        writer.writerow(["Customer", "Product", "Added Date", "Removed Date", "Conversions"])
        
        # Write data rows (assuming the API response is in a dictionary format, adjust field names accordingly)
        for activity in data:
            writer.writerow([
                activity.get("customer_email", "N/A"),
                activity.get("product_name", "N/A"),
                activity.get("added_date", "N/A"),
                activity.get("removed_date", "N/A"),
                activity.get("converted", "N/A")
            ])
    print(f'Data exported to {filename}')

# Main function to automate the process
def main():
    wishlist_data = fetch_wishlist_data(start_date, end_date)
    if wishlist_data:
        export_to_csv(wishlist_data)

if __name__ == "__main__":
    main()