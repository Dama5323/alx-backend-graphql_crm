from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime

@shared_task
def generate_crm_report():
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql/",
        verify=True,
        retries=3
    )

    client = Client(transport=transport, fetch_schema_from_transport=False)

    query = gql("""
        query {
            allCustomers { totalCount }
            allOrders { edges { node { totalAmount } } }
        }
    """)

    try:
        result = client.execute(query)
        customers = result["allCustomers"]["totalCount"]
        orders = result["allOrders"]["edges"]

        order_count = len(orders)
        revenue = sum(float(order["node"]["totalAmount"]) for order in orders)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp} - Report: {customers} customers, {order_count} orders, {revenue} revenue\n"

        with open("/tmp/crm_report_log.txt", "a") as log:
            log.write(log_line)

    except Exception as e:
        with open("/tmp/crm_report_log.txt", "a") as log:
            log.write(f"{datetime.now()} - ERROR: {e}\n")

@shared_task
def generate_crm_report():
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql/",
        verify=True,
        retries=3,
    )

    client = Client(transport=transport, fetch_schema_from_transport=False)

    query = gql("""
        query {
            allCustomers { totalCount }
            allOrders { edges { node { totalAmount } } }
        }
    """)

    try:
        response = client.execute(query)
        customers = response["allCustomers"]["totalCount"]
        orders = response["allOrders"]["edges"]

        order_count = len(orders)
        total_revenue = sum(float(order["node"]["totalAmount"]) for order in orders)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp} - Report: {customers} customers, {order_count} orders, {total_revenue} revenue\n"

        with open("/tmp/crm_report_log.txt", "a") as logfile:
            logfile.write(log_line)

    except Exception as e:
        with open("/tmp/crm_report_log.txt", "a") as logfile:
            logfile.write(f"{datetime.now()} - ERROR: {str(e)}\n")
