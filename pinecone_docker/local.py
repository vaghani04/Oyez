from pinecone.grpc import PineconeGRPC, GRPCClientConfig
from pinecone import ServerlessSpec
import time

# Initialize a client.
# API key is required, but the value does not matter.
# Host and port of the Pinecone Local instance
# is required when starting without indexes. 
pc = PineconeGRPC(
    api_key="pclocal", 
    host="http://localhost:5080" 
)                                    

# Create an index
index_name = "example-index"

if not pc.has_index(index_name):  
    pc.create_index(
        name=index_name,
        dimension=2,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1",
        )
    )

# Wait for the index to be ready
while not pc.describe_index(index_name).status['ready']:
    time.sleep(1)

# Target the index, disabling tls
index_host = pc.describe_index(index_name).host
index = pc.Index(host=index_host, grpc_config=GRPCClientConfig(secure=False))

# Upsert records into the index
index.upsert(
    vectors=[
        {
            "id": "vec1", 
            "values": [1.0, -2.5],
            "metadata": {"genre": "drama"}
        },
        {
            "id": "vec2", 
            "values": [3.0, -2.0],
            "metadata": {"genre": "documentary"}
        },
        {
            "id": "vec3", 
            "values": [0.5, -1.5],
            "metadata": {"genre": "documentary"}
        }
    ],
    namespace="example-namespace"
)

# Check the number of records in the index
print("Index stats:\n", index.describe_index_stats())

# Query the index with a metadata filter
response = index.query(
    vector=[3.0, -2.0],
    filter={"genre": {"$eq": "documentary"}},
    top_k=1,
    include_values=True,
    include_metadata=True,
    namespace='example-namespace'
)

print("\nQuery response:\n", response)

# Delete the index
pc.delete_index(index_name)