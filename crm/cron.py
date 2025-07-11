import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime
import os

def log_crm_heartbeat():
    now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{now} CRM is alive"

    try:
        # Set up the GraphQL client
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)

        # Perform a hello query
        query = gql("{ hello }")
        result = client.execute(query)
        if "hello" in result:
            message += f" - GraphQL says: {result['hello']}"
    except Exception as e:
        message += f" - GraphQL query failed: {e}"

    # Append the heartbeat message to the log
    with open("/tmp/crm_heartbeat_log.txt", "a") as log:
        log.write(message + "\n")


def update_low_stock():
    now = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_path = "/tmp/low_stock_updates_log.txt"

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)

    
        mutation = gql("""
            mutation {
                updateLowStockProducts {
                    updatedProducts {
                        name
                        stock
                    }
                    message
                }
            }
        """)

        result = client.execute(mutation)
        updates = result["updateLowStockProducts"]["updatedProducts"]
        message = result["updateLowStockProducts"]["message"]

        with open(log_path, "a") as log:
            log.write(f"[{now}] {message}\n")
            for p in updates:
                log.write(f"[{now}] Product: {p['name']} - Stock: {p['stock']}\n")

    except Exception as e:
        with open(log_path, "a") as log:
            log.write(f"[{now}] Error: {str(e)}\n")
