#!/bin/bash
if [ $1 == "--dev" ]; then
    echo "Staring development environment..."
    echo "Revoming containers, if exist..."
    docker-compose down --volumes
    echo "Building new development container..."
    docker-compose up --build --remove-orphans --force-recreate
fi
if [ $1 == "--prod" ]; then
    echo "Deploying to Production environment..."
    
    echo "Removing containers, if exist..."
    docker-compose -f docker-compose-prod.yml down --volumes
    echo "Building new production container..."
    docker-compose -f docker-compose-prod.yml up -d --build --remove-orphans --force-recreate
fi