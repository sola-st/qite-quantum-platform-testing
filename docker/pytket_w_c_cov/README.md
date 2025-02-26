## Build the Docker

```bash
docker build --build-arg UID=$(id -u) --build-arg GID=$(id -g) -t pytket_w_c .
```

## Run the Docker

```bash
docker run -it --rm \
    -v $(pwd)/container_accessible_folder:/home/regularuser/host \
    -v $(pwd)/pytket_w_c /bin/bash:/home/regularuser/tket/base_qc_w_opt.py \
    pytket_w_c /bin/bash

# inside the container
source /home/regularuser/tket/.venv/bin/activate
python /home/regularuser/tket/base_qc_w_opt.py


```

