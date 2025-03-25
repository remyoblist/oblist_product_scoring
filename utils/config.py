import os

# Shopify API Configuration
SHOPIFY_API_KEY = os.getenv('SHOPIFY_API_KEY')  # Set your Shopify API key in your environment variables
SHOPIFY_API_SECRET = os.getenv('SHOPIFY_API_SECRET')  # Set your Shopify API secret in your environment variables
SHOPIFY_STORE_NAME = os.getenv('SHOPIFY_STORE_NAME')  # Set your Shopify store name in your environment variables

# Google Analytics Configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')  # Set your Google API key in your environment variables
GOOGLE_ANALYTICS_VIEW_ID = os.getenv('GOOGLE_ANALYTICS_VIEW_ID')  # Set your Google Analytics View ID in your environment variables

# Algolia Configuration
ALGOLIA_APP_ID = os.getenv('ALGOLIA_APP_ID')  # Set your Algolia App ID in your environment variables
ALGOLIA_API_KEY = os.getenv('ALGOLIA_API_KEY')  # Set your Algolia API key in your environment variables

# Other configurations
DATA_DIR = os.getenv('DATA_DIR', 'data')  # Default directory for storing data
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # Default log level

# Add any other configurations as needed
