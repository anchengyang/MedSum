import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.vectorstores.chroma import Chroma
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate,  ChatPromptTemplate
from IPython.display import display, Markdown
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_text_splitters import CharacterTextSplitter

from dataclasses import dataclass

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@dataclass
class FilteringClient:
    def __init__(self, bg_data: list[Document]):
        self.bg_data = bg_data
        self.embeddings = OpenAIEmbeddings()
        # self.llm = ChatOpenAI(temperature=0)
        self.llm = ChatOpenAI(model_name="gpt-4", temperature=0.5, openai_api_key=OPENAI_API_KEY)
        self.persist_directory = "chroma"
        self.db = None

    def split(self):
        '''
        Splits document data into Langchain Chunks, returning a chunked document
        '''
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0)
        chunks = text_splitter.split_documents(self.bg_data)
        return chunks

    def load_db(self):
        '''
        Loads/Creates Chroma DB
        '''
        # only run this once
        if self.db is None:
            print("Loading DB")
            chunks = self.split()
            self.db = Chroma.from_documents(
                chunks,
                embedding=self.embeddings,
                # metadatas=[{"source": f"{i}-wb23"} for i in range(len(chunks))],
                persist_directory=self.persist_directory,
            )
            self.db.persist()
        # else:
        #     self.db = Chroma(persist_directory=self.persist_directory, embeddings=self.embeddings)

        return self.db
    
    
    def get_retriever(self):
        '''
        Returns a retriever based on a content description and metadata field info
        '''
        metadata_field_info=[
            AttributeInfo(
                name="PMID",
                description="The unique PubMed ID corresponding to the paper", 
                type="integer",
            ),
            AttributeInfo(
                name="Title",
                description="The title of the paper", 
                type="integer",
            ),
            AttributeInfo(
                name="Abstract",
                description="A concise summary of the research paper", 
                type="string or list[string]"
            ),
        ]

        document_content_description = "A set of research paper IDs and their abstracts"

        retriever = SelfQueryRetriever.from_llm(
            self.llm,
            self.load_db(),
            document_content_description,
            metadata_field_info,
            enable_limit = True,
            verbose=True)
        return retriever

    
    def rag_result(self, research_question, no_of_articles, population, intervention, comparison, outcome):
        prompt = PromptTemplate(
        input_variables=["research_question", "population", "intervention", "comparison", "outcome", "no_of_articles"],
        template=
        """
            You are a researcher performing a literature review based on a research question, PICO, and a number of documents to select.
            PICO is an acronym for Population, Intervention, Comparison, and Outcome, and it's a framework used in research to structure questions and facilitate literature reviews.
            Research Question: {input}
            Population: {population}
            Intervention: {intervention}
            Comparison: {comparison}
            Outcome: {outcome}
            Number of Articles to Select: {no_of_articles}

            The dataset provided is a pre-processed dataset of PubMed articles.
            It includes the following columns:
            'PMID': the PubMed ID of the published article,
            'Title': the title of the published article,
            'Abstract': an abstract of the published article,
            ----------------
            {context}
            --------------

            Based on these details, you are required to select {no_of_articles} articles that are relevant to the research question.
            For each of these articles, provide:
            - The title of the article
            - The PubMed ID of the article
            - A brief explanation why you selected it, including a snippet from the article that supports its relevance.


            If there are actual numbers and percentages, state it.
            """
        )

        question_answer_chain = create_stuff_documents_chain(
            self.llm, prompt)
        chain = create_retrieval_chain(self.get_retriever(), question_answer_chain)

        result = chain.invoke({"input": research_question, 
                            "no_of_articles": no_of_articles, 
                            "population": population, 
                            "intervention": intervention, 
                            "comparison": comparison, 
                            "outcome": outcome})       

        reference_links = []
        pmids = []
        for doc in result["context"]:
            pmid = doc.metadata["PMID"]
            if pmid not in pmids:
                pmids.append(pmid)
                link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                reference_links.append(link)

        formatted_reference_links = "\n- ".join(reference_links)

        output_text = f"""
        ### Question: 
        {result["input"]}

        ### Response: 
        {result["answer"]}

        ### Reference Links:
        {formatted_reference_links}
        """

        print(Markdown(output_text).data)
        return result

