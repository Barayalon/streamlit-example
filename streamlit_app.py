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
      for i, message in enumerate(st.session_state.chat_history):
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
    messages = [{'role': 'system', 'content': "אתה מורה לאנגלית. You are checking your student's answers on an assay exam, this is the assay:" + sources +"this is the question:"+question+"The answer is provided by the student. You need to check if the student answered correctly, if not give the correct answer with an explanation. Refer to the student's vocabulary, grammar and spelling if applicable. if the question is multiple choices check if the answer is correct and if not tell the student to try again.התלמיד שלך מדבר עיברת, הוא יבין יותר טוב אם תענה בעיברית"},
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
  

def gpt_4_raw_text(topic):
  model = "gpt-4"
  openai.api_key = os.environ["OPENAI_API_KEY"]
  topic = str(topic)
  topic = topic.replace('\\n','')
  messages= [{'role' : 'system', 'content': """You are a private english totur and you need to write an assay based on the topic provided by the student, thisis an example assay: WATER FROM AIR

I It is no secret that the climate is changing throughout the world and less rain is falling in many
places. This is causing a shortage of drinking water worldwide. This situation is made worse by the
increasing world population. Fortunately, new sources are being developed, including methods that
actually take water out of the air. It may sound like magic, but it is already being done.
II The Canadian WaterMill Company has a device that first extracts water from the air and then
purifies it, so it is safe to drink. WaterMill's director claims their product is environmentally friendly and
can work in humid, tropical areas, such as rainforests, as well as in dry regions, like deserts. However,
this technology does not produce large amounts of water at any one time, it is quite expensive and uses
a lot of electricity. There is a similar device being developed by American scientists that does the same
as the Canadian device but it doesn't use electricity at all.
III An Israeli company has also recently developed a device that produces drinking water from air.
This product comes in three sizes, including a small unit for a home or an office. It works best in humid
environments although it can produce water in dry regions as well. It needs to be plugged into an
electricity supply but the company also makes a device that operates on batteries for use in rural areas
or in emergency situations.
IV A recent report from the United Nations (UN) says that 20% of the world's population lives in
underdeveloped areas, where water sources are limited. This lack of clean water severely affects people's
lives in those regions. It is the major cause of disease, child mortality and starvation. It has also caused
wars in the past and probably will again in the future unless this problem is solved.
V While scientists are developing new methods to extract water from the air, there are additional ways
of obtaining drinking water. Many countries have huge desalination plants, which convert sea water
to fresh water. Another way of producing drinking water is the purification of sewage and turning it into
clean water. Astronauts rely on this solution when in outer space. Hopefully, all these methods will help
end the worldwide shortage of clean drinking water."""},
        {'role': 'user', 'content': "this is my topic:"+ topic}]
  response = openai.ChatCompletion.create(
    model= "gpt-4",
    messages= messages,
    temperature=0,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0)
  return response["choices"][0]["message"]["content"]


def main():
    st.header("Class AI",)
    st.session_state.question_num = 0
      
    st.write('## 1. Enter your OpenAI API key')
    st.text_input('OpenAI API key', type='password', key='api_key', on_change=on_api_key_change, label_visibility="collapsed")
    st.write(os.environ['OPENAI_API_KEY'])
      
    if "conversation" not in st.session_state:
      st.session_state.conversation = None
    if "new_exam" not in st.session_state:
      st.session_state.new_exam = None
    if "article" not in st.session_state:
      st.session_state.article = None
    if "question_num" not in st.session_state:
      st.session_state.question_num = int(0)
    if "question" not in st.session_state:
      st.session_state.question = None
    if "chat_history" not in st.session_state:
      st.session_state.chat_history = None

    st.header("Answer the questions on your data :books:")
    
    with st.sidebar:
      st.subheader("Your documents")
      topic = st.text_input("What topic would like to write an exam about?")
      if st.button("Generate Exam"):
        with st.spinner("Processing"):
                    #text on topic
                    raw_text = gpt_4_raw_text(topic)
                    # new exam
                    new_exam = answer_query_gpt_16k_bagrut(prompt.example_questions,raw_text)
                    # list questions
                    st.session_state.new_exam = new_exam.strip().split('\n\n')
                    # define the article as part of the environment 
                    st.session_state.article = raw_text
                    # define the question number
                    st.session_state.question_num = int(1)
            
      st.session_state.question = st.radio("Exam questions", st.session_state.new_exam, index = 1)
      st.text_area("Question nu st.session_state.questionmber", value =  st.session_state.question)

      
      #if st.session_state.question.find('Multiple') > -1:
        #user_question = st.radio("choose your answer", st.session_state.question.strip().split('\n'))
      #else:
        #user_question = st.text_input("Write the answer to the question")
      

    user_question = st.text_input("Write the answer to the question")

    if st.session_state.question:
        if user_question:
          question_num = st.session_state.question_num
          handle_answer(user_question,st.session_state.question)

        else:
          #question_num = st.session_state.question_num
          question = st.session_state.question
          question = str(question)
          question = question.replace("\n","<br/>")
          st.write(bot_template.replace(
                      "{{MSG}}", question), unsafe_allow_html=True)


            
      #Add an expander for article view
    if st.session_state.article:
      expander = st.expander("Article text")
      expander.write(st.session_state.article)


              






if __name__ == '__main__':
    main()
