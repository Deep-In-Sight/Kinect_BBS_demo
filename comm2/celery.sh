#!/bin/bash
celery -A server.celery_app worker --loglevel=info
