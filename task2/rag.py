import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

raw_docs = [
    Document(page_content="""
        The Eiffel Tower is a wrought-iron lattice tower located in Paris, France.
        It was constructed between 1887 and 1889 as the entrance arch for the 1889 World's Fair.
        The tower stands 330 metres tall and was the tallest man-made structure in the world
        for 41 years until the Chrysler Building was completed in 1930.
        It is named after its designer, engineer Gustave Eiffel.
    """, metadata={"source": "eiffel_tower.txt"}),

    Document(page_content="""
        Python is a high-level, general-purpose programming language created by Guido van Rossum.
        It was first released in 1991. Python emphasizes code readability and simplicity.
        It supports multiple programming paradigms including procedural, object-oriented,
        and functional programming. Python is widely used in data science, web development,
        automation, and artificial intelligence.
    """, metadata={"source": "python_lang.txt"}),

    Document(page_content="""
        The Amazon Rainforest covers most of the Amazon basin in South America.
        It spans nine countries and represents over half of the world's remaining rainforests.
        The rainforest is home to an estimated 10% of all species on Earth.
        It plays a critical role in regulating the global climate by absorbing carbon dioxide.
        Deforestation is the biggest threat to the Amazon today.
    """, metadata={"source": "amazon.txt"}),
]

splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
chunks = splitter.split_documents(raw_docs)
print(f"Split {len(raw_docs)} documents into {len(chunks)} chunks.\n")

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

vector_store = FAISS.from_documents(chunks, embeddings)
retriever = vector_store.as_retriever(search_kwargs={"k": 2})

print("Vector store built. Ready to answer questions.\n")

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,
)

rag_prompt = ChatPromptTemplate.from_template("""
Answer the question using ONLY the context below.
If the answer is not in the context, say "I don't have that information in my documents."

Context:
{context}

Question: {question}
""")

def ask(question: str) -> str:
    """Retrieves relevant chunks and generates an answer using the LLM."""
    relevant_chunks = retriever.invoke(question)

    print(f"Retrieved {len(relevant_chunks)} chunk(s) for: '{question}'")
    for i, chunk in enumerate(relevant_chunks):
        print(f"  Chunk {i+1} from [{chunk.metadata['source']}]: {chunk.page_content[:80].strip()}...")

    context = "\n\n".join(chunk.page_content for chunk in relevant_chunks)

    filled_prompt = rag_prompt.invoke({"context": context, "question": question})
    response = model.invoke(filled_prompt)
    return response.content

questions = [
    "When was the Eiffel Tower built?",
    "Who created Python?",
    "What is the biggest threat to the Amazon rainforest?",
    "What is the population of Tokyo?",
]

print("=" * 60)
for q in questions:
    print(f"\nQ: {q}")
    answer = ask(q)
    print(f"A: {answer}")
    print("-" * 60)

