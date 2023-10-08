#! /bin/bash

set -e

pytest --cov=alexa_red_alert \
  --cov-branch \
  --cov-report=html:test-reports/coverage tests

coverage json -o test-reports/pytest-coverage.json
