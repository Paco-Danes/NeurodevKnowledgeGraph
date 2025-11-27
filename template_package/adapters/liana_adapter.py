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
        The parquet files are expected to have columns: 'source', 'target', 'species'
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
        required_cols = ['source', 'target', 'species']
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
        If an entry starts with "COMPLEX:" (e.g. "COMPLEX:P04626_P21860") it is treated as a QuaternaryStructure.
        No species in nodes -> species is stored as a property in edges.
        """
        logger.info("Generating Nodes...")

        # Map id -> {"species": species, "label": "Protein"|"QuaternaryStructure"}
        proteins = {}

        for _, row in self.data.iterrows():
            for col in ("source", "target"):
                pid = row[col]

                if pd.isna(pid):
                    continue

                pid_str = str(pid)

                if pid_str.startswith("COMPLEX:") or "_" in pid_str:
                    label = "QuaternaryStructure"
                    pid_str = pid_str.replace("COMPLEX:", "")
                else:
                    label = "Protein"

                if pid_str not in proteins:
                    proteins[pid_str] = {"label": label}

        # Yield nodes
        for protein_id, meta in proteins.items():
            yield (
                protein_id,
                meta["label"],
                {}
            )

        logger.info(f"Generated {len(proteins)} unique protein/complex nodes.")

    def get_edges(self):
        """
        Generator yielding edges.
        Format: (id, source_id, target_id, label, properties)
        
        Each row represents a ligand-receptor interaction.
        """
        logger.info("Generating Edges...")

        for _, row in self.data.iterrows():
            ligand = row["source"]
            receptor = row["target"]
            species = row["species"]

            if ligand.startswith("COMPLEX:") or "_" in ligand:
                ligand = ligand.replace("COMPLEX:", "")
            if receptor.startswith("COMPLEX:") or "_" in receptor:
                receptor = receptor.replace("COMPLEX:", "")
            
            # Create a unique ID for the interaction
            interaction_id = f"{ligand}-{receptor}-{species}"

            # Additional properties beyond species can be added here
            properties = {"species": species}

            yield (
                interaction_id, # testing
                ligand,      # Source (ligand)
                receptor,    # Target (receptor)
                "LigandReceptorInteraction",
                properties
            )
        
        logger.info(f"Generated {len(self.data)} interaction edges.")

