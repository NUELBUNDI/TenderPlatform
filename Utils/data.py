from supabase import create_client, Client
import pandas as pd

class DisplayContractData:
    """
    A class to interact with Supabase to retrieve and filter tender data based on keywords.
    
    Attributes:
        url (str): Supabase URL.
        api_key (str): Supabase API key.
        key_words (list): List of keywords to filter tenders.
        client (Client): Supabase client instance.
        data (DataFrame): DataFrame to hold the retrieved data.
    """
    
    def __init__(self, url, api_key, key_words):
        """
        Initializes the DisplayContractData class.
        
        Args:
            url (str): Supabase URL.
            api_key (str): Supabase API key.
            key_words (list): Keywords to filter tenders.
        """
        self.api_key = api_key
        self.url = url
        self.key_words = key_words
        self.client: Client = create_client(self.url, self.api_key)
        self.data = None
        
    def select_data_from_db(self):
        """
        Fetches all data from the 'Tenders' table in the database.
        
        Returns:
            DataFrame: A DataFrame containing the retrieved data.
            str: A message if no data is retrieved.
        
        Raises:
            Exception: If an error occurs while fetching the data.
        """
        try:
            response = self.client.table('Tenders').select('*').execute()
            if response.data:
                self.data = pd.DataFrame(response.data)
                return self.data
            else:
                return "No data retrieved from the database"
        except Exception as err:
            raise Exception(f'Error selecting data from the database: {err}')
            
    def filter_by_key_words(self):
        """
        Filters the retrieved data based on the specified keywords.
        
        Returns:
            DataFrame: A DataFrame containing filtered data sorted by published date.
        
        Raises:
            Exception: If no data is available or an error occurs during filtering.
        """
        try:
            if self.data is None:
                raise ValueError("No data available. Please retrieve data from the database first.")
            
            # Create a regex pattern from the keywords
            pattern = '|'.join(self.key_words)
            
            # Filter rows where the tender title contains any of the keywords
            filtered_df = self.data[self.data['tender_title'].str.contains(pattern, case=False, na=False)]
            
            # Convert published_date to datetime and sort the filtered data
            filtered_df['published_date'] = pd.to_datetime(filtered_df['published_date'], errors='coerce').dt.strftime('%Y-%m-%d')
            filtered_df = filtered_df.sort_values(by='published_date', ascending=False)
            
            return filtered_df
        except Exception as err:
            raise Exception(f'Error filtering data: {err}')
