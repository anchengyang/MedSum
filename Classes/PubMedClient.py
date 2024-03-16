from dataclasses import dataclass
import os
from dotenv import load_dotenv
from Bio import Entrez

from utils.utils import create_df_fill_full_abstract, extract_keywords_from_results
from utils.constants import keywords, study_designs

load_dotenv()
BIO_EMAIL = os.getenv("BIO_EMAIL")

@dataclass
class PubMedClient:
    def __init__(self):
        self.email = BIO_EMAIL


    def search(self, query, max_results=10000):
        Entrez.email = self.email
        handle = Entrez.esearch(
            db='pubmed',
            sort='relevance',
            retmax=str(max_results),
            retmode='xml',
            term=query,
        )
        results = Entrez.read(handle)
        return results

    def fetch_details(self, id_list):
        ids = ','.join(id_list)
        Entrez.email = self.email
        handle = Entrez.efetch(
            db='pubmed',
            retmode='xml',
            id=ids,
        )
        papers = Entrez.read(handle)
        return papers


if __name__ == '__main__':
    client = PubMedClient()
    results = client.search('fever AND covid', max_results=10)
    id_list = results['IdList']
    papers = client.fetch_details(id_list)
    df = create_df_fill_full_abstract(papers)
    print(df)

    extract_abstract = extract_keywords_from_results(df, keywords, study_designs)
    print(extract_abstract)