import os
from dotenv import load_dotenv
load_dotenv()

from openai import OpenAI
from langchain_neo4j import Neo4jGraph

# 1. Initialize OpenAI LLM for embeddings
llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

response = llm.embeddings.create(
    input="What are the confidentiality obligations between the parties?",
    model="text-embedding-ada-002"
)

embedding = response.data[0].embedding

# 2. Connect to Neo4j
graph = Neo4jGraph(
    url=os.getenv('NEO4J_URI'),
    username=os.getenv('NEO4J_USERNAME'),
    password=os.getenv('NEO4J_PASSWORD')
)

# 3. Run vector similarity query on your clauseIndex
result = graph.query("""
CALL db.index.vector.queryNodes('clauseIndex', 5, $embedding)
YIELD node, score
RETURN node.text AS clause_text, score, node.title AS title, node.type AS type
ORDER BY score DESC
""", {"embedding": embedding})

# 4. Display results
print("🔍 Most similar legal clauses:\n")
for row in result:
    print(f"Clause Title: {row['title']} ({row['type']})")
    print(f"Text: {row['clause_text']}")
    print(f"Similarity Score: {row['score']:.4f}")
    print("---------------")
