#!/bin/bash
# Run the tests locally using the qgis testing environment docker

xhost +

# One of master_2, master, release
TARGET_VERSION="master_2"
PLUGIN_NAME="qgiscommons"


docker rm -f qgis-testing-environment

# replace latest with master if you wish to test on master, latest is
# latest supported Boundless release

if [[ "$(docker images -q boundlessgeo/qgis-testing-environment:$TARGET_VERSION 2> /dev/null)" == "" ]]; then
    docker pull boundlessgeo/qgis-testing-environment:$TARGET_VERSION
fi

docker tag boundlessgeo/qgis-testing-environment:$TARGET_VERSION qgis-testing-environment


docker run -d  --name qgis-testing-environment  -e DISPLAY=:99 -v /tmp/.X11-unix:/tmp/.X11-unix -v `pwd`:/tests_directory qgis-testing-environment

# Setup
docker exec -it qgis-testing-environment sh -c "qgis_setup.sh $PLUGIN_NAME"
docker exec -it qgis-testing-environment sh -c "ln -s /tests_directory/$PLUGIN_NAME /root/.qgis2/python/plugins/$PLUGIN_NAME"


# run the tests
docker exec -it qgis-testing-environment sh -c "DISPLAY=unix:0 qgis_testrunner.sh ${PLUGIN_NAME}.tests.settings"
