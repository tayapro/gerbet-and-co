source .env

IMAGE_REPO=gerbet-and-co
IMAGE_TAG=dev0

docker build . --build-arg DATABASE_URL=$DATABASE_URL -t $IMAGE_REPO:$IMAGE_TAG