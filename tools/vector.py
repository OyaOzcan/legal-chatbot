import streamlit as st
from tools.llm import llm, embeddings
from app.infrastructure.graph import graph
from langchain_neo4j import Neo4jVector
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

neo4jvector = Neo4jVector.from_existing_index(
    embeddings,
    graph=graph,
    index_name="cuadVectorIndex",            
    node_label="ContractChunk",              
    text_node_property="text",               
    embedding_node_property="embedding",     
    retrieval_query="""
RETURN
    node.text AS text,
    score,
    {
        source: node.source
    } AS metadata
"""
)

retriever = neo4jvector.as_retriever()

instructions = (
    "Use the given context to answer the legal question."
    "If you don't know the answer, say you don't know."
    "Context: {context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", instructions),
    ("human", "{input}"),
])

question_answer_chain = create_stuff_documents_chain(llm, prompt)

clause_retriever = create_retrieval_chain(
    retriever,
    question_answer_chain
)

def get_clause_similarity(input):
    return clause_retriever.invoke({"input": input})



