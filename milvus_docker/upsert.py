import numpy as np
from pymilvus import MilvusClient, CollectionSchema, FieldSchema, DataType
# , db
from milvus_docker.settings import DockerSettings
from rag.utils.embedding_utils import EmbeddingUtils
import os

class MilvusDockerUpserter:
    def __init__(self):
        self.settings = DockerSettings()
        # self.client = MilvusClient(host=self.settings.MILVUS_HOST, port=self.settings.MILVUS_PORT)
        self.client = MilvusClient(uri=self.settings.MILVUS_URI)
        self.embedding_utils = EmbeddingUtils(self.settings.MODEL_NAME)
        # if self.settings.MILVUS_DB not in db.list_database():
        #     database = db.create_database(self.settings.MILVUS_DB)

    def load_embeddings(self):
        embeddings_path = os.path.join(self.settings.EMBEDDINGS_DIR, self.settings.EMBEDDINGS_FILE)
        metadata_path = os.path.join(self.settings.EMBEDDINGS_DIR, self.settings.METADATA_FILE)
        try:
            embeddings = np.load(embeddings_path)
            metadata = np.load(metadata_path, allow_pickle=True)
            return embeddings, metadata
        except Exception as e:
            print(f"Failed to load embeddings or metadata: {e}")
            return None, None

    def normalize_vectors(self, vectors):
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        normalized_vectors = vectors / norms
        return normalized_vectors

    def upsert(self):
        embeddings, metadata = self.load_embeddings()
        if embeddings is None or metadata is None:
            print("No embeddings to upsert")
            return
        
        valid_indices = [i for i, emb in enumerate(embeddings) if not np.all(emb == 0)]
        if not valid_indices:
            print("No valid embeddings to upsert")
            return
        embeddings = embeddings[valid_indices].astype('float32')
        metadata = metadata[valid_indices]

        embeddings = self.normalize_vectors(embeddings)

        index_params = self.client.prepare_index_params()
        index_params.add_index(
                field_name="vector",
                index_type="IVF_FLAT",
                metric_type="COSINE"
            )

        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=100, is_primary=True),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=self.settings.DIMENSION),
            FieldSchema(name="case_dir", dtype=DataType.VARCHAR, max_length=255)
        ]
        schema = CollectionSchema(fields=fields, description="Oyez Cases Docker")
        self.client.drop_collection(self.settings.COLLECTION_NAME)
        self.client.create_collection(
            collection_name=self.settings.COLLECTION_NAME,
            schema=schema,
            index_params=index_params
        )

        # index_params = {
        #         "index_type": "IVF_FLAT", 
        #         "metric_type": "IP", 
        #         "params": {"nlist": 100},
        #         "field_name": "vector"
        #     }
        # self.client.create_index(
        #     collection_name=self.settings.COLLECTION_NAME,
        #     # field_name="vector",
        #     index_params=index_params
        # )

        # data = []
        # for i, (emb, meta) in enumerate(zip(embeddings, metadata)):
        #     data.append({
        #         "id": str(meta["case_id"]),
        #         "vector": emb.tolist(),
        #         "case_dir": meta["case_dir"]
        #     })
        for i, (emb, meta) in enumerate(zip(embeddings, metadata)):
            data ={
                "id": str(meta["case_id"]),
                "vector": emb.tolist(),
                "case_dir": meta["case_dir"]
            }
            print(data)
            self.client.insert(
                collection_name=self.settings.COLLECTION_NAME,
                data=data
            )
            print("Inserted Sucessfully for ", meta["case_id"])
        print(f"Upsert result: {self.client.get_collection_stats(self.settings.COLLECTION_NAME)}")

    def run(self):
        self.upsert()