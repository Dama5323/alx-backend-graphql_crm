import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

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
