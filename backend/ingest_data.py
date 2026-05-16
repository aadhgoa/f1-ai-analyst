import fastf1
import chromadb
from chromadb.utils import embedding_functions

def ingest():
    print("Setting up FastF1 cache...")
    fastf1.Cache.enable_cache('cache/')
    
    print("Connecting to ChromaDB...")
    client = chromadb.HttpClient(host="localhost", port=8080)
    
    # Use default sentence transformers embedding function
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    print("Getting or creating collection...")
    collection = client.get_or_create_collection(
        name="f1_context",
        embedding_function=sentence_transformer_ef
    )
    
    print("Fetching F1 schedule for 2026...")
    schedule = fastf1.get_event_schedule(2026)
    
    docs = []
    metadatas = []
    ids = []
    
    for index, row in schedule.iterrows():
        if row['EventFormat'] != 'testing':
            doc = f"The 2026 {row['EventName']} was held at {row['Location']}, {row['Country']}. The race took place on {row['EventDate'].strftime('%Y-%m-%d')}."
            docs.append(doc)
            metadatas.append({
                "year": 2026,
                "round": row['RoundNumber'],
                "country": row['Country'],
                "location": row['Location'],
                "event_name": row['EventName']
            })
            ids.append(f"2026_round_{row['RoundNumber']}")
    
    print(f"Inserting {len(docs)} records into ChromaDB...")
    collection.upsert(
        documents=docs,
        metadatas=metadatas,
        ids=ids
    )
    
    print("Ingestion complete!")

if __name__ == "__main__":
    ingest()
