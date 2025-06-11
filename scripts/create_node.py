import pandas as pd
from neo4j import GraphDatabase
import os
import re
from dotenv import load_dotenv

load_dotenv(override=True)

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

constraints = [
    """
    CREATE CONSTRAINT agreement_name_unique IF NOT EXISTS
    FOR (a:Agreement) REQUIRE a.name IS UNIQUE
    """,
    """
    CREATE CONSTRAINT clause_text_unique IF NOT EXISTS
    FOR (c:Clause) REQUIRE c.text IS UNIQUE
    """,
    """
    CREATE CONSTRAINT clause_type_unique IF NOT EXISTS
    FOR (t:ClauseType) REQUIRE t.name IS UNIQUE
    """,
    """
    CREATE CONSTRAINT governing_law_name_unique IF NOT EXISTS
    FOR (g:GoverningLaw) REQUIRE g.name IS UNIQUE
    """,
    """
    CREATE CONSTRAINT party_name_unique IF NOT EXISTS
    FOR (p:Party) REQUIRE p.name IS UNIQUE
    """
]

with driver.session(database="neo4j") as session:
    for query in constraints:
        session.run(query)
        print("✅ Constraint çalıştırıldı")


def safe_strip(val):
    return val.strip() if isinstance(val, str) else ""


def extract_agreement_type(filename):
    match = re.search(r'([A-Za-z &\-]+Agreement)', filename, re.IGNORECASE)
    return match.group(1).title() if match else "Unknown"


df = pd.read_csv("../data/cuad/master_clauses.csv")

clause_columns = [col.replace("-Answer", "") for col in df.columns if col.endswith("-Answer")]

def insert_clause(tx, agreement, clause_text, clause_type, governing_law, agreement_type,
                  agreement_date, effective_date, expiration_date, renewal_term, notice_period, source_file, parties):
    tx.run("""
        MERGE (a:Agreement {name: $agreement})
        SET a.type = $agreement_type,
            a.date = $agreement_date,
            a.effective_date = $effective_date,
            a.expiration_date = $expiration_date,
            a.renewal_term = $renewal_term,
            a.notice_period = $notice_period,
            a.source_file = $source_file

        MERGE (c:Clause {text: $clause})
        SET c.clause_type = $clause_type

        MERGE (t:ClauseType {name: $clause_type})
        MERGE (a)-[:HAS_CLAUSE]->(c)
        MERGE (c)-[:OF_TYPE]->(t)

        FOREACH (_ IN CASE WHEN $governing_law IS NOT NULL AND $governing_law <> "" THEN [1] ELSE [] END |
            MERGE (g:GoverningLaw {name: $governing_law})
            MERGE (c)-[:UNDER_LAW]->(g)
        )

        FOREACH (party IN $parties |
            MERGE (p:Party {name: party})
            MERGE (c)-[:MENTIONS]->(p)
        )
    """, {
        "agreement": agreement,
        "clause": clause_text,
        "clause_type": clause_type,
        "governing_law": governing_law,
        "agreement_type": agreement_type,
        "agreement_date": agreement_date,
        "effective_date": effective_date,
        "expiration_date": expiration_date,
        "renewal_term": renewal_term,
        "notice_period": notice_period,
        "source_file": source_file,
        "parties": parties
    })

with driver.session(database="neo4j") as session:
    for idx, row in df.iterrows():
        filename_raw = safe_strip(row.get("Filename", "Unknown Agreement"))
        agreement_name = os.path.splitext(filename_raw)[0]
        agreement_type = extract_agreement_type(filename_raw)
        governing_law = safe_strip(row.get("Governing Law-Answer", ""))
        agreement_date = safe_strip(row.get("Agreement Date-Answer", ""))
        effective_date = safe_strip(row.get("Effective Date-Answer", ""))
        expiration_date = safe_strip(row.get("Expiration Date-Answer", ""))
        renewal_term = safe_strip(row.get("Renewal Term-Answer", ""))
        notice_period = safe_strip(row.get("Notice Period To Terminate Renewal- Answer", ""))
        source_file = filename_raw
        parties_raw = safe_strip(row.get("Parties-Answer", ""))
        parties = [p.strip() for p in parties_raw.split(",") if p.strip()]

        for clause_type in clause_columns:
            clause_text = safe_strip(row.get(f"{clause_type}-Answer", ""))
            if clause_text:
                session.write_transaction(
                    insert_clause,
                    agreement_name,
                    clause_text,
                    clause_type,
                    governing_law,
                    agreement_type,
                    agreement_date,
                    effective_date,
                    expiration_date,
                    renewal_term,
                    notice_period,
                    source_file,
                    parties
                )

        print(f"✅ {idx+1}/{len(df)} sözleşme işlendi: {agreement_name} ({agreement_type})")

driver.close()
