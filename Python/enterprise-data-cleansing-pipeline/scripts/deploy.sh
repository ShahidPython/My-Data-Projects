#!/bin/bash
set -e

ENVIRONMENT=${1:-production}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DEPLOY_LOG="logs/deploy_${TIMESTAMP}.log"

echo "🚀 Starting deployment to ${ENVIRONMENT} environment..."

# Load environment variables
if [ -f ".env.${ENVIRONMENT}" ]; then
    source ".env.${ENVIRONMENT}"
else
    echo "❌ Environment file .env.${ENVIRONMENT} not found"
    exit 1
fi

# Run tests
echo "🧪 Running test suite..."
python -m pytest tests/ -v --tb=short --cov=src --cov-report=html

if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Deployment aborted."
    exit 1
fi

# Build Docker image
echo "🐳 Building Docker image..."
docker build -t data-cleansing-pipeline:${TIMESTAMP} -t data-cleansing-pipeline:latest .

# Push to registry
echo "📤 Pushing to container registry..."
docker tag data-cleansing-pipeline:${TIMESTAMP} ${DOCKER_REGISTRY}/data-cleansing-pipeline:${TIMESTAMP}
docker push ${DOCKER_REGISTRY}/data-cleansing-pipeline:${TIMESTAMP}

# Deploy to Kubernetes/ECS
echo "⚙️  Deploying to ${ENVIRONMENT}..."
if [ "$ENVIRONMENT" = "production" ]; then
    kubectl set image deployment/data-cleansing-pipeline app=${DOCKER_REGISTRY}/data-cleansing-pipeline:${TIMESTAMP}
    kubectl rollout status deployment/data-cleansing-pipeline
else
    aws ecs update-service --cluster data-cleaning-cluster --service data-cleaning-service --force-new-deployment
fi

# Health check
echo "🏥 Performing health check..."
sleep 30
curl -f http://${SERVICE_ENDPOINT}/health || {
    echo "❌ Health check failed"
    exit 1
}

echo "✅ Deployment completed successfully at $(date)"