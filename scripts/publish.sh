set -e

echo "Publishing..."
REGISTRY_URL="111373087273.dkr.ecr.us-east-1.amazonaws.com/api.zacharyjklein.com"
TAG="stable"
eval $(aws ecr get-login --no-include-email)
docker build -t api .
docker tag api $REGISTRY_URL:$TAG
docker push $REGISTRY_URL:$TAG
