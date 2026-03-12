from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama


def ask_question(question):

    docs = retriever.invoke(question)

    context = "\n".join([d.page_content for d in docs])

    prompt = f"""
Answer the question using the context below.

Context:
{context}

Question:
{question}
"""

    response = llm.invoke(prompt)

    return response



loader = PyPDFLoader('./Problem Management Process.pdf')
docs = loader.load()

print("Loaded document with", len(docs), "pages.")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

print("Splitting document into chunks...")
chunks = splitter.split_documents(docs)

print("Number of chunks:", len(chunks))

print("Creating embeddings...")
embedding = HuggingFaceEmbeddings(
  model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Creating vector database...")
vectordb = Chroma.from_documents(
    documents=chunks,
    embedding=embedding,
    persist_directory="./vectordb"
)

print("Vector database created.")

retriever = vectordb.as_retriever()

llm = Ollama(model="phi3")

print("Asking question...")

answer = ask_question("What is this document about?")

print("\nAnswer:", answer)
