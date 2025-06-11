from langchain_neo4j import GraphCypherQAChain
from langchain.prompts.prompt import PromptTemplate

from llm import llm
from graph import graph


schema_str = """
(:Agreement {name: STRING, type: STRING, date: STRING, effective_date: STRING, expiration_date: STRING, renewal_term: STRING, notice_period: STRING, source_file: STRING})
(:Clause {text: STRING, clause_type: STRING})
(:ClauseType {name: STRING})
(:Party {name: STRING})
(:GoverningLaw {name: STRING})

(:Agreement)-[:HAS_CLAUSE]->(:Clause)
(:Clause)-[:OF_TYPE]->(:ClauseType)
(:Clause)-[:MENTIONS]->(:Party)
(:Clause)-[:UNDER_LAW]->(:GoverningLaw)
"""

CYPHER_GENERATION_TEMPLATE = """
You are a senior Neo4j Cypher expert. Your task is to convert the user's legal-related question into a syntactically correct Cypher query.

You must follow these rules strictly:

- Only return valid Cypher syntax. Do NOT include explanations, comments, or natural language.
- Do NOT include quotation marks around the entire query.
- Use only the relationship types, node labels, and properties mentioned in the schema.
- If no relevant clause exists, return a Cypher query that returns an empty result (e.g., `RETURN []`).
- Always use `toLower()` and `CONTAINS` when filtering by clause type or text if uncertain.

- Do not use relationship types that are not defined, like CONTAINS.
- Use `HAS_CLAUSE` to link `Agreement` and `Clause`.
- Clause nodes do not have a "name" property. Use "clause_type" or "text" instead.

--- Schema ---
{schema}

--- User Question ---
{question}

--- Cypher Query ---
"""

cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)

cypher_qa = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    verbose=True,
    cypher_prompt=cypher_prompt,
    allow_dangerous_requests=True
)


