#!/bin/bash

# Get script directory using BASH_SOURCE
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cwd=$(pwd)

# Navigate to project root from script dir
cd "$SCRIPT_DIR/../.." || exit
PROJECT_CWD=$(pwd)

# Log file location
LOG_FILE="/tmp/customer_cleanup_log.txt"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Check if we are in correct directory
if [ -f "manage.py" ]; then
    DELETED_COUNT=$(python3 manage.py shell -c "
from datetime import timedelta
from django.utils import timezone
from crm.models import Customer, Order

one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.exclude(id__in=Order.objects.filter(created_at__gte=one_year_ago).values_list('customer_id', flat=True))
count = inactive_customers.count()
inactive_customers.delete()
print(count)
")
else
    echo "[$TIMESTAMP] Error: manage.py not found in $PROJECT_CWD" >> "$LOG_FILE"
    exit 1
fi

# Write cleanup result to log
echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers from cwd: $cwd" >> "$LOG_FILE"
