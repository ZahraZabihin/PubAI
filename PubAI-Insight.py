import streamlit as st
import os
import tempfile
import pandas as pd
from dotenv import load_dotenv
from extractor_utils import OpenAIExtractor
from core4 import DocumentAnalyzer
from pubmed4 import PubMedSearcher
import PyPDF2
import re

# Load environment variables
load_dotenv()

# Initialize components
pubmed_searcher = PubMedSearcher()
document_analyzer = DocumentAnalyzer()
openai_extractor = OpenAIExtractor()

# OpenAI token limit handling
MAX_TOKENS = 8000

def split_dataframe(df, chunk_size=50):
    """Splits a DataFrame into smaller chunks."""
    return [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]

def process_chunk(chunk, prompt):
    combined_text = ""
    references = []

    for index, row in chunk.iterrows():
        article_reference = f"{row['First Author']} et al. ({row['Year']}) [PubMed]"
        article_text = f"Title: {row['Title']}\nAbstract: {row['Abstract']} ({article_reference})\n"
        combined_text += article_text
        references.append(article_reference)

    return combined_text, references

def get_token_count(text, model_name="gpt-4o"):
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(text))

def handle_text_split(text, prompt, model_name="gpt-4o"):
    """Queries OpenAI without splitting the text, assumes text is processed and combined beforehand."""
    return openai_extractor.query_openai_with_custom_prompt(text, prompt)

def split_files(uploaded_files, group_size=10):
    """Splits uploaded files into chunks of specified size."""
    grouped_files = []
    num_files = len(uploaded_files)
    
    for i in range(0, num_files, group_size):
        grouped_files.append(uploaded_files[i:i + group_size])
    
    return grouped_files

def extract_text_from_pdfs(uploaded_files):
    """Extracts text directly from uploaded PDF files."""
    combined_text = ""
    file_references = []  # List to hold PDF names for reference

    for uploaded_file in uploaded_files:
        pdf_name = os.path.basename(uploaded_file.name)
        file_references.append(pdf_name)

        try:
            # Extract text from the PDF
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text()

            # Append the extracted text and PDF file name to the combined text
            combined_text += f"{pdf_text}\n\n[Source: {pdf_name}]\n"
        except Exception as e:
            st.error(f"Error reading PDF file {pdf_name}: {str(e)}")
    
    return combined_text, file_references


# Streamlit interface
st.title("PubAI Insights")

# Get user input
pubmed_query = st.text_input("Enter PubMed search query:", "")
uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)
prompt_input = st.text_area("Enter the prompt to ask OpenAI:", "")

# Perform PubMed or PDF or both analysis
if st.button("Run Analysis"):
    combined_text = ""
    references = []

    if pubmed_query and not uploaded_files:
        st.info("Extracting information from PubMed only...")
        # Step 1: Fetch articles from PubMed based on the query
        pubmed_ids = pubmed_searcher.fetch_all_pubmed_ids(pubmed_query)
        articles = pubmed_searcher.fetch_article_details(pubmed_ids)
        df = pd.DataFrame(articles)
        st.write("Extracted PubMed Articles:", df)

        # Step 2: Split DataFrame into chunks of 50 articles
        chunks = split_dataframe(df, chunk_size=50)
        
        # Prepare lists to store chunk-wise responses and references
        all_chunk_responses = []
        all_references = []

        # Step 3: Process each chunk of articles and query AI for each chunk
        for chunk in chunks:
            chunk_text, chunk_references = process_chunk(chunk, prompt_input)
            chunk_response = openai_extractor.query_openai_with_custom_prompt(
                chunk_text, 
                prompt_input
            )
            all_chunk_responses.append(chunk_response)
            all_references.extend(chunk_references)

        combined_text = " ".join(all_chunk_responses)








    elif uploaded_files and not pubmed_query:
        st.info("Extracting information from PDFs only...")
        
        # Extract and combine text from the uploaded PDFs
        combined_text, references = extract_text_from_pdfs(uploaded_files)

        # Query OpenAI with the extracted text from PDFs
        final_response = openai_extractor.query_openai_with_custom_prompt(
            combined_text, 
            prompt_input
        )






    elif pubmed_query and uploaded_files:
        st.info("Extracting information from both PubMed and PDFs...")

        # Step 1: Fetch articles from PubMed based on the query
        pubmed_ids = pubmed_searcher.fetch_all_pubmed_ids(pubmed_query)
        articles = pubmed_searcher.fetch_article_details(pubmed_ids)
        df = pd.DataFrame(articles)
        st.write("Extracted PubMed Articles:", df)

        # Step 2: Split DataFrame into chunks of 50 articles
        chunks = split_dataframe(df, chunk_size=50)
        all_chunk_responses = []
        all_references = []

        # Step 3: Process each chunk of articles and query AI for each chunk
        for chunk in chunks:
            chunk_text, chunk_references = process_chunk(chunk, prompt_input)
            chunk_response = openai_extractor.query_openai_with_custom_prompt(
                chunk_text, 
                prompt_input
            )
            all_chunk_responses.append(chunk_response)
            all_references.extend(chunk_references)

        combined_pubmed_text = " ".join(all_chunk_responses)

        # Extract and combine text from the uploaded PDFs
        combined_pdf_text, references = extract_text_from_pdfs(uploaded_files)

        # Combine both PubMed and PDF text
        combined_text = combined_pubmed_text + " " + combined_pdf_text








    # Perform OpenAI analysis if there's any text to process
    if combined_text:
        st.info("Sending text to OpenAI for analysis...")
        
        # Query OpenAI with the combined text
        final_response = openai_extractor.query_openai_with_custom_prompt(
            combined_text, 
            prompt_input
        )

        # Display results
        st.subheader("Final Response:")
        st.write("The following text includes data extracted from these PDF files:")
        st.write(", ".join(references))
        st.write(final_response)

        # Download option
        st.download_button("Download Full Response", data=final_response.encode('utf-8'), file_name="final_response.txt")
