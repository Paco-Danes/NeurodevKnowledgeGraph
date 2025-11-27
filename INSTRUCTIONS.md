### REQUIREMENTS
- 💻 OS: linux-based (prefered)
- 🐳 Docker: `docker --version` should not give errors.
- 📦 Poetry: in ubuntu i just did `sudo apt install python3-poetry`
- 🐍 Python + `pip install biocypher`: if you want local testings before running the dockers

### DOCKER
- Run the pipeline. This will pull images (first time), create containers 'build', 'import', 'deploy' + a volume and run them sequentially. Only 'deploy' remains up and running.
    ```bash
    docker compose up -d
    ```
- To show logs do one of:
    ```bash
    docker logs build
    docker logs import
    docker logs deploy
    ```
- To kill all containers, do one of:
    ```bash
    docker compose down # simply stops 'deploy'
    docker compose down -v # also remove/reset volumes
    ```
    remove the volumes when you modified the adapters and will have different data in output, just to be sure nothing old remains.
- If needed, check for running and stopped containers or images
    ```bash
    docker ps -a # visualize all containers
    docker images # visualize all images
    ```
- If 'deploy' is running, neo4j is serving at http://localhost:7474/browser/

### Dependencies
- If you are using a new python package, add to poetry and rerun the docker pipeline:
    ```bash
    poetry add <package_name> # e.g 'poetry add pyarrow' for reading parquet files with pandas
    poetry install # updates lock/toml files
    ```
### Biocypher documentation
Click here to [go to Quickstart page](https://biocypher.org/BioCypher/learn/quickstart/)