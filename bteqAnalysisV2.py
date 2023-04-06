import pandas as pd
import re 
import streamlit as st
import numpy as np
# df = pd.read_csv("edw_sql_analysis - run5.csv")


st.title("Analyzing BTEQ Run: A Comprehensive Evaluation of Results ")

class Summary :
    def __init__(self,df):
        self.df = df
        
    def get_metadata_completed(self):
        return (self.df["metadata_job_status"] == "completed").sum()
    
    def get_metadata_failed(self):
        return (self.df["metadata_job_status"] == "failed").sum()
    
    def get_parse_completed(self):
        return (self.df["parse_status"] == "Success").sum()
    
    def get_parse_failed(self):
        return (self.df["parse_status"] == "Failed").sum()
        
    def get_import_completed(self):
        return (self.df["sql_import"] == "Success").sum()
    
    def get_import_failed(self):
        return (self.df["sql_import"] == "Failed").sum()
    
    def buildSummary(self):
        st.write("Total number of SQL's : ", len(df))
        st.write("Total build completed :" , self.get_metadata_completed())
        st.write("Total build failed : ", self.get_metadata_failed()) 
        st.write("Parser complete : " , self.get_parse_completed()) 
        st.write("Parser Failed : " ,self.get_parse_failed())
        st.write("SQL Import complete : " ,self.get_import_completed()) 
        st.write("SQL Import Failed : ", self.get_import_failed())
        
    def keyword_error(self):
        text_input = st.text_input("Search Error")
        if text_input and st.button("Submit") :     
            dff = df[df["error"] != None]
            dff.fillna("NA",inplace=True)
            errors = dff[dff["error"].str.contains(text_input,case=False)]
            st.write(errors)

    def search_target_table(self):
        unique_tables = {}
        for i in df["target_table_name"]:
            if i  not in unique_tables and type(i) == str:
                unique_tables[i] = 1
        selected_table = st.selectbox("Select table",unique_tables.keys())
        if st.button("Search table"):
            dff = df[df["target_table_name"] != None]
            dff.fillna("NA",inplace=True)
            target_table = dff[dff["target_table_name"].str.contains(selected_table,case=False)]
            metadata, parser , sqlimport = self.get_individual_table(target_table)
            st.write(target_table)
            st.write("\t\tMetadata Error",metadata)
            st.write("\t\tParser Error",parser)
            st.write("\t\tSQL Import Error",sqlimport)



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
        errors = df[df["sql_import"]=="Failed"]
        tables_count = 0
        for i in errors["error"]:
            res = self.extractSchemaTable(i)
            if(res):
                tables_count += 1
                st.write(res)
        st.write("Total table count : ",tables_count)

    def get_individual_table(self, target_table):
        return (target_table["metadata_job_status"] == "failed").sum() , (target_table["parse_status"] == "Failed").sum(), (target_table["sql_import"] == "Failed").sum()

    def get_table_completed(self):
        unique_tables = {}
        for i in df["target_table_name"]:
            if i  not in unique_tables and type(i) == str:
                unique_tables[i] = 1
        dff = df[df["target_table_name"] != None]
        dff.fillna("NA",inplace=True)
        fully_completed =0 
        cnt = 1
        for i in unique_tables.keys():
            target_table = dff[dff["target_table_name"] == i]
            metadata, parser , sqlimport = self.get_individual_table(target_table)
            if (metadata ==0 and parser ==0 and sqlimport ==0):
                st.write(str(cnt) + ". Table Name : " + i + " Total SQL's :  " + str(len(target_table))  + " Completed ✅ " )
                fully_completed += 1
            else :
                total_failed = metadata + parser + sqlimport
                st.write(str(cnt) + ". Table Name : " + i +  " Total SQL's :  " + str(len(target_table)) + " Failed : " + str(total_failed))
                st.write("Metadata Error",metadata)
                st.write("Parser Error",parser)
                st.write("SQL Import Error",sqlimport)
            cnt += 1
        st.subheader("Fully completed : " + str(fully_completed) + " out of : " + str(cnt))

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
	df = pd.read_csv(uploaded_file)
	df.columns = df.columns.str.lower().str.replace(' ', '_')
	st.title("Run report")
	st.write(df)
	summary = Summary(df)
	summary.buildSummary()
	if st.button("Get All parser error"):
		parser_error = df[df["parse_status"]=="Failed"]
		st.write(parser_error)
	if st.button("Get All SQL Import error"):
		import_error = df[df["sql_import"]=="Failed"]
		st.write(import_error)
	if st.button("Get All Metadata build error"):
		metadata_error = df[df["metadata_job_status"]=="failed"]
		st.write(metadata_error)
	if st.button("Get All Tables Not Found"):
		summary.get_table_not_found()
	summary.keyword_error()
	summary.search_target_table()
	if st.button("Get table analysis") :
		summary.get_table_completed()
       
	st.write("\n\n🔄  Mapping error for jira is in progress 🔄")
    # st.write("sd")
	