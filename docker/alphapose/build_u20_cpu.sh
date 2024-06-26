#! /bin/sh

# This script builds openpose image.
# 2 ARGS IN ORDER: {USERNAME}, {PID}

BASE_IMAGE="ubuntu:20.04"
IMAGE_NAME="alphapose:ubuntu20.04"
DOCKER_FILE="dockerfiles/Dockerfile.U20CPU"

# BUILD OPENPOSE IMAGE ---------------------------------------------------------
echo "Building image : ${IMAGE_NAME}"
DOCKER_BUILDKIT=1 docker build \
    --file ${DOCKER_FILE} \
    --build-arg BASE_IMAGE=${BASE_IMAGE} \
    --tag "${IMAGE_NAME}" \
    .
echo "Built image : ${IMAGE_NAME}\n"

# ADD USER ---------------------------------------------------------------------
if [ $# -gt 0 ]; then
    mkdir tmp
    P=$(pwd)
    cp -rf ../_user tmp
    cd tmp/_user
    echo "adding user..."
    sh build.sh $1 $2 ${IMAGE_NAME}
    echo "added user...\n"
    cd $P
    rm -rf tmp
fi
