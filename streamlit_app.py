__version__ = "0.0.0.1"
app_name = "Build my exam"

import streamlit as st
import os
from PyPDF2 import PdfReader
import openai
import prompt
import openai
import tiktoken
from htmlTemplates import css, bot_template, user_template


st.set_page_config(layout='centered', page_title=f'{app_name} {__version__}')
ss = st.session_state


#User's API key to OpenAI
def on_api_key_change():
	api_key = ss.get('api_key') or os.getenv('OPENAI_API_KEY')
	os.environ['OPENAI_API_KEY'] = api_key
    

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def handle_answer(answer,question):
    st.session_state.chat_history = question
    history = [st.session_state.chat_history]
    sources = st.session_state.article
    response = check_answers(question,answer,sources)
    st.session_state.chat_history = history.extend([answer,response])

    if history:
      for i, message in enumerate(history):
          message = message.replace("\n","<br/>")
          if i % 2 == 0:
              st.write(bot_template.replace(
                  "{{MSG}}", message), unsafe_allow_html=True)
          else:
              st.write(user_template.replace(
                  "{{MSG}}", message), unsafe_allow_html=True)
    else:
       st.write(bot_template.replace(
                  "{{MSG}}", question), unsafe_allow_html=True)
       st.write([st.session_state.chat_history,answer,response,history])

def convert_list_to_text(lst):
    text = ' '.join(lst)
    return text

def choose_files(files,question):
  

  response = openai.Completion.create(
    model= "text-davinci-003",
    prompt= "these are the list of files available:"+files+"you need to answer this question:"+question+"return a python list seperated by comma of files names that are the most relevant for the question. You have a limit of four files",
    temperature=0,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0)
  choices =response['choices']
  return choices[0]['text']

def str_list(string):
  item_list = string.split(",")
  return item_list

def answer_query_source(query,source):
  

  response = openai.Completion.create(
    model= "text-davinci-003",
    prompt= "use the source: "+source+"to answer this query"+query+". Return a pythno list of the results. If you can't answer the query return: 'I counld not answer the query with the given information.'",
    temperature=0,
    max_tokens=1500,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0)
  choices =response['choices']
  return choices[0]['text']

def utf16_to_unicode(utf16_string):
    # Convert the string from Unicode to UTF-16
    utf16_bytes = utf16_string.encode('utf-16')

    # Decode the UTF-16 bytes to Unicode
    return utf16_bytes.decode('utf-16')



def dict_to_string(data):
  data = data
  string = ""
  for dictionary in data:
    for key in dictionary:
      string += f"{key}: {dictionary[key]}\n"
    string += "\n"
  return string

example_dict = [{'role' : 'system', 'content': 'You are a business development analyst in a major biotech company. You perform analysis on the data provided to you and previous data according to relevant queries.'},
        {'role': 'user', 'content': "Use the sources to answer this query: " }]

string = dict_to_string(example_dict)
print(string)

def data_to_string(data):
  data = data
  string = ""
  for dictionary in example_dict:
    for key in dictionary:
      string += f"{key}: {dictionary[key]}\n"
    string += "\n"

def answer_query_gpt_16k_bagrut(exam,sources):
  model = "gpt-3.5-turbo-16k"
  openai.api_key = os.environ['OPENAI_API_KEY']
  exam = exam.replace('\\n','')
  sources = str(sources)
  sources = sources.replace('\\n','')
  messages= [{'role' : 'system', 'content': 'You are a pritvate english tutor. You need to wirte questions to prepare your student based on this exam:' + exam +'the questions are based on the students intresets, his intrests are provided by student'},
        {'role': 'user', 'content': "I am your student please prepare an exam based in these sources:"+sources}]
  response = openai.ChatCompletion.create(
    model= "gpt-3.5-turbo-16k",
    messages= messages,
    temperature=0,
    max_tokens = 16383 - (num_tokens_from_string(dict_to_string(messages),model)),
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0)
  choices =response['choices']
  return response['choices'][0]['message']['content']


encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
def num_tokens_from_string(string: str, model_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def check_answers(question, answer, sources):
    # Set the specific GPT-3 model to be used
    model = "gpt-3.5-turbo-16k"

    # Set the OpenAI API key for authentication
    openai.api_key = os.environ['OPENAI_API_KEY']
    # Convert the question to a string and remove any newline characters
    question = str(question)
    question = question.replace('\\n','')

    # Convert the answer to a string and remove any newline characters
    answer = str(answer)
    answer = answer.replace('\\n','')

    # Convert the sources to a string and remove any newline characters
    sources = str(sources)
    sources = sources.replace('\\n','')

    # Define the messages for the chat-based API call
    messages = [{'role': 'system', 'content': "You are an English teacher. You are checking your student's answers on an assay exam, this is the assay:" + sources +"this is the question:"+question+"The answer is provided by the student. You need to check if the student answered correctly, if not give the correct answer with an explanation. Refer to the student's vocabulary, grammar and spelling if applicable. if the question is multiple choices check if the answer is correct and if not tell the student to try again"},
                {'role': 'user', 'content': "I am your student please review my answer:"+answer}]

    # Call the OpenAI Chat Completion API to generate a response
    response = openai.ChatCompletion.create(
        model= "gpt-3.5-turbo-16k",
        messages= messages,
        temperature=0,
        max_tokens = 16383 - (num_tokens_from_string(dict_to_string(messages),model)),
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0)

    # Extract the response choices from the API response
    choices = response['choices']

    # Return the content of the first message in the response choices
    return response['choices'][0]['message']['content']


def main():
    st.session_state.question_num = 0
    if not(os.environ['OPENAI_API_KEY']):
      st.write('## 1. Enter your OpenAI API key')
      st.text_input('OpenAI API key', type='password', key='api_key', on_change=on_api_key_change, label_visibility="collapsed")
      st.write(os.environ['OPENAI_API_KEY'])
    
    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "new_exam" not in st.session_state:
        st.session_state.new_exam = None
    if "article" not in st.session_state:
        st.session_state.article = None
    st.header("Answer the questions on your data :books:")

    if st.session_state.article:

      user_question = st.text_input("are you ready to start?")

      if st.button("Next Question"):
        question_num = st.session_state.question_num
        next_question = 1+ question_num
        st.session_state.question_num = 1+ question_num
        
        if user_question:
          question_num = st.session_state.question_num
          handle_answer(user_question,st.session_state.new_exam[question_num])
        else:
          question = st.session_state.new_exam[1]
          question = question.replace("\n","<br/>")
          st.write(bot_template.replace(
                  "{{MSG}}", question), unsafe_allow_html=True)

    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", accept_multiple_files=True)
        if st.button("Generate Exam"):
             with st.spinner("Processing"):
                  # get pdf text
                  raw_text = get_pdf_text(pdf_docs)
                  # new exam
                  new_exam = answer_query_gpt_16k_bagrut(prompt.example_questions,raw_text)
                  # list questions
                  st.session_state.new_exam = new_exam.strip().split('\n\n')
                  # define the article as part of the environment 
                  st.session_state.article = raw_text
                  # define the question number
                  st.session_state.question_num = 1
        if st.session_state.article:
           st.text_area("Exam questions", value =st.session_state.new_exam)





if __name__ == '__main__':
    main()