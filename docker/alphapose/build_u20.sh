#! /bin/sh

# This script builds openpose image.
# 2 ARGS IN ORDER: {USERNAME}, {PID}

BASE_IMAGE="nvidia/cuda:11.7.1-cudnn8-devel-ubuntu20.04"
IMAGE_NAME="alphapose:cuda11.7.1-cudnn8-devel-ubuntu20.04"
DOCKER_FILE="dockerfiles/Dockerfile.U20"

# BUILD ALPHAPOSE IMAGE --------------------------------------------------------
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
