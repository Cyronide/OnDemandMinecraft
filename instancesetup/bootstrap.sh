#!/bin/bash

launcher_meta_url="https://launchermeta.mojang.com/mc/game/version_manifest.json"
app_dir="/home/ubuntu/OnDemandMinecraft"

apt-get update
apt-get -y install jq
apt-get -y install openjdk-11-jdk-headless

latest_release_url=$(curl -LSsf "$launcher_meta_url" | jq -r '.latest.release')
latest_manifest_url=$(curl -LSsf "$launcher_meta_url" | jq --arg LATEST_RELEASE_URL "$latest_release_url" --raw-output '[.versions[]|select(.id == $LATEST_RELEASE_URL)][0].url')
latest_jar_url=$(curl -LSsf "$latest_manifest_url" | jq --raw-output '.downloads.server.url')

mkdir "$app_dir"
cp /tmp/OnDemandMinecraft/instancesetup/* "$app_dir"

curl -LSsf -o ./server.jar $latest_jar_url

mkdir /home/ubuntu/screens
chmod 700 /home/ubuntu
export SCREENDIR=/home/ubuntu/screens
crontab "${app_dir}/crontab"

chown -R ubuntu:ubuntu "$app_dir"
rm -rf /tmp/OnDemandMinecraft