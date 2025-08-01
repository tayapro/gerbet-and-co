source .env

IMAGE_REPO=sti80/gerbet-and-co
IMAGE_TAG=dev

docker build . --build-arg DATABASE_URL=$DATABASE_URL -t $IMAGE_REPO:$IMAGE_TAG