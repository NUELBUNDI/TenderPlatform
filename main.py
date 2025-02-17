import streamlit as st 


dashboard = st.Page(
    "Contracts/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True
)




pg = st.navigation(
        {
            "Account": [dashboard],

        }
    )

pg.run()