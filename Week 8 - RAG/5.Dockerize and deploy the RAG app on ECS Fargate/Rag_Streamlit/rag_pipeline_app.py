import streamlit as st
from pypdf import PdfReader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import google.generativeai as genai
import nltk
from nltk.tokenize import sent_tokenize
import numpy as np




nltk.download('punkt')
genai.configure(api_key="AIzaSyBs0co95TeFd_4HeUT1BsCGEhqpMziGjK4")

# 📄 PDF text extraction
def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    return "".join(page.extract_text() for page in reader.pages)

# 🧩 Chunking methods
def chunk_text(text, method, params):
    if method == "RecursiveCharacterTextSplitter":
        splitter = CharacterTextSplitter(
            chunk_size=int(params["chunk_size"]),
            chunk_overlap=int(params["chunk_overlap"]),
            separator=params.get("separator", "\n\n")
        )
        return splitter.split_text(text)
    elif method == "FixedWindowSplitter":
        size = int(params["window_size"])
        overlap = int(params["overlap_size"])
        return [text[i:i+size] for i in range(0, len(text), size - overlap)]
    elif method == "SentenceSplitter":
        return [s for s in sent_tokenize(text) if len(s) >= int(params["min_sentence_length"])]
    else:
        return [text]  # Placeholder for other chunkers

# 🔍 Retrieval methods
def retrieve_chunks(chunks, query, method, params):
    if method == "FAISS":
        embed_model = HuggingFaceEmbeddings(model_name=params["embedding_model"])
        db = FAISS.from_texts(chunks, embedding=embed_model)
        docs = db.similarity_search(query, k=int(params["top_k"]))
        return [doc.page_content for doc in docs]
    elif method == "BM25":
        tokenized_corpus = [chunk.split(" ") for chunk in chunks]
        bm25 = BM25Okapi(tokenized_corpus)
        scores = bm25.get_scores(query.split(" "))
        top_indices = np.argsort(scores)[-int(params["k1"]):][::-1]
        return [chunks[i] for i in top_indices]
    elif method == "Hybrid":
        return chunks[:int(params["top_k"])]  # Placeholder
    else:
        return chunks[:3]  # Placeholder for other retrievers

# 🧠 LLM response
def generate_response(chunks, query, method, params):
    context = "\n\n".join(chunks)
    prompt = f"{params.get('system_instruction', 'You are a helpful assistant.')}\n\nContext:\n{context}\n\nQuery: {query}"
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text

# 📊 Evaluation
def evaluate_response(response, method, params):
    if method == "WordCount":
        wc = len(response.split())
        return f"Response contains {wc} words."
    elif method == "SemanticSimilarity":
        embedder = SentenceTransformer(params["embedding_model"], device='cpu')
        query_vec = embedder.encode(params["query"])
        response_vec = embedder.encode(response)
        score = np.dot(query_vec, response_vec) / (np.linalg.norm(query_vec) * np.linalg.norm(response_vec))
        return f"Semantic similarity score: {score:.2f}"
    else:
        return "Evaluation method not implemented."

# 🔧 Parameter templates
param_templates = {
    # Chunking
    "RecursiveCharacterTextSplitter": {"chunk_size": "500", "chunk_overlap": "50", "separator": "\\n\\n"},
    "TokenTextSplitter": {"tokens_per_chunk": "256", "tokenizer_name": "gpt2"},
    "SentenceSplitter": {"min_sentence_length": "20"},
    "FixedWindowSplitter": {"window_size": "500", "overlap_size": "50"},
    "MarkdownHeaderTextSplitter": {"headers_to_split_on": "['#', '##']", "strip_headers": "True"},
    "TableAwareSplitter": {"table_detection_mode": "pdfplumber", "min_table_rows": "2"},
    "SemanticSplitter": {"embedding_model": "sentence-transformers/all-MiniLM-L6-v2", "similarity_threshold": "0.7"},

    # Retrieval
    "FAISS": {"embedding_model": "sentence-transformers/all-MiniLM-L6-v2", "top_k": "3", "distance_metric": "cosine"},
    "BM25": {"tokenizer": "whitespace", "k1": "3", "b": "0.75"},
    "Hybrid": {"bm25_weight": "0.5", "embedding_weight": "0.5", "top_k": "3"},
    "Chroma": {"persist_directory": "./chroma_db", "embedding_model": "sentence-transformers/all-MiniLM-L6-v2", "top_k": "3"},
    "Weaviate": {"endpoint": "http://localhost:8080", "api_key": "", "top_k": "3", "filter_conditions": "{}"},
    "Milvus": {"collection_name": "rag_collection", "top_k": "3", "metric_type": "L2"},
    "Elasticsearch": {"index_name": "rag_index", "top_k": "3", "query_boost": "1.0", "vector_boost": "1.0"},

    # LLM
    "Gemini": {"temperature": "0.7", "top_p": "0.9", "max_tokens": "1024", "system_instruction": "You are a helpful assistant."},
    "PromptTemplate": {"template_type": "qa", "format_style": "markdown"},
    "ChainOfThought": {"reasoning_depth": "3", "step_separator": "->"},
    "SystemInstructions": {"role": "assistant", "tone": "neutral", "format": "plain"},
    "MultiTurnMemory": {"history_length": "5", "context_window": "1024"},
    "ToolUse": {"tool_schema": "{}", "tool_trigger_keywords": "['search', 'calculate']"},

    # Evaluation
    "WordCount": {"min_words": "50", "max_words": "500"},
    "BLEU": {"weights": "(0.25, 0.25, 0.25, 0.25)", "smoothing_function": "method1"},
    "ROUGE": {"rouge_types": "['rouge1', 'rougeL']", "use_stemmer": "True"},
    "SemanticSimilarity": {"embedding_model": "sentence-transformers/all-MiniLM-L6-v2", "similarity_metric": "cosine", "threshold": "0.7", "query": ""},
    "LLMJudge": {"evaluation_prompt": "Rate the helpfulness and accuracy.", "criteria_list": "['helpfulness', 'factuality']"},
    "HallucinationDetection": {"fact_check_prompt": "Verify factual claims.", "confidence_threshold": "0.6"},
    "HumanFeedback": {"rating_scale": "1-5", "feedback_fields": "['clarity', 'accuracy']"}
}

# 🚀 Streamlit UI
st.title("🔍 Fully Configurable RAG Pipeline with Gemini 2.5 Flash")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")
query = st.text_input("Enter your query")

chunk_model = st.selectbox("Select Chunking Model", list(param_templates.keys())[:7])
retrieval_model = st.selectbox("Select Retrieval Model", list(param_templates.keys())[7:14])
llm_model = st.selectbox("Select LLM Model", list(param_templates.keys())[14:21])
eval_model = st.selectbox("Select Evaluation Model", list(param_templates.keys())[21:])

st.markdown("### 🔧 Configure Parameters")

chunk_params = {k: st.text_input(f"{chunk_model} - {k}", value=v) for k, v in param_templates[chunk_model].items()}
retrieval_params = {k: st.text_input(f"{retrieval_model} - {k}", value=v) for k, v in param_templates[retrieval_model].items()}
llm_params = {k: st.text_area(f"{llm_model} - {k}", value=v) for k, v in param_templates[llm_model].items()}
eval_params = {k: st.text_input(f"{eval_model} - {k}", value=query if k == "query" else v) for k, v in param_templates[eval_model].items()}

if uploaded_file and query:
    with st.spinner("Running RAG pipeline..."):
        try:
            text = extract_text_from_pdf(uploaded_file)
            chunks = chunk_text(text, chunk_model, chunk_params)
            retrieved = retrieve_chunks(chunks, query, retrieval_model, retrieval_params)
            response = generate_response(retrieved, query, llm_model, llm_params)
            evaluation = evaluate_response(response, eval_model, eval_params)

            st.subheader("📤 Response")
            st.write(response if response else "No response generated.")

            st.subheader("📊 Evaluation")
            st.write(evaluation if evaluation else "No evaluation result.")
        except Exception as e:
            st.error(f"❌ Error during pipeline execution: {e}")
