import pandas as pd
import biocypher
from biocypher._logger import logger

class LianaAdapter:
    def __init__(self, human_file, mouse_file):
        self.human_file = human_file
        self.mouse_file = mouse_file
        self.data = self._load_data()

    def _load_data(self):
        """
        Loads and merges the mouse and human parquet files.
        The parquet files are expected to have columns: 'ligand', 'receptor', 'species'
        """
        logger.info("Loading Parquet files...")

        try:
            df_human = pd.read_parquet(self.human_file)
            if "species" not in df_human.columns:
                df_human["species"] = "human"
        except FileNotFoundError:
            logger.warning(f"File {self.human_file} not found. Skipping.")
            df_human = pd.DataFrame()

        try:
            df_mouse = pd.read_parquet(self.mouse_file)
            if "species" not in df_mouse.columns:
                df_mouse["species"] = "mouse"
        except FileNotFoundError:
            logger.warning(f"File {self.mouse_file} not found. Skipping.")
            df_mouse = pd.DataFrame()

        # Combine datasets
        full_df = pd.concat([df_human, df_mouse], ignore_index=True)

        # Validate required columns exist
        required_cols = ['ligand', 'receptor', 'species']
        missing_cols = [col for col in required_cols if col not in full_df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}. Found columns: {full_df.columns.tolist()}")

        logger.info(f"Loaded {len(full_df)} interactions from {full_df['species'].nunique()} species.")
        logger.info(f"Species distribution: {full_df['species'].value_counts().to_dict()}")
        
        return full_df

    def get_nodes(self):
        """
        Generator yielding nodes.
        Format: (id, label, properties)
        
        Each unique protein (from ligand or receptor columns) becomes a node.
        If an entry contains an underscore (e.g. "EGFR_ERBB2") it is treated as a Complex.
        """
        logger.info("Generating Nodes...")

        # Map id -> {"species": species, "label": "Protein"|"MacromolecularComplex"}
        proteins = {}

        for _, row in self.data.iterrows():
            for col in ("ligand", "receptor"):
                pid = row[col]
                species = row["species"]

                if pd.isna(pid):
                    continue

                pid_str = str(pid)
                label = "MacromolecularComplex" if "_" in pid_str else "Protein"

                if pid_str not in proteins:
                    proteins[pid_str] = {"species": species, "label": label}
                # keep first-seen species; log if different
                elif proteins[pid_str]["species"] != species:
                    logger.debug(
                        f"Species mismatch for {pid_str}: keeping {proteins[pid_str]['species']} "
                        f"over new {species}"
                    )

        # Yield nodes
        for protein_id, meta in proteins.items():
            yield (
                protein_id,
                meta["label"],
                {"species": meta["species"]}
            )

        logger.info(f"Generated {len(proteins)} unique protein/complex nodes.")

    def get_edges(self):
        """
        Generator yielding edges.
        Format: (id, source_id, target_id, label, properties)
        
        Each row represents a ligand-receptor interaction.
        """
        logger.info("Generating Edges...")

        for idx, row in self.data.iterrows():
            ligand = row["ligand"]
            receptor = row["receptor"]
            species = row["species"]
            
            # Create a unique ID for the interaction
            interaction_id = f"{ligand}_{receptor}_{species}_{idx}"

            # Additional properties beyond species can be added here
            properties = {"species": species}
            
            # Add any other columns from the dataframe as properties
            for col in self.data.columns:
                if col not in ["ligand", "receptor", "species"]:
                    properties[col] = row[col]

            yield (
                interaction_id,
                ligand,      # Source (ligand)
                receptor,    # Target (receptor)
                "LigandReceptorInteraction",
                properties
            )
        
        logger.info(f"Generated {len(self.data)} interaction edges.")


def main():
    # 1. Define file paths
    human_path = "liana_humanconsensus_db.parquet"
    mouse_path = "liana_mouseconsensus_db.parquet"

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


if __name__ == "__main__":
    main()
