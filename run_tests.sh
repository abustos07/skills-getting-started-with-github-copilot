#!/bin/bash
# Test runner script for the Mergington High School API

echo "Running FastAPI tests with pytest..."
echo "======================================="

# Activate virtual environment and run tests
cd /workspaces/skills-getting-started-with-github-copilot
/workspaces/skills-getting-started-with-github-copilot/.venv/bin/python -m pytest tests/ -v --no-cov

echo ""
echo "Test run complete!"