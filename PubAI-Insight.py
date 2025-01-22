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
st.markdown("""
# **How to Use PubAI Insights for Specific Questions**

**PubAI Insights** is a powerful and versatile tool that allows you to ask specific research questions from PubMed articles, uploaded PDF files, or both. Depending on your needs, you can choose one of the following options:

---

## **Option 1: Analyze PubMed Articles**
If you want to extract information from PubMed articles, follow these steps:

1. **Write a PubMed Query**:
   - Use a structured query to filter articles of interest.
   - For example, if you're researching Kawasaki disease prevalence, write:
     ```
     Kawasaki [Title/Abstract] AND Prevalence [Title/Abstract]
     ```

2. **Enter your query** in the **PubMed Search Query** field on the app.

3. **Define your custom prompt** to ask specific questions. For example:
   ```
   Extract all mentions of epidemiological data related to incidence and prevalence of Kawasaki disease from the following text. For each mention, provide:

   - The incidence/prevalence rate or number of cases described, regardless of how it is expressed (e.g., raw numbers, percentages, or other formats).
   - The specific condition, population group (e.g., region, age group, or year of collecting data), or any other context (e.g., hospitalizations, mortality rates) that the data applies to.
   - If the data is region-specific, mention the region, and highlight if the region is within the United States (e.g., state-level or country-level data).
   - The author(s) and publication year as a reference.
   ```

4. Click **"Run Analysis"**, and the app will fetch articles from PubMed, process them using your custom prompt, and display the results.

---

## **Option 2: Analyze Uploaded PDF Files**
If you want to analyze your own PDF documents:

1. **Upload one or more PDF files** using the **Upload PDF Files** option in the app.

2. **Write a custom prompt** to extract information. For example:
   ```
   Extract all mentions of epidemiological data related to incidence and prevalence of Kawasaki disease from the uploaded text. Provide details on:

   - Incidence/prevalence rates or number of cases.
   - The region, condition, or population group the data applies to.
   - Any context (e.g., year of data collection, hospitalization rates, mortality).
   - References including the document title or filename.
   ```

3. Click **"Run Analysis"**, and the app will extract text from your PDFs, process it using your prompt, and generate insights.
## **Option 3: Analyze Both PubMed Articles and Uploaded PDFs**
For a comprehensive analysis combining PubMed articles and your own documents:

1. **Write a PubMed Query**:
   - Enter a query to search articles of interest on PubMed (e.g., `Kawasaki [Title/Abstract] AND Prevalence [Title/Abstract]`).

2. **Upload PDF Files**:
   - Select and upload your own PDF documents for additional context.

3. **Define a custom prompt** to address both data sources. For example:
   ```
   Extract all epidemiological data on Kawasaki disease incidence and prevalence from the following text. For each mention:

   - Provide the incidence/prevalence rates or cases.
   - Specify regions, conditions, or population groups.
   - Highlight region-specific data within the United States.
   - Include references (authors and publication year for PubMed articles; filenames for PDFs).
   ```

4. Click **"Run Analysis"**, and the app will combine data from both PubMed and your uploaded PDFs, process them with your custom prompt, and provide integrated results.

---

## **Why This App is Powerful**
- **Flexibility**: Choose from PubMed articles, your own PDFs, or both for analysis.
- **Custom Prompts**: Ask detailed, specific questions to meet your research needs.
- **Comprehensive Insights**: Extract epidemiological or other critical data with context and references.
- **Reliability**: The app ensures robust processing of data from multiple sources for accurate and complete results.

With these options, **PubAI Insights** empowers you to extract and analyze research data effortlessly and effectively.
""")

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
