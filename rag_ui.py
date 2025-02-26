import streamlit as st
import asyncio
import time
from rag.llm_processor import LLMProcessor
from milvus_local.llm_processor import MilvusLocalLLMProcessor
import logging
import os

logging.getLogger("streamlit.watcher.local_sources_watcher").setLevel(logging.ERROR)
logging.getLogger("streamlit.web.bootstrap").setLevel(logging.ERROR)
logging.getLogger("grpc").setLevel(logging.ERROR)

os.environ["TOKENIZERS_PARALLELISM"] = "false"

async def fetch_pinecone_response(query):
    processor = LLMProcessor()
    start_time = time.time()
    result = await processor.process_query(query)
    elapsed_time = time.time() - start_time
    return result["response"], elapsed_time

async def fetch_milvus_response(query):
    processor = MilvusLocalLLMProcessor()
    start_time = time.time()
    result = await processor.process_query(query)
    elapsed_time = time.time() - start_time
    return result["response"], elapsed_time

async def process_dual_queries(query):
    pinecone_task = asyncio.create_task(fetch_pinecone_response(query))
    milvus_task = asyncio.create_task(fetch_milvus_response(query))
    pinecone_response, pinecone_time = await pinecone_task
    milvus_response, milvus_time = await milvus_task
    return {
        "pinecone": {"response": pinecone_response, "time": pinecone_time},
        "milvus": {"response": milvus_response, "time": milvus_time}
    }

def render_ui():
    st.title("Oyez RAG Explorer")
    query = st.text_input("Enter your query about Supreme Court cases:", key="query_input")

    if st.button("Get Response", key="get_response"):
        with st.spinner("Fetching responses..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(process_dual_queries(query))
                loop.close()

                col1, col2 = st.columns(2)

                with col1:
                    st.subheader(f"Pinecone Cloud Response (Time: {results['pinecone']['time']:.2f}s)")
                    st.markdown(results["pinecone"]["response"])

                with col2:
                    st.subheader(f"Milvus Local Response (Time: {results['milvus']['time']:.2f}s)")
                    st.markdown(results["milvus"]["response"])

            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    render_ui()