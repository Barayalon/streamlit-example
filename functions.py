import os
import openai
import tiktoken

openai.api_key = os.environ['OPENAI_API_KEY']

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
    messages = [{'role': 'system', 'content': "You are an English teacher. You are checking your student's answers on an assay exam, this is the assay:" + sources +"this is the question:"+question+"The answer is provided by the student. You need to check if the student answered correctly, if not give the correct answer with an explanation. Refer to the student's vocabulary, grammar and spelling if applicable"},
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