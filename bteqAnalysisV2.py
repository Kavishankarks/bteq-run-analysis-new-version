import pandas as pd
import re 
import streamlit as st
import numpy as np
import pandasql as psql
from streamlit_ace import st_ace
# import docs
# from docs import display_docs
# df = pd.read_csv("edw_sql_analysis - run5.csv")


# st.title("Analyzing BTEQ Run: A Comprehensive Evaluation of Results ")

st.set_page_config(
    page_title="IWX BTEQ Run Analysis",
    page_icon="https://aks-qa-540.infoworks.technology/assets/IWX_transp.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Tool to analyse the BTEQ Run report "
    }
)



def render_page(page):
    # Use the dictionary to call the function corresponding to the selected page
    pages[page]()

class Summary :
    def __init__(self,df):
        self.df = df
        
    def get_metadata_completed(self):
        return (self.df["metadata_build_status"] == "completed").sum()
    
    def get_metadata_failed(self):
        return (self.df["metadata_build_status"] == "failed").sum()
    
    def get_parse_completed(self):
        return (self.df["parse_status"] == "Success").sum()
    
    def get_parse_failed(self):
        return (self.df["parse_status"] == "Failed").sum()
        
    def get_import_completed(self):
        return (self.df["import_status"] == "Success").sum()
    
    def get_import_failed(self):
        return (self.df["import_status"] == "Failed").sum()
    
    def buildSummary(self):
        st.write("Summary")
        col1, col2, col3, col4= st.columns(4)
        col1.metric("Total SQL's : ",len(df))
        col2.metric("Parser Completed",self.get_parse_completed())
        col3.metric("SQL Import Completed",self.get_import_completed())
        col4.metric("Metadata Completed",self.get_metadata_completed())
        col2.metric("Parser Failed : " ,self.get_parse_failed())
        col3.metric("SQL Import Failed : ", self.get_import_failed())
        col4.metric("Total build failed : ", self.get_metadata_failed()) 
        
    def keyword_error(self):
        text_input = st.text_input("Search Error")
        if text_input and st.button("Submit") :     
            dff = df[df["error"] != None]
            errors = dff[dff["error"].str.contains(text_input,case=False)]
            st.write(errors)

    def search_target_table(self):
        unique_tables = {}
        for i in df["target_table"]:
            if i  not in unique_tables and type(i) == str:
                unique_tables[i] = 1
        selected_table = st.selectbox("Select table",unique_tables.keys())
        if st.button("Search table"):
            dff = df[df["target_table"] != None]
            
            target_table = dff[dff["target_table"].str.contains(selected_table,case=False)]
            metadata, parser , sqlimport = self.get_individual_table(target_table)
            st.write(target_table)
            st.write("\t\tParser Error",parser)
            st.write("\t\tSQL Import Error",sqlimport)
            st.write("\t\tMetadata Error",metadata)



    def extractSchemaTable(self,text):
        if(type(text) != str or "Cant" not in text) :
            return None
        pattern = r"schema:\s*(\w+)\s+and\s+table\s+name:\s*(\w+)"
        match = re.search(pattern, text)
        if match: 
            return "Schema : " + match.group(1) + " Table : " + match.group(2)
        else :
            return None

    def get_table_not_found(self):
        errors = df[df["import_status"]=="Failed"]
        tables_count = 0
        for i in errors["error"]:
            res = self.extractSchemaTable(i)
            if(res):
                tables_count += 1
                st.write(res)
        st.write("Total table count : ",tables_count)

    def get_individual_table(self, target_table):
        return (target_table["metadata_build_status"] == "failed").sum() , (target_table["parse_status"] == "Failed").sum(), (target_table["import_status"] == "Failed").sum()

    def get_table_completed(self,list_error):
        unique_tables = {}
        for i in df["target_table"]:
            if i  not in unique_tables and type(i) == str:
                unique_tables[i] = 1
        dff = df[df["target_table"] != None]
        dff.fillna("NA",inplace=True)
        fully_completed =0 
        cnt = 1
        for i in unique_tables.keys():
            target_table = dff[dff["target_table"] == i]
            metadata, parser , sqlimport = self.get_individual_table(target_table)
            if (metadata ==0 and parser ==0 and sqlimport ==0):
                st.write(str(cnt) + ". Table Name : " + i + " Total SQL's :  " + str(len(target_table))  + " Completed ✅ " )
                fully_completed += 1
            else :
                st.write(str(cnt) + ". Table Name : " + i )
                col1, col2, col3, col4, col5 = st.columns(5)
                col2.metric("Total SQL's ",len(target_table))
                col3.metric("Parser Error",parser)
                col4.metric("SQL Import Error",sqlimport)
                col5.metric("Metadata Error",metadata)
                if list_error:
                    st.write(target_table)
            cnt += 1
        st.subheader("Fully completed : " + str(fully_completed) + " out of : " + str(cnt))

    def get_jcl_completed(self,list_error):
        # compare_with_last = st.selectbox("Compare with last",("Yes","No"))
        # if compare_with_last == "Yes" :
        #     upload_last_file = st.file_uploader("Chosse last run report")
        #     last_run_df= pd.read_csv(upload_last_file)
        #     st.write(last_run_df)
        # else :
        unique_jcls = {}
        for i in df["jcl"]:
            if i  not in unique_jcls and type(i) == str:
                unique_jcls[i] = 1
        # st.write(unique_jcls.keys())
        # st.write(len(unique_jcls))
        dff = df[df["jcl"] != None]
        dff.fillna("NA",inplace=True)
        fully_completed =0 
        cnt = 1
        for i in unique_jcls.keys():
            target_jcl = dff[dff["jcl"] == i]
            metadata, parser , sqlimport = self.get_individual_table(target_jcl)
            if (metadata ==0 and parser ==0 and sqlimport ==0):
                st.subheader(str(cnt) + ". Table Name : " + i  + " Completed ✅ " )
                cola1, cola2 = st.columns(2)
                cola1.metric(" Total SQL's :  " , str(len(target_jcl)) )
                fully_completed += 1
            else :
                total_failed = metadata + parser + sqlimport
                st.subheader(str(cnt) + ". JCL : " + i )
                col1, col2, col3, col4, col5 = st.columns(5)
                col2.metric("Total SQL's ",len(target_jcl))
                col3.metric("Parser Error",parser)
                col4.metric("SQL Import Error",sqlimport)
                col5.metric("Metadata Error",metadata)
                if list_error:
                    st.write(target_jcl)
            cnt += 1
        st.subheader("Fully completed : " + str(fully_completed) + " out of : " + str(cnt))
    
    def error_display(self):
        tab1, tab2, tab3 = st.tabs(["Parser error","SQL Import error", "Metadata build error"])
       
        with tab1 :
            import_error = df[df["parse_status"]=="Failed"]
            st.write(import_error)
        with tab2 :
            parser_error = df[df["import_status"]=="Failed"]
            st.write(parser_error)
        with tab3:
            metadata_error = df[df["metadata_build_status"]=="failed"]
            st.write(metadata_error)
   
class preProcessData :
    def __init__(self,df) -> None:
        self.actual_columns  = ['jcl', 'control_card', 'sql_liness', 'sql_number', 'query_type',
       'parse_status', 'table_mode', 'target_table', 'dependent_tables',
       'pipelineid', 'import_status', 'metadata_build',
       'metadata_build_status', 'error']
        self.actual_columns_next = [ 'file_name', 'sql_liness', 'sql_number', 'query_type',
       'parse_status', 'table_mode', 'target_table', 'dependent_tables',
       'pipelineid', 'import_status', 'metadata_build',
       'metadata_build_status', 'error'
        ]
        self.current_columns = df.columns
        self.df = df
        
    def update_columns_names(self) :
        if (len(self.df.columns) == 15) :
            self.df = self.df.drop(df.columns[-1], axis=1)
            self.current_columns = self.df.columns
        if(len(self.current_columns)== len(self.actual_columns) ):
            try :
                self.df = self.df.rename(columns = dict(zip(self.current_columns, self.actual_columns)))
            except :
                st.exception("Column count mismatch")
        else :
            # if "file" in self.df.columns :

            try :
                self.df = self.df.rename(columns = dict(zip(self.current_columns, self.actual_columns_next)))
            except :
                st.exception("Column count mismatch")
        
        if("file_name" in self.df.columns) :
                self.df[["jcl","control_card"]] = self.df["file_name"].str.rsplit('/',n=1,expand=True)
                self.df.drop("file_name", axis=1, inplace=True)
                self.df.insert(0, 'control_card', self.df.pop('control_card'))
                self.df.insert(0, 'jcl', self.df.pop('jcl'))
        return self.df
    
    def replace_nan_with_na(self):
        self.df.fillna("NA",inplace=True)

class JiraMapping :
    def __init__(self,df_mapping) -> None :
        self.actual_columns = ["jira_id","error"]
        self.current_columns = df_mapping.columns
        self.df_mapping = df_mapping

    def update_column_names(self) :
        if(len(self.current_columns)== len(self.actual_columns) ):
            try :
                self.df_mapping = self.df_mapping.rename(columns = dict(zip(self.current_columns, self.actual_columns)))
            except :
                st.exception("Column count mismatch")
        return self.df_mapping
def display_docs():
    """
    Displays documentation for your Streamlit app.
    """
    st.title('Documentation')

    st.header('Introduction')
    st.write('Welcome to my Streamlit app! This app allows you to ...')

    st.header('Usage')
    st.write('To use this app, simply ...')

    st.header('FAQ')
    st.write('Q: What do I do if ...')
    st.write('A: You can ...')

    st.header('Contact')
    st.write('If you have any questions or feedback, please contact us at ...')

pages = {
    "Documentation" : display_docs
}
with st.sidebar:
    if st.sidebar.button('Documentation'):
        render_page(display_docs)
    select_screen = st.sidebar.selectbox("Option", ("BTEQ Run Analysis","Compare two BteqRun Reports","Error Level Analysis"))
uploaded_file = st.file_uploader("Choose a file")


if select_screen == "BTEQ Run Analysis" :
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        preprocess = preProcessData(df)
        df = preprocess.update_columns_names()
        preprocess.replace_nan_with_na()
        st.title("Run report")
        st.write(df)
        # Execute the SQL query on the DataFrame
        summary = Summary(df)
        summary.buildSummary()
        sql_code = """
        SELECT *
        FROM my_table
        WHERE column_name = 'value'
        """

        # Create the text_area with the Ace editor
        sql_code = st_ace(
            value=sql_code,
            language="sql",
            theme="chrome",
            height=400,
            font_size=14,
            keybinding="vscode",
            placeholder="Enter SQL code here...",
        )

        # Display the SQL code
        st.write("SQL code:")
        st.code(sql_code, language="sql")
        # sql_query = st.text_area('Enter SQL query:')
        if st.button("Submit"):
            try:
                result = psql.sqldf(sql_code)
                # Display the results
                st.title("SQL Query Results")
                st.write(result)
            except Exception as e:
                st.write('Invalid SQL query',e)
        summary.error_display()
        summary.keyword_error()
        summary.search_target_table()
        s = st.checkbox("List errors")
        if st.button("Get table analysis") :
            summary.get_table_completed(s)
        if st.button("Get JCL analysis") :
            summary.get_jcl_completed(s)
        uploaded_jira_mapping = st.file_uploader("Chose Jira Mapping ")
        if st.button("Get All Tables Not Found"):
            summary.get_table_not_found()
        if uploaded_jira_mapping is not None :
                df_jira = pd.read_csv(uploaded_jira_mapping)
                # df_jira.columns = df_jira.columns.str.lower().str.replace(' ', '_')
                jiramap = JiraMapping(df_jira)
                df_jira = jiramap.update_column_names()
                df_jira["error"] = df_jira["error"].str.replace('""',"")
                dff = df[df["target_table"] != None]
                dff.fillna("NA",inplace=True)
                dff["error"] = dff["error"].str.replace('""',"")
                cnt =0
                for i in df_jira["error"] :
                    cnt += 1
                    try :
                        error_df = dff[dff["error"] == i]
                        if(not error_df.empty):
                            st.write(df_jira["jira_id"][cnt])
                            st.write(error_df)
                    except Exception as e :
                        st.exception(f'unknown exception {e}') 
        # st.write("sd")


elif(select_screen=="Compare two BteqRun Reports") :
     if uploaded_file is not None:
        st.write("Compare two Bteq")
        uploaded_file_second = st.file_uploader("Choose a compare file")
        df1 = pd.read_csv(uploaded_file)
        if uploaded_file_second :
            df2 = pd.read_csv(uploaded_file_second)

            #preprocess both files
            preprocess_df1 = preProcessData(df1)
            df1 = preprocess_df1.updateColumnsNames()
            preprocess_df1.replace_nan_with_na()
            
            preprocess_df2 = preProcessData(df2)
            df2 = preprocess_df2.updateColumnsNames()
            preprocess_df2.replace_nan_with_na()

            if(len(df1) == len(df2)) :
                if df1.equals(df2):
                    st.write("The two DataFrames are identical.")
                else :
                    st.write("Comparing the Run files")
            else :
                st.write("Not able to compare because of missmatch in file sizes")

elif select_screen == "Error Level Analysis" :
     if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write('Original DataFrame:')
        st.write(df.columns)

        # Allow the user to edit the dataframe
        edited_df = st.experimental_data_editor(df) # 👈 An editable dataframe
        st.write(edited_df)
        # favorite_command = edited_df.loc[edited_df["rating"].idxmax()]["command"]
        # st.markdown(f"Your favorite command is **{favorite_command}** 🎈")
        
