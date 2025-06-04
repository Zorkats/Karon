import pandas as pd
from modules.utils import clean_scopus_data


def test_clean_scopus_data():
    df = pd.DataFrame({
        'dc:title': ['Paper 1', 'Paper 2', 'Paper 3'],
        'author': ['Author 1', 'Author 2', 'Author 3'],
        'prism:publicationName': ['Journal 1', 'Journal 2', 'Journal 3'],
        'year': ['2020', 'not-a-year', '2022'],
        'prism:doi': ['10.1234/1', None, '10.1234/3'],
    })

    cleaned = clean_scopus_data(df)

    assert cleaned.columns.tolist() == ['title', 'author', 'journal', 'year', 'doi']
    assert len(cleaned) == 2
    assert int(cleaned.loc[cleaned['doi'] == '10.1234/1', 'year'].iloc[0]) == 2020
    assert int(cleaned.loc[cleaned['doi'] == '10.1234/3', 'year'].iloc[0]) == 2022
