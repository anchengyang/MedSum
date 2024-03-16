import pandas as pd

def get_abstract(paper):
        abstract = ''
        if 'Abstract' in paper['MedlineCitation']['Article']:
            abstract = paper['MedlineCitation']['Article']['Abstract']['AbstractText']
            if isinstance(abstract, list):
                abstract = ' '.join(abstract)
        return abstract

def create_df_full_abstract(papers):
    pmid_list = []
    title_list= []
    abstract_list=[]
    journal_list = []
    language_list =[]
    pubdate_year_list = []
    pubdate_month_list = []
    
    for i, paper in enumerate (papers['PubmedArticle']):
        try:
            title_list.append(paper['MedlineCitation']['Article']['ArticleTitle'])
        except:
            title_list.append('No Data')

        try:
            key_to_extract = 'Label'
            string_elements = paper['MedlineCitation']['Article']['Abstract']['AbstractText']
            values = [element for element in string_elements if key_to_extract in element.attributes and element.attributes[key_to_extract] == 'RESULTS']
            abstract_list.append(' '.join(values))
        except:
            abstract_list.append('No Abstract')

        try:    
            journal_list.append(paper['MedlineCitation']['Article']['Journal']['Title'])
        except:
            journal_list.append('No Data')

        try:
            language_list.append(paper['MedlineCitation']['Article']['Language'][0])
        except:
            language_list.append('No Data')

        try: 
            pubdate_year_list.append(paper['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Year'])
        except:
            pubdate_year_list.append('No Data')

        try:
            pubdate_month_list.append(paper['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate']['Month'])
        except:
            pubdate_month_list.append('No Data')
        
        try:
            pmid_list.append(str(paper['MedlineCitation']['PMID']))
        except:
            pmid_list.append('No Data')
            
    df = pd.DataFrame(list(zip(pmid_list, title_list, abstract_list, journal_list, language_list, pubdate_year_list, pubdate_month_list)),
        columns=['PMID', 'Title', 'Abstract', 'Journal', 'Language', 'Year','Month'])
    
    return df

def create_df_fill_full_abstract(articles):
    existing_df = create_df_full_abstract(articles)
    
    abstract_list_1=[]

    for i, paper in enumerate (articles['PubmedArticle']):
        try:
            abstract_list_1.append(paper['MedlineCitation']['Article']['Abstract']['AbstractText'])
        except:
            abstract_list_1.append('No Abstract')
    
    existing_df["Abstract_1"] = abstract_list_1

    existing_df.loc[existing_df['Abstract'] == '', 'Abstract'] = existing_df.loc[existing_df['Abstract'] == '', 'Abstract_1']
    
    return existing_df

def extract_keywords(title, keywords):
    extracted = [keyword for keyword in keywords if keyword in title]
    return ', '.join(extracted)


def extract_study_design(title, study_designs):
    extracted = [study_design for study_design in study_designs if study_design in title]
    return ', '.join(extracted)

def extract_keywords_from_results(df_full_abstract, keywords, study_designs):
    # Create a new column with extracted keywords
    df_full_abstract['Outcomes'] = df_full_abstract['Title'].apply(extract_keywords, keywords=keywords)
    df_full_abstract['Outcomes_from_results'] = df_full_abstract['Abstract'].apply(extract_keywords, keywords=keywords)
    df_full_abstract['Study_design'] = df_full_abstract['Title'].apply(extract_study_design, study_designs=study_designs)

    return df_full_abstract
