#!/usr/bin/env bash
set -eu

: "${COSIGN_PRIVATE_KEY:?COSIGN_PRIVATE_KEY is required}"
: "${COSIGN_PUBLIC_KEY:?COSIGN_PUBLIC_KEY is required}"
: "${COSIGN_PASSWORD:?COSIGN_PASSWORD is required}"

apk upgrade --no-cache
apk add --update curl skopeo

cosign_version="3.1.2"
cosign_sha256="f7622ed3cf22e55e1ae6377c080979ff77a22da9981c11df222a2e444991e7cf"
curl -fSL "https://github.com/sigstore/cosign/releases/download/v${cosign_version}/cosign-linux-amd64" -o /tmp/cosign
echo "${cosign_sha256}  /tmp/cosign" | sha256sum -c -
chmod 0755 /tmp/cosign
mv /tmp/cosign /usr/local/bin/cosign

# Deploy to Docker Hub
skopeo copy --all docker://$CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG docker://docker.io/psono/psono-fileserver:latest

export docker_version_tag=$(echo $CI_COMMIT_TAG | awk  '{ string=substr($0, 2, 100); print string; }' )
skopeo copy --all docker://$CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG docker://docker.io/psono/psono-fileserver:$docker_version_tag

release_image="docker.io/psono/psono-fileserver"
latest_digest="$(skopeo inspect --format '{{.Digest}}' "docker://${release_image}:latest")"
version_digest="$(skopeo inspect --format '{{.Digest}}' "docker://${release_image}:${docker_version_tag}")"

if [ "${latest_digest}" != "${version_digest}" ]; then
    echo "Docker Hub tags have different digests: latest=${latest_digest}, ${docker_version_tag}=${version_digest}" >&2
    exit 1
fi

cosign sign --yes --tlog-upload=false --key env://COSIGN_PRIVATE_KEY "${release_image}@${version_digest}"

# Transparency-log verification is intentionally disabled together with Rekor uploads.
cosign verify --insecure-ignore-tlog --key env://COSIGN_PUBLIC_KEY "${release_image}@${version_digest}"

# Deploy to GitHub
echo "Clonging gitlab.com/psono/psono-fileserver.git"
git clone https://gitlab.com/psono/psono-fileserver.git
cd psono-fileserver
git branch --track develop origin/develop
git fetch --all
git pull --all

echo "Empty .ssh folder"
if [ -d "/root/.ssh" ]; then
    rm -Rf /root/.ssh;
fi
mkdir -p /root/.ssh

echo "Fill .ssh folder"
echo "$github_deploy_key" > /root/.ssh/id_rsa
cat > /root/.ssh/known_hosts <<- "EOF"
|1|AuV+6vt2c6yHKSBI3cGlgiQgBw0=|oReK12ycO4x62cIfNqNIvclb2Ao= ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEmKSENjQEezOmxkZMy7opKgwFB9nkt5YRrYMjNuG5N87uRgg6CLrbo5wAdT/y6v0mKV0U2w0WZ2YB/++Tpockg=
|1|rLMxkb3I+R6GmInBad4kitV0ZTk=|c7GxoZTzebOPBENzRmPEylRcgtY= ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEmKSENjQEezOmxkZMy7opKgwFB9nkt5YRrYMjNuG5N87uRgg6CLrbo5wAdT/y6v0mKV0U2w0WZ2YB/++Tpockg=
EOF
chmod 600 /root/.ssh/id_rsa
chmod 600 /root/.ssh/known_hosts

echo "Push to github.com/psono/psono-fileserver.git"
git remote set-url origin git@github.com:psono/psono-fileserver.git
git push --all origin
