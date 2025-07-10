#!/usr/bin/env python3

import datetime
import logging
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Setup logging
log_file = "/tmp/order_reminders_log.txt"
logging.basicConfig(filename=log_file, level=logging.INFO)

# Get date range (last 7 days)
today = datetime.datetime.now()
seven_days_ago = today - datetime.timedelta(days=7)

# Setup GraphQL client
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=True,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=False)

# GraphQL query
query = gql("""
query GetRecentOrders($since: DateTime!) {
  allOrders(orderDate_Gte: $since) {
    edges {
      node {
        id
        customer {
          email
        }
      }
    }
  }
}
""")

# Execute query
params = {"since": seven_days_ago.isoformat()}
response = client.execute(query, variable_values=params)

# Log each order
timestamp = today.strftime("%Y-%m-%d %H:%M:%S")
orders = response.get("allOrders", {}).get("edges", [])

for order in orders:
    order_id = order["node"]["id"]
    customer_email = order["node"]["customer"]["email"]
    log_entry = f"[{timestamp}] Order ID: {order_id}, Customer Email: {customer_email}"
    logging.info(log_entry)

print("Order reminders processed!")
