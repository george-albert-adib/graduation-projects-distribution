# -*- coding: utf-8 -*-
"""
Created on Sun Sep 28 23:05:36 2025

@author: George Albert
"""

import re
from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import pandas as pd

def extract_text_from_pdf(pdf_path):
    """
    Extracts text content from a PDF file.
    """
    output_string = StringIO()
    with open(pdf_path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
    return output_string.getvalue()

def get_transcript_info(pdf_path):
    """
    Extracts Student ID and final cumulative grades from the transcript text.
    """
    text = extract_text_from_pdf(pdf_path)

    # 1. Extract Student ID
    # Pattern looks for "Student ID: " followed by 7 digits
    student_id_match = re.search(r"Student ID:\s*(\d{7})", text)
    student_id = student_id_match.group(1) if student_id_match else "Not Found"

    # 2. Extract Final Cumulative Data
    # The final cumulative data is typically on the last page.
    # The last block of cumulative data appears just before "Issued Via" on the last page.
    # We can search for the last occurrence of the key phrases.

    # Pattern for Cumulative Credit Hours
    credit_hours_match = re.findall(r"Cumulative Credit Hours:\s*(\d+)", text)
    final_credit_hours = credit_hours_match[-1] if credit_hours_match else "Not Found"

    # Pattern for Cumulative Course Points
    course_points_match = re.findall(r"Cumulative Course Points:\s*(\d+\.?\d*)", text)
    final_course_points = course_points_match[-1] if course_points_match else "Not Found"

    # Pattern for Cumulative GPA
    gpa_match = re.findall(r"Cumulative GPA:\s*(\d+\.?\d*)", text)
    final_gpa = gpa_match[-1] if gpa_match else "Not Found"

    # Pattern for Passed Hours
    passed_hours_match = re.findall(r"Passed Hours:\s*(\d+)", text)
    final_passed_hours = passed_hours_match[-1] if passed_hours_match else "Not Found"

    # Pattern for Training Weeks
    training_weeks_match = re.findall(r"Training Weeks:\s*(\d+/\d+)", text)
    final_training_weeks = training_weeks_match[-1] if training_weeks_match else "Not Found"


    return {
        "Student ID": student_id,
        "Cumulative Credit Hours": final_credit_hours,
        "Cumulative Course Points": final_course_points,
        "Cumulative GPA": final_gpa,
        "Passed Hours": final_passed_hours,
        "Training Weeks": final_training_weeks
    }

# --- Usage Example ---
# Assuming the file is named 'credit_transcript_2100905.pdf'
file_path = 'credit_transcript_2002296.pdf' 

import os

# giving directory name
dirname = 'E:\\ASU\\Admin\\Graduation Projects Distribution\\Transcripts'

# giving file extension
ext = ('.pdf')

counter = 0
outputs = pd.DataFrame(columns=["user_id","cumulative_grades","cumulative_GPA"], index=range(len(os.listdir(dirname))))

# iterating over all files
for files in os.listdir(dirname):
    if files.endswith(ext):
        file_path = os.path.join(dirname, files)
        try:
            results = get_transcript_info(file_path)
        
            # print(f"--- Extracted Transcript Information for {file_path} ---")
            # print(f"Student ID: {results['Student ID']}")
            # print("-" * 30)
            # print("Final Cumulative Data:")
            # print(f"  Cumulative Credit Hours: {results['Cumulative Credit Hours']}")
            # print(f"  Cumulative Course Points: {results['Cumulative Course Points']}")
            # print(f"  Cumulative GPA: {results['Cumulative GPA']}")
            # print(f"  Passed Hours: {results['Passed Hours']}")
            # print(f"  Training Weeks: {results['Training Weeks']}")
            outputs.loc[counter] = pd.Series({"user_id":results['Student ID'], "cumulative_grades":results['Cumulative Course Points'], "cumulative_GPA":results['Cumulative GPA']})
            counter += 1
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
            
outputs.to_csv("parsed_transcripts")