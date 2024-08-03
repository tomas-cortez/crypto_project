#!/bin/bash

set -e
set -u

# Check if database exists
if psql -lqt | cut -d \| -f 1 | grep -qw "$POSTGRES_DB"; then
    echo "Database '$POSTGRES_DB' already exists."
else
    echo "Creating database '$POSTGRES_DB'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        CREATE DATABASE "$POSTGRES_DB" WITH OWNER "$POSTGRES_USER" ENCODING 'UTF8';
EOSQL
fi

# Check if user exists before creation. 
if ! psql -c "\du" postgres | grep -q "$POSTGRES_USER"; then
    echo "Creating user '$POSTGRES_USER'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        CREATE USER "$POSTGRES_USER" WITH PASSWORD '$POSTGRES_PASSWORD';
EOSQL
fi

if ! psql -c "\du" postgres | grep -q "$READONLY_USER"; then
    echo "Creating user '$READONLY_USER'"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        CREATE USER "$READONLY_USER" WITH PASSWORD '$READONLY_PASSWORD';
EOSQL
fi

# Granting privileges to the new users
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    GRANT ALL PRIVILEGES ON DATABASE "$POSTGRES_DB" TO "$POSTGRES_USER";
    -- Grant SELECT on specific tables to the READONLY_USER (example):
    -- GRANT SELECT ON coin_data TO "$READONLY_USER"; 
    -- GRANT SELECT ON coin_month_data TO "$READONLY_USER"; 
EOSQL

# Creating the table structure
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE TABLE IF NOT EXISTS coin_data (
        coin VARCHAR NOT NULL,
        date DATE NOT NULL,
        price FLOAT,
        json JSON,
        PRIMARY KEY (coin, date)
    );
    
    CREATE TABLE IF NOT EXISTS coin_month_data (
        coin VARCHAR NOT NULL,
        year INTEGER NOT NULL,
        month INTEGER NOT NULL,
        min_price FLOAT,
        max_price FLOAT,
        PRIMARY KEY (coin, year, month)
    );
EOSQL