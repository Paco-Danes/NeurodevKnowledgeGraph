import biocypher
from template_package.adapters.liana_adapter import LianaAdapter
from biocypher._logger import logger 

# 1. Define file paths
human_path = "template_package/data/liana_humanconsensus_db.parquet"
mouse_path = "template_package/data/liana_mouseconsensus_db.parquet"

# 2. Instantiate Adapter
adapter = LianaAdapter(human_path, mouse_path)

# 3. Instantiate BioCypher Driver
# This reads the schema_config.yaml and biocypher_config.yaml automatically
driver = biocypher.BioCypher()

# 4. Run the driver with the adapter generators
driver.write_nodes(adapter.get_nodes())
driver.write_edges(adapter.get_edges())
driver.write_import_call()

# 5. Output Summary
logger.info(
    "Import complete. Check the 'biocypher-out' directory for CSVs and import scripts."
)