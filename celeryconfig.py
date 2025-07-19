# Celery configuration
import os

# Broker settings
broker_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Result backend
result_backend = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Task settings
task_serializer = 'json'
accept_content = ['json']
result_serializer = 'json'
timezone = 'UTC'
enable_utc = True

# Worker settings
worker_prefetch_multiplier = 1
worker_max_tasks_per_child = 1000

# Task routing
task_routes = {
    'worker.tasks.process_dna_task': {'queue': 'dna_processing'}
}

# Queue settings
task_default_queue = 'default'
task_default_exchange = 'default'
task_default_routing_key = 'default' 