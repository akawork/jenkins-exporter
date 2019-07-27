## Jenkins Exporter

Jenkins exporter for Prometheus to deploy on FSOFT environment.
This exporter has written in python3.6.

## Usage:

### Step 1: Build image

```sh
docker build -t jenkins_exporter -f Dockerfile
```

### Step 2: Running Jenkins exporter

```sh
docker run -p 9118:9118 --name jenkins_exporter -d \
-e "JENKINS_SERVER=http://192.168.232.147:8080" \
-e "JENKINS_USERNAME=admin" \
-e "JENKINS_PASSWORD=123456" jenkins_exporter
```

With:

- JENKINS_SERVER: is the url of Jenkins
- JENKINS_USERNAME: is the user of Jenkins who have permission to access Jenkins resource
- JENKINS_PASSWORD: is the password of user.