import streamlit as st
import asyncio
from rag.llm_processor import LLMProcessor
import logging

logging.getLogger("streamlit.watcher.local_sources_watcher").setLevel(logging.ERROR)
logging.getLogger("streamlit.web.bootstrap").setLevel(logging.ERROR)

async def process_query(query):
    processor = LLMProcessor()
    return await processor.process_query(query)

st.title("Oyez RAG Explorer")
query = st.text_input("Enter your query about Supreme Court cases:")

if st.button("Get Response"):
    try:
        result = asyncio.run(process_query(query))
        st.write("Response:", result["response"])
    except Exception as e:
        st.error(f"An error occurred: {e}")