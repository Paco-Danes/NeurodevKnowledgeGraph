#!/bin/bash -c
cd /usr/app/
cp -r /src/* .
cp config/biocypher_docker_config.yaml config/biocypher_config.yaml
poetry install
python3 create_knowledge_graph.py
chmod -R 777 biocypher-log#!/bin/bash
set -e  # Exit immediately if any command fails

echo "--- [BUILD] Starting Build Script ---"

# 1. Move to the application directory
cd /usr/app/ || exit

# 2. Copy source files
# We use a loop or specific glob settings to ensure hidden files are handled if needed,
# but to keep your exact logic, we stick to standard copy.
echo "--- [BUILD] Copying source files from /src/ ---"
cp -r /src/* .

# 3. Configure BioCypher
echo "--- [BUILD] Configuring BioCypher ---"
if [ -f "config/biocypher_docker_config.yaml" ]; then
    cp config/biocypher_docker_config.yaml config/biocypher_config.yaml
    echo "--- [BUILD] Config copied successfully ---"
else
    echo "--- [BUILD] ERROR: config/biocypher_docker_config.yaml not found! ---"
    exit 1
fi

# 4. Install Dependencies
echo "--- [BUILD] Installing Poetry dependencies ---"
poetry install

# 5. Run the Knowledge Graph Creator
echo "--- [BUILD] Running create_knowledge_graph.py ---"
if [ -f "create_knowledge_graph.py" ]; then
    python3 create_knowledge_graph.py
else
    echo "--- [BUILD] ERROR: create_knowledge_graph.py script missing! ---"
    exit 1
fi

# 6. Set Permissions
# We check if the folder exists first to avoid a crash if the python script failed to make it
if [ -d "biocypher-log" ]; then
    echo "--- [BUILD] Setting permissions on biocypher-log ---"
    chmod -R 777 biocypher-log
else
    echo "--- [BUILD] WARNING: biocypher-log directory was not created. Skipping chmod. ---"
fi

echo "--- [BUILD] Script Finished Successfully ---"