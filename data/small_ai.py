from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaLLM
import os


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

    for answer in llm.stream(prompt):
        print(answer, end="")




if not os.path.exists("./vectordb"):
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

    vectordb.persist()
    print("Vector database created and persisted.")
else:
    print("Loading existing vector database...")
    vectordb = Chroma(
        embedding_function=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
        persist_directory="./vectordb"
    )
    print("Vector database loaded.")

retriever = vectordb.as_retriever()

llm = OllamaLLM(model="phi3")


print("Asking question...")

ask_question("What is the role of Queue Manager?")


