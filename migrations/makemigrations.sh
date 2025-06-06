#!/usr/bin/env sh
set -eux

echo "Please enter the migration name: "
read USER_MIGRATION_NAME

# go to directory with migrations
MIGRATION_DIR="/code/migrations/versions"
# count current number of migrations
NUM_MIGRATIONS=$(ls -1q $MIGRATION_DIR | wc -l)
# prepare next migration number with leading zeros
NEXT_MIGRATION_NUM=$(printf "%04d" $((NUM_MIGRATIONS + 1)))

# prepare full migration name
MIGRATION_NAME="${NEXT_MIGRATION_NUM}_${USER_MIGRATION_NAME}"

# run Alembic to create migration
alembic revision --autogenerate -m "$MIGRATION_NAME"
