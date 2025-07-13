import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime
import os
from django.conf import settings
import json

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
    """Update low stock products and log the results."""
    # Setup GraphQL client
    transport = RequestsHTTPTransport(
        url=getattr(settings, 'GRAPHQL_ENDPOINT', 'http://localhost:8000/graphql/'),
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Define the mutation
    mutation = gql("""
        mutation UpdateLowStock {
            updateLowStockProducts {
                success
                message
                updatedProducts {
                    id
                    name
                    stock
                }
            }
        }
    """)

    # Prepare log entry
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'status': None,
        'products': [],
        'error': None
    }

    try:
        result = client.execute(mutation)
        response = result.get('updateLowStockProducts', {})
        
        if response.get('success'):
            log_entry['status'] = 'success'
            log_entry['message'] = response.get('message', '')
            log_entry['products'] = [
                {'name': p['name'], 'stock': p['stock']} 
                for p in response.get('updatedProducts', [])
            ]
        else:
            log_entry['status'] = 'failed'
            log_entry['message'] = response.get('message', 'Unknown error')

    except Exception as e:
        log_entry['status'] = 'error'
        log_entry['error'] = str(e)

    # Write to log file
    with open("/tmp/low_stock_updates_log.txt", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
