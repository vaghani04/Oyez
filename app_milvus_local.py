from milvus_local.upsert import MilvusLocalUpserter

def run():
    upserter = MilvusLocalUpserter()
    upserter.run()

if __name__ == "__main__":
    run()