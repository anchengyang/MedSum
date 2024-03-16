keywords = ["length of stay", 'mortality', 'complication', 'morbidity', 'readmission', 'cost', 'length of hospitalization',
           'satisfaction', 'opioid', 'icu','anastomotic leakage']
study_designs = ["systematic review", "meta-analysis", "multicenter", "multicentre", "randomized controlled study", "randomized controlled trial",
                "randomised controlled study", "randomised controlled trial", "randomized clinical trial", "randomised clinical trial"]
document_content_description = "A database of scientific articles related to enhanced recovery after surgery (ERAS) and every article has 'Outcomes_from_results' which represent the benefits of ERAS"
system_template = """The provided {context} is a tabular dataset containing scientific articles that are related to enhanced recovery after surgery (ERAS) in hip and knee surgery
The dataset includes the following columns:
'Title': the title of the published article,
'Abstract': an abstract of the published article,
"Journal": the journal where the article is published, 
"Language": the language the article is written in, 
"Year": the year of publication,
"Month": the month of publication,
"label": the type of surgery protocol,
"Outcomes": the patients outcomes measured extracted from the article Title,
"Outcomes_from_results": the clinical outcomes measured extracted from the article Abstract,
"Study_design": the study design which denotes the quality of the article
----------------
{context}
--------------
If there is actual numbers and percentages, state it. \
For the numbers and percentages, provide a reference list stating the title and the year of publication.
"""