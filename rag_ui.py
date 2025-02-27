import streamlit as st
import asyncio
import time
import os
import logging
from rag.llm_processor import LLMProcessor
from milvus_local.llm_processor import MilvusLocalLLMProcessor
from milvus_docker.llm_processor import MilvusDockerLLMProcessor 
from pinecone_docker.llm_processor import PineconeDockerLLMProcessor

logging.basicConfig(level=logging.ERROR)
logging.getLogger("grpc").setLevel(logging.ERROR)
logging.getLogger("grpc").setLevel(logging.CRITICAL)
logging.getLogger("streamlit.watcher.local_sources_watcher").setLevel(logging.ERROR)
logging.getLogger("streamlit.web.bootstrap").setLevel(logging.ERROR)

os.environ["TOKENIZERS_PARALLELISM"] = "false"

async def fetch_pinecone_response(query):
    processor = LLMProcessor()
    start_time = time.time()
    result = await processor.process_query(query)
    elapsed_time = time.time() - start_time
    return result["response"], elapsed_time, result.get("scores", [])

async def fetch_milvus_local_response(query):
    processor = MilvusLocalLLMProcessor()
    start_time = time.time()
    result = await processor.process_query(query)
    elapsed_time = time.time() - start_time
    return result["response"], elapsed_time, result.get("scores", [])

async def fetch_milvus_docker_response(query):
    processor = MilvusDockerLLMProcessor()
    start_time = time.time()
    result = await processor.process_query(query)
    elapsed_time = time.time() - start_time
    return result["response"], elapsed_time, result.get("scores", [])

async def fetch_pinecone_docker_response(query):
    processor = PineconeDockerLLMProcessor()
    start_time = time.time()
    result = await processor.process_query(query)
    elapsed_time = time.time() - start_time
    return result["response"], elapsed_time, result.get("scores", [])


async def process_all_queries(query):
    pinecone_task = asyncio.create_task(fetch_pinecone_response(query))
    milvus_local_task = asyncio.create_task(fetch_milvus_local_response(query))
    milvus_docker_task = asyncio.create_task(fetch_milvus_docker_response(query))  # <HIGHLIGHT: Added Milvus Docker task>
    pinecone_docker_task = asyncio.create_task(fetch_pinecone_docker_response(query))  # <HIGHLIGHT: Added Milvus Docker task>
    
    pinecone_response, pinecone_time, pinecone_scores = await pinecone_task
    milvus_local_response, milvus_local_time, milvus_local_scores = await milvus_local_task
    pinecone_docker_response, pinecone_docker_time, pinecone_docker_scores = await pinecone_docker_task  # <HIGHLIGHT: Added unpacking>
    milvus_docker_response, milvus_docker_time, milvus_docker_scores = await milvus_docker_task  # <HIGHLIGHT: Added unpacking>
    return {
        "pinecone": {"response": pinecone_response, "time": pinecone_time, "scores": pinecone_scores},
        "milvus_local": {"response": milvus_local_response, "time": milvus_local_time, "scores": milvus_local_scores},
        "pinecone_docker": {"response": pinecone_docker_response, "time": pinecone_docker_time, "scores": pinecone_docker_scores},
        "milvus_docker": {"response": milvus_docker_response, "time": milvus_docker_time, "scores": milvus_docker_scores}
    }

def render_ui():
    st.title("Oyez RAG Explorer")
    st.markdown("Compare responses from Pinecone Cloud, Milvus Local, and Milvus Docker with ease!")

    query = st.text_input("Enter your query about Supreme Court cases:", key="query_input", placeholder="e.g., What are the key points about tax disputes?")

    if st.button("Get Response", key="get_response", type="primary"):
        with st.spinner("Fetching responses from all databases..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(process_all_queries(query))
                loop.close()

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.subheader(f"Pinecone Cloud (Time: {results['pinecone']['time']:.2f}s)")
                    with st.expander("Details", expanded=True):
                        st.markdown(results["pinecone"]["response"])
                        if results["pinecone"]["scores"]:
                            st.markdown("**Relevance Scores:**")
                            for score in results["pinecone"]["scores"]:
                                st.markdown(f"- Case {score['id']}: {score['score']:.4f}")

                with col2:
                    st.subheader(f"Milvus Local (Time: {results['milvus_local']['time']:.2f}s)")
                    with st.expander("Details", expanded=True):
                        st.markdown(results["milvus_local"]["response"])
                        if results["milvus_local"]["scores"]:
                            st.markdown("**Relevance Scores:**")
                            for score in results["milvus_local"]["scores"]:
                                st.markdown(f"- Case {score['id']}: {score['score']:.4f}")

                with col3:
                    st.subheader(f"Milvus Docker (Time: {results['milvus_docker']['time']:.2f}s)")
                    with st.expander("Details", expanded=True):
                        st.markdown(results["milvus_docker"]["response"])
                        if results["milvus_docker"]["scores"]:
                            st.markdown("**Relevance Scores:**")
                            for score in results["milvus_docker"]["scores"]:
                                st.markdown(f"- Case {score['id']}: {score['score']:.4f}")
                
                with col4:
                    st.subheader(f"Pinecone Docker (Time: {results['pinecone_docker']['time']:.2f}s)")
                    with st.expander("Details", expanded=True):
                        st.markdown(results["pinecone_docker"]["response"])
                        if results["pinecone_docker"]["scores"]:
                            st.markdown("**Relevance Scores:**")
                            for score in results["pinecone_docker"]["scores"]:
                                st.markdown(f"- Case {score['id']}: {score['score']:.4f}")
            except Exception as e:
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    render_ui()