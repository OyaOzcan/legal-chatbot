import os
from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_neo4j import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

CUAD_PATH = "../data/cuad/full_contract_txt"

print("1 - .env dosyasından ayarlar yüklendi.")

loader = DirectoryLoader(CUAD_PATH, glob="**/*.txt", loader_cls=TextLoader)
docs = loader.load()
print(f"2 - Toplam {len(docs)} adet belge yüklendi.")
text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
    chunk_size=1500,
    chunk_overlap=200,
)

chunks = text_splitter.split_documents(docs)
print(f"3 - Toplam {len(chunks)} adet chunk oluşturuldu.")

print("4 - Neo4j vektör deposu oluşturuluyor, bekleyin...")
neo4j_db = Neo4jVector.from_documents(
    documents=chunks,
    embedding=OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY")),
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    database="neo4j",
    index_name="cuadVectorIndex",
    node_label="ContractChunk",
    text_node_property="text",
    embedding_node_property="embedding"
)
print("5 - Neo4j vektör deposu başarıyla oluşturuldu.")


print("Neo4j vektör deposu başarıyla oluşturuldu.")

print(f"Toplam belge sayısı: {len(docs)}")
print(f"Toplam chunk sayısı: {len(chunks)}")

for i, chunk in enumerate(chunks[:5]):  
    print(f"Chunk {i+1}: {chunk.page_content[:100]}...") 

print("Neo4j bağlantısı kuruluyor...")

