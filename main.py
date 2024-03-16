import os
from Classes.MetaDataCSVLoader import MetaDataCSVLoader
from Classes.OpenAIClient import OpenAIClient
from Classes.PubMedClient import PubMedClient
from utils.constants import keywords, study_designs, system_template
from utils.utils import create_df_fill_full_abstract, extract_keywords_from_results

def main():
    # Process the data
    # openai = OpenAIClient()
    pubmed = PubMedClient()

    results = pubmed.search('fever AND covid', max_results=500)
    id_list = results['IdList']
    papers = pubmed.fetch_details(id_list)
    df = create_df_fill_full_abstract(papers)

    extract_abstract = extract_keywords_from_results(df, keywords, study_designs)
    
    # check if data folder exists, if not create it
    if not os.path.exists('data'):
        os.makedirs('data')
    # save to csv
    extract_abstract.to_csv('data/pubmed.csv', index=False)

    # load the data
    loader = MetaDataCSVLoader(file_path="data/pubmed.csv", metadata_columns=['label', 'Outcomes_from_results', 'Study_design'], encoding="utf-8")
    bg_data = loader.load()

    openai = OpenAIClient(bg_data)

    query_los = "What is the correlation between fever and covid?"

    openai.print_result(query_los, system_template)

    query_los = "What are the outcomes of covid?"

    openai.print_result(query_los, system_template)


if __name__ == '__main__':
    main()