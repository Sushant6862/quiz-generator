
import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file,extract_mcqs,create_mcq_dataframe
import streamlit as st
from langchain.callbacks import get_openai_callback
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain
from src.mcqgenerator.logger import logging

#loading json file

with open('D:\mcqgen\Responce.json', 'r') as file:
    RESPONSE_JSON = json.load(file)

#creating a title for the app
st.title("MCQs Creator Application with LangChain 🦜⛓️")

#Create a form using st.form
with st.form("user_inputs"):
    #File Upload
    uploaded_file=st.file_uploader("Uplaod a PDF or txt file")

    #Input Fields
    mcq_count=st.number_input("No. of MCQs", min_value=3, max_value=50)

    #Subject
    subject=st.text_input("Insert Subject",max_chars=20)

    # Quiz Tone
    tone=st.text_input("Complexity Level Of Questions", max_chars=20, placeholder="Simple")

    #Add Button
    button=st.form_submit_button("Create MCQs")

    # Check if the button is clicked and all fields have input

    if button and uploaded_file is not None and mcq_count and subject and tone:
        with st.spinner("loading..."):
            try:
                text=read_file(uploaded_file)
                #Count tokens and the cost of API call
                with get_openai_callback() as cb:
                    response=generate_evaluate_chain(
                        {
                        "text": text,
                        "number": mcq_count,
                        "subject":subject,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON)
                            }
                    )
                #st.write(response)

            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("Error")

            else:
                print(f"Total Tokens:{cb.total_tokens}")
                print(f"Prompt Tokens:{cb.prompt_tokens}")
                print(f"Completion Tokens:{cb.completion_tokens}")
                print(f"Total Cost:{cb.total_cost}")
                if isinstance(response, dict):
                    #Extract the quiz data from the response
                    quiz=response.get("quiz", None)
                    


                    # Step 1: Split the string into lines
                    lines = quiz.splitlines()

                    # Step 2: Initialize variables
                    mcq_dict = {}
                    current_mcq = {}
                    current_question = None

                    # Step 3: Loop through the lines and extract information
                    for line in lines:
                        line = line.strip()
                        
                        if line.startswith('"mcq":'):
                            current_question = line.split(':', 1)[1].strip().strip('",')
                            current_mcq['mcq'] = current_question
                            
                        elif line.startswith('"options":'):
                            current_mcq['options'] = {}
                        
                        elif '"a":' in line or '"b":' in line or '"c":' in line or '"d":' in line:
                            option_key, option_value = line.split(':', 1)
                            option_key = option_key.strip().strip('",')
                            option_value = option_value.strip().strip('",')
                            current_mcq['options'][option_key] = option_value
                        
                        elif line.startswith('"correct":'):
                            correct_answer = line.split(':', 1)[1].strip().strip('",')
                            current_mcq['correct'] = correct_answer
                            mcq_dict[len(mcq_dict) + 1] = current_mcq
                            current_mcq = {}

                    # # Step 4: Output the structured data
                    # import pprint
                    # pprint.pprint(mcq_dict)

                    if mcq_dict is not None:
                        df=create_mcq_dataframe(mcq_dict)
                        df.index=df.index+1
                        st.table(df)
                        #Display the review in atext box as well
                        st.text_area(label="Review", value=response["review"])
                       
                        

                    else:
                     st.write(response)
