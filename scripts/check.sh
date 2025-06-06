
#!/usr/bin/env sh
set -eux

BLACK_ARGS=". --config ./pyproject.toml"
RUFF_ARGS=". "
MYPY_ARGS=". --exclude containers_data"
CI=false

cd "$(dirname $0)/.."

# Black

echo "* black ."
black $BLACK_ARGS


# Mypy

echo "* mypy"
mypy $MYPY_ARGS


exit 0
