from PySide6.QtCore import QThread, Signal
import requests
import pandas as pd
from modules.utils import clean_scopus_data

class QueryDownloadWorker(QThread):
    progress_signal = Signal(int)
    log_signal = Signal(str)
    
    def __init__(self, query, api_key, insttoken, api_type):
        super().__init__()
        self.query = query
        self.api_key = api_key
        self.insttoken = insttoken
        self.api_type = api_type
        self.result = None

    def run(self):
        if self.api_type == 'Scopus':
            df = self.download_from_scopus()
            if df is not None:
                self.result = df  # Guardar el DataFrame limpio
            else:
                self.result = pd.DataFrame()  # Asignar un DataFrame vacío si falla
        elif self.api_type == 'Web of Science':
            df = self.download_from_wos()
            if df is not None:
                self.result = df  # Guardar el DataFrame limpio
            else:
                self.result = pd.DataFrame()  # Asignar un DataFrame vacío si falla

    def download_from_scopus(self):
        url = 'https://api.elsevier.com/content/search/scopus'
        headers = {'X-ELS-APIKey': self.api_key,
                   'X-ELS-Insttoken': self.insttoken,
                   'Accept': 'application/json'}
        params = {'query': self.query, 'count': 25, 'start': 0}
        all_results = []

        while True:
            self.log_signal.emit(f"Fetching results starting at {params['start']}")
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                self.log_signal.emit(f"Error {response.status_code}: {response.text}")
                break

            data = response.json()
            entries = data.get('search-results', {}).get('entry', [])
            if not entries:
                break

            all_results.extend(entries)
            self.progress_signal.emit(len(all_results))  # Emitimos el progreso

            if len(entries) < 25:
                break

            params['start'] += 25

        df = pd.DataFrame(all_results)
        df_cleaned = clean_scopus_data(df)
        self.log_signal.emit("Download complete")
        return df_cleaned

    def download_from_wos(self):
        url = 'https://api.clarivate.com/api/woslite/v1/woslite'
        headers = {'X-ApiKey': self.api_key}
        params = {
            'databaseId': 'WOS',
            'usrQuery': self.query,
            'count': 25,
            'firstRecord': 1
        }
        all_results = []

        while True:
            self.log_signal.emit(f"Fetching results starting at {params['firstRecord']}")
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                self.log_signal.emit(f"Error {response.status_code}: {response.text}")
                break

            data = response.json()
            entries = data.get('Data', {}).get('Records', {}).get('records', [])
            if not entries:
                break

            all_results.extend(entries)
            self.progress_signal.emit(len(all_results))  # Emitimos el progreso

            if len(entries) < 25:
                break

            params['firstRecord'] += 25

        df = pd.DataFrame(all_results)
        self.log_signal.emit("Download complete")
        self.result = df
