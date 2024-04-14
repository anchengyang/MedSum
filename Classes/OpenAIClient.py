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

from dataclasses import dataclass

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@dataclass
class OpenAIClient:
    def __init__(self, bg_data: list[Document]):
        self.bg_data = bg_data
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(model_name="gpt-4", temperature=0, openai_api_key=OPENAI_API_KEY)
        self.persist_directory = "chroma"
        self.db = None

    def split(self):
        '''
        Splits document data into Langchain Chunks, returning a chunked document
        '''
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
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
    
    def get_retriever(self, document_content_description):
        '''
        Returns a retriever based on a content description and metadata field info
        '''
        metadata_field_info=[
            AttributeInfo(
                name="label",
                description="The type of surgery protocol", 
                type="string",
            ),
            AttributeInfo(
                name="Outcomes_from_results",
                description="The patients outcomes measured", 
                type="string or list[string]",
            ),
            AttributeInfo(
                name="Study_design",
                description="The different study design which denotes the quality of the scientific articles", 
                type="string or list[string]"
            ),
        ]
        retriever = SelfQueryRetriever.from_llm(
            self.llm, self.load_db(), document_content_description, metadata_field_info, search_kwargs={"k": 10},verbose=True
        )
        return retriever
    
    def qa_func(self, system_template):
        '''
        Sets a prompt with human + system template.
        Returns a RetrievalQA Object:
        - Retriever retrieves relevant documents from the vector DB
        '''
        messages = [
            SystemMessagePromptTemplate.from_template(system_template),
            HumanMessagePromptTemplate.from_template("{question}")
        ]
        qa_prompt = ChatPromptTemplate.from_messages(messages)
        #memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        #qa = ConversationalRetrievalChain.from_llm(llm=llm, retriever=vectorstore.as_retriever(), return_source_documents=False,combine_docs_chain_kwargs={"prompt": qa_prompt},memory=memory,verbose=True)
        qa = RetrievalQA.from_chain_type(llm=self.llm, retriever=self.load_db().as_retriever(), chain_type_kwargs={"prompt": qa_prompt},verbose=True, return_source_documents=True)

        return qa
    
    def print_result(self, query, system_template):
        '''
        gets RetrievalQA object and calls it with a query.
        Returns the query, results, and reference links/
        '''
        qa = self.qa_func(system_template)
        result = qa(query)

        reference_links = []
        pmids = []
        for doc in result["source_documents"]:
            pmid = doc.metadata["PMID"]
            if pmid not in pmids:
                pmids.append(pmid)
                link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                reference_links.append(link)

        formatted_reference_links = "\n- ".join(reference_links)

        output_text = f"""
        ### Question: 
        {result["query"]}

        ### Response: 
        {result["result"]}

        ### Reference Links:
        {formatted_reference_links}
        """

        print(Markdown(output_text).data)
        return result
