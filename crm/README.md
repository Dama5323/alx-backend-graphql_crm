# CRM Celery Report Generator

## Setup Instructions

### 1. Install Redis and Python Dependencies

```bash
# Install Redis (Ubuntu/Debian)
sudo apt update
sudo apt install redis-server

# Or use Docker
docker run -d -p 6379:6379 redis

# Install project requirements
pip install -r requirements.txt
```

---
### Migrate Database
```
python manage.py migrate
```
---
### Start Celery Worker
```
celery -A crm worker -l info
```
---

### Start Celery Beat Scheduler
```
celery -A crm beat -l info
```

---
###  Check Weekly Report Log
CRM reports will be logged here every Monday at 6:00 AM:
```
cat /tmp/crm_report_log.txt
```
Each log entry is timestamped in the format:

```
YYYY-MM-DD HH:MM:SS - Report: X customers, Y orders, Z revenue
```

---

### Test the Report Task Manually (Optional)

### Run in shell to verify:
You can test the task by running it manually in a Django shell:

```bash
python manage.py shell
>>> from crm.tasks import generate_crm_report
>>> generate_crm_report.delay()
```

then view the log:
```
cat /tmp/crm_report_log.txt
```
---

