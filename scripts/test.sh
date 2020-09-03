set -e

echo "Formatting code..."
black . --line-length 79 --check

echo "Checking flake8 compliance..."
flake8

echo "Evaluating code security..."
bandit . -r -lll

# Add unit tests...

echo "That's some well-formatted, safe looking, clean code you got there!"
