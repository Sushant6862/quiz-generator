
import os
import PyPDF2
import json
import traceback
import pandas as pd

def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader=PyPDF2.PdfFileReader(file)
            text=""
            for page in pdf_reader.pages:
                text+=page.extract_text()
            return text
            
        except Exception as e:
            raise Exception("error reading the PDF file")
        
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    
    else:
        raise Exception(
            "unsupported file format only pdf and text file suppoted"
            )

# def get_table_data(quiz_str):
#     try:
#         # convert the quiz from a str to dict
#         quiz_dict=json.loads(quiz_str)
#         quiz_table_data=[]
        
#         # iterate over the quiz dictionary and extract the required information
#         for key,value in quiz_dict.items():
#             mcq=value["mcq"]
#             options=" || ".join(
#                 [
#                     f"{option}-> {option_value}" for option, option_value in value["options"].items()
                 
#                  ]
#             )
            
#             correct=value["correct"]
#             quiz_table_data.append({"MCQ": mcq,"Choices": options, "Correct": correct})
        
#         return quiz_table_data
        
#     except Exception as e:
#         traceback.print_exception(type(e), e, e.__traceback__)
#         return False

def extract_mcqs(input_string):
    # Remove the introductory text and get the relevant part
    mcq_text = input_string.split('\n\n', 1)[1]
    
    # Initialize an empty dictionary to store the MCQs
    mcqs = {}
    
    # Split the string into individual MCQ blocks
    mcq_blocks = mcq_text.split('},\n\n')
    
    for block in mcq_blocks:
        # Extract the question number
        question_num = block.split(':', 1)[0].strip('"{')
        
        # Extract the MCQ question
        mcq_start = block.find('"mcq": "') + len('"mcq": "')
        mcq_end = block.find('", "options"')
        mcq_question = block[mcq_start:mcq_end]
        
        # Extract the options
        options_start = block.find('"options": {') + len('"options": {')
        options_end = block.find('}, "correct"')
        options_string = block[options_start:options_end]
        
        options = {}
        option_pairs = options_string.split(', ')
        for pair in option_pairs:
            if '": "' in pair:
                key, value = pair.split('": "', 1)
                key = key.strip('"')
                value = value.strip('"')
                options[key] = value
        
        # Extract the correct answer
        correct_start = block.find('"correct": "') + len('"correct": "')
        correct_end = block.rfind('"')
        correct_answer = block[correct_start:correct_end]
        
        # Store the extracted information in the dictionary
        mcqs[question_num] = {
            'question': mcq_question,
            'options': options,
            'correct_answer': correct_answer
        }
    
    return mcqs




def create_mcq_dataframe(mcqs):
    flattened_data = []
    for num, mcq in mcqs.items():
        row = {
            'question_number': num,
            'question': mcq['mcq'],  # Update to access 'mcq' instead of 'question'
            'correct_answer': mcq['correct']  # Update to access 'correct' instead of 'correct_answer'
        }
        for option, text in mcq['options'].items():
            row[f'option_{option}'] = text
        flattened_data.append(row)
    
    return pd.DataFrame(flattened_data)