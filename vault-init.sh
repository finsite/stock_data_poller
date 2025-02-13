# echo "✅ Default secrets stored in Vault."
#!/bin/bash
echo "⏳ Waiting for Vault to become available..."
until curl -s --fail http://vault:8200/v1/sys/health > /dev/null; do
  sleep 2
done

echo "✅ Vault is ready. Populating default secrets..."

# Store default settings in Vault
curl --header "X-Vault-Token: root" \
     --request POST \
     --data '{
       "data": {
         "POLLER_TYPE": "stock",
         "QUEUE_TYPE": "rabbitmq",
         "SYMBOLS": "AAPL,GOOG,MSFT,TSLA,AMZN,FB,NVDA,AMD",
         "SQS_QUEUE_URL": "",
         "RABBITMQ_HOST": "localhost",
         "RABBITMQ_EXCHANGE": "stock_data_exchange",
         "RABBITMQ_ROUTING_KEY": "stock_data",
         "POLL_INTERVAL": "60",
         "REQUEST_TIMEOUT": "30",
         "MAX_RETRIES": "5",
         "RETRY_DELAY": "5",
         "LOG_LEVEL": "info",
         "POLYGON_API_KEY": "",
         "FINNHUB_API_KEY": "",
         "ALPHA_VANTAGE_API_KEY": "",
         "YFINANCE_API_KEY": "",
         "IEX_API_KEY": "",
         "QUANDL_API_KEY": "",
         "FINNHUB_FILL_RATE_LIMIT": "100",
         "POLYGON_FILL_RATE_LIMIT": "100",
         "ALPHA_VANTAGE_FILL_RATE_LIMIT": "100",
         "YFINANCE_FILL_RATE_LIMIT": "100",
         "IEX_FILL_RATE_LIMIT": "100",
         "QUANDL_FILL_RATE_LIMIT": "100",
         "ENABLE_LOGGING": "true",
         "CLOUD_LOGGING_ENABLED": "false",
         "CLOUD_LOGGING_ENDPOINT": "",
         "AWS_ACCESS_KEY_ID": "",
         "AWS_SECRET_ACCESS_KEY": "",
         "AWS_REGION": "us-east-1",
         "ENABLE_RETRY": "true",
         "ENABLE_BACKFILL": "false",
         "POLL_TIMEOUT": "30",
         "MAX_API_CALLS_PER_MIN": "1000"
       }
     }' http://vault:8200/v1/secret/data/poller

echo "✅ Default secrets stored in Vault."
