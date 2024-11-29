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
Extract all mentions of epidemiological data related to incidence and prevalence of Kawasaki disease from the following text. For each mention, provide:
```
The incidence/prevalence rate or number of cases described, regardless of how it is expressed (e.g., raw numbers, percentages, or other formats).
The specific condition, population group (e.g., region, age group, or year of collecting data), or any other context (e.g., hospitalizations, mortality rates) that the data applies to.
If the data is region-specific, mention the region, and highlight if the region is within the United States (e.g., state-level or country-level data).
The author(s) and publication year as a reference.
```

4. Click **"Run Analysis"**, and the app will fetch articles from PubMed, process them using your custom prompt, and display the results.

---

## **Option 2: Analyze Uploaded PDF Files**
If you want to analyze your own PDF documents:

1. **Upload one or more PDF files** using the **Upload PDF Files** option in the app.

2. **Write a custom prompt** to extract information. For example:
```
Extract all mentions of epidemiological data related to incidence and prevalence of Kawasaki disease from the uploaded text. Provide details on:

Incidence/prevalence rates or number of cases.
The region, condition, or population group the data applies to.
Any context (e.g., year of data collection, hospitalization rates, mortality).
References including the document title or filename.

```
3. Click **"Run Analysis"**, and the app will extract text from your PDFs, process it using your prompt, and generate insights.

---

## **Option 3: Analyze Both PubMed Articles and Uploaded PDFs**
For a comprehensive analysis combining PubMed articles and your own documents:

1. **Write a PubMed Query**:
- Enter a query to search articles of interest on PubMed (e.g., `Kawasaki [Title/Abstract] AND Prevalence [Title/Abstract]`).

2. **Upload PDF Files**:
- Select and upload your own PDF documents for additional context.

3. **Define a custom prompt** to address both data sources. For example:
```
Extract all epidemiological data on Kawasaki disease incidence and prevalence from the following text. For each mention:

Provide the incidence/prevalence rates or cases.
Specify regions, conditions, or population groups.
Highlight region-specific data within the United States.
Include references (authors and publication year for PubMed articles; filenames for PDFs).

```

4. Click **"Run Analysis"**, and the app will combine data from both PubMed and your uploaded PDFs, process them with your custom prompt, and provide integrated results.

---

## **Why This App is Powerful**
- **Flexibility**: Choose from PubMed articles, your own PDFs, or both for analysis.
- **Custom Prompts**: Ask detailed, specific questions to meet your research needs.
- **Comprehensive Insights**: Extract epidemiological or other critical data with context and references.
- **Reliability**: The app ensures robust processing of data from multiple sources for accurate and complete results.

With these options, **PubAI Insights** empowers you to extract and analyze research data effortlessly and effectively.
