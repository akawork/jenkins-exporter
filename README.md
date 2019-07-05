Jenkins Exporter

Jenkins exporter for Prometheus to deploy on FSOFT environment.
This exporter have written in python3.6.

Usage:

1. Download newest version of jenkins_exporter-?.tar
2. Build image:
   
   2.1. Install docker:
      - [Install Docker on macOS](https://runnable.com/docker/install-docker-on-macos)
      - [Install Docker on Windows 10](https://runnable.com/docker/install-docker-on-windows-10)
      - [Install Docker on Linux](https://runnable.com/docker/install-docker-on-linux)

   2.2. Load docker image:
      ```sh
      $ docker load -i jenkins_exporter-?.tar
      ```
3. Run Jenkins Exporter by docker:
   ```sh
   $ docker run -p 9118:9118 -d jenkins_exporter \
     [-s --server <jenkins server url>] \
     [--user <jenkins username>]
     [--passwd <jenkins password>]
     [-p --port <display metrics port>]
   ```

   - docker
      - `-p`: connect docker port to real port
      - `-d`: run as a process
   - jenkins_exporter
      - `-s --server`: targer jenkins server
      - `--user`: username for authentication
      - `--passwd`: password for authentication
      - `p --port`: port to display metrics