docker build -t arahmanhamdy/img-process .
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
docker push arahmanhamdy/img-process
zappa deploy $1 2>/dev/null || zappa update $1

