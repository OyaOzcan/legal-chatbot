import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv(override=True)

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

txt_folder = "../data/cuad/full_contract_txt"  

with driver.session(database="neo4j") as session:
    session.run("""
        CREATE CONSTRAINT full_contract_name_unique IF NOT EXISTS
        FOR (f:FullContract) REQUIRE f.name IS UNIQUE
    """)
    print("✅ Constraint oluşturuldu: FullContract.name benzersiz")

def insert_full_contract(tx, name, text):
    tx.run("""
        MERGE (f:FullContract {name: $name})
        SET f.text = $text
    """, {"name": name, "text": text})

with driver.session(database="neo4j") as session:
    for filename in os.listdir(txt_folder):
        if filename.endswith(".txt"):
            file_path = os.path.join(txt_folder, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
                name = os.path.splitext(filename)[0]
                session.write_transaction(insert_full_contract, name, text)
                print(f"✅ Yüklendi: {name}")

driver.close()
print("🎯 Tüm sözleşmeler FullContract olarak yüklendi.")
