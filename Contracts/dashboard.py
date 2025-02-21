import streamlit as st
from Utils.data import *
import os
from st_aggrid import AgGrid , GridOptionsBuilder
from st_aggrid.shared import JsCode

from datetime import date

st.set_page_config(page_title='Tender Platform', page_icon='📑',layout='wide')


# Get Supabase URL and API key from environment

SUPABASE_URL = st.secrets['SUPABASE_URL'] 
SUPABASE_API_KEY = st.secrets['SUPABASE_API_KEY'] 


# SUPABASE_URL     = os.getenv("SUPABASE_URL")
# SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

st.header('Monitoring Tender Platform',divider=True)
## Side Bar

keywords = [    "Borehole", "Pump", "Solar", "Water treatment", "Chemical",
                "Pool", "Generator", "Wastewater", "Lawn Mower",
                "Effluent Treatment", "Irrigation", "Meter", "BMS", "Scada"
            ]
key_words = st.sidebar.multiselect(label='Key words',options=keywords,default=['Borehole'])

# Initialize the class
display_data = DisplayContractData(url=SUPABASE_URL, api_key=SUPABASE_API_KEY, key_words=key_words)

# Retrieve data from the database
data = display_data.select_data_from_db()


# Filter data based on keywords
filtered_data = display_data.filter_by_key_words()
filtered_data['created_at']   = pd.to_datetime(filtered_data['created_at']).dt.date
filtered_data                 = filtered_data[filtered_data['created_at']>=filtered_data['created_at'].max()]

# st.write(filtered_data)

filtered_data.reset_index(drop=True,inplace=True)
filtered_data['Public Url'] = 'https://tenders.go.ke/tenders/' + filtered_data['tender_id'].astype(str)
filtered_data = filtered_data[['published_date','tender_no','procument_method','procument_category','close_date','tender_fee','submission_method','Public Url','tender_title']]

filtered_data.rename(columns={'published_date':'Published Date','tender_no':'Tender No','procument_method':'Procument Method','close_date':'Close Date',\
                               'tender_fee':'Tender Fee','submission_method':'Submission Method','tender_title':'Description',\
                                   'procument_category':'Procument Category'},inplace=True)



gb = GridOptionsBuilder.from_dataframe(filtered_data)
gb.configure_default_column(

                            groupable=True,
                            value=True,
                            aggFunc='sum',
                            resizable =True,
                            filterable = True
                            
                            
                        )


gb.configure_column("Public Url",headerName="Url Link",width=100,
                    cellRenderer=JsCode("""
                        class UrlCellRenderer {
                        init(params) {
                            this.eGui = document.createElement('a');
                            this.eGui.innerText = 'Tender Link';
                            this.eGui.setAttribute('href', params.value);
                            this.eGui.setAttribute('style', "text-decoration:none");
                            this.eGui.setAttribute('target', "_blank");
                        }
                        getGui() {
                            return this.eGui;
                        }
                        }
                    """)
                )
### Build the final option object

gb.configure_column("Tender No",headerName="Tender No",width=50)

### Enable pagination
gb.configure_pagination(paginationAutoPageSize=True, paginationPageSize=10)
grid_options = gb.build()

### Render AgGrid
AgGrid(
            filtered_data,
            gridOptions=grid_options,
            height=min(1200, (len(filtered_data)) * 30),
            width='100%',
            allow_unsafe_jscode=True,
            heme='material', # options: streamlit, alpine, balham, material
        )



@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")

csv = convert_df(filtered_data)


if st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name="Tender.csv",
                mime="text/csv",
            ):
    st.success('Download successfully')