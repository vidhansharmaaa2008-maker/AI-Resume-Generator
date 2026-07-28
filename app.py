import streamlit as st
# streamlit: web based app making
# lite python framework
st.title("AI Resume maker")

st.markdown("""## User can create 
or download AI created resume
based on high ATS score""")


#============AGENT CODE=============

import os
import time
import langchain
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
import pytesseract as pyt
from tavily import TavilyClient
from langchain.messages import SystemMessage, HumanMessage
import numpy as np
import streamlit as st
from langchain_community.document_loaders import PyMuPDFLoader
from PIL import Image

#===============API KEY LOAD================
GOOGLE_API_KEY = st.sidebar.text_input("GOOGLE_API_KEY",type="password")
GROQ_API_KEY = st.sidebar.text_input("GROQ_API_KEY",type="password")
TAVILY_API_KEY = st.sidebar.text_input("TAVILY_API_KEY",type="password")

if not (GOOGLE_API_KEY) and not (GROQ_API_KEY) and not (TAVILY_API_KEY):
    st.sidebar.warning("PASS API KEYS")
    st.stop()
else:
    st.success("API KEYS LOADED")

model = ChatGoogleGenerativeAI(
    model='gemini-3.5-flash',
    google_api_key = GOOGLE_API_KEY
)

# tool
def search_recent_news_jobs(query):
  """This function helps to search
  recent news to given search query
  suppose user write Python Developer
  jobs it should return trending news and jobs links"""
  client = TavilyClient(
      api_key = TAVILY_API_KEY
  )
  result = client.search(query)



# agent creation
from langchain.agents import create_agent

agent = create_agent(
    model= model,
    tools = [search_recent_news_jobs]
)
agent



#===========PROMPT GENERATOR=================
def prompt_generator(agent):
  """This function help to give detailed prompt
  followed by chain of thoughts and persona
  based prompting, main task is to give detained
  prompt build Resume for students or experienced person
  based on their given personal information.
  """

  prompt= """you are a senior HR resume analyzer,
  main task is to give detailed prompt to build
  Resume for students or experienced person
  based on their given personal information.
  System Instrution I want Model to generate resume
  in HTML format, include that in prompt"""


  response = agent.invoke(prompt)
  file_name = 'prompt.py'
  with open(file_name, 'w') as f:
    f.write(response.content[-1]['text'])
  return "Prompt file generated successfully, agent can read it"
    
prompt_generator(model)

# tool 2
def resume_maker_prompt():
  """This function just gives 
 updated prompt for model"""

  with open('prompt.py', 'r') as f:
    prompt = f.read()
  return prompt

resume_maker_prompt()
#===================UPLOAD IMAGE===================>
uploaded_file=st.sidebar.file_uploader(
    "Choose an image file",
    type=["jpg", "jpeg", "png", "webp"]
)
if uploaded_file is not None:
    try:
        image=Image.open(uploaded_file)
        
        st.sidebar.image(image, caption="Uploaded Image", use_container_width=True)

        if image.mode in ("RGBA", "P"):
            image=image.convert("RGB")
        base_name = os.path.splitext(uploaded_file.name)[0]
        save_path=f"{base_name}.jpg"


        # 3. Save the image to the current working directory
        image.save(save_path, "JPEG")
        st.sidebar.success(f" Image successfully saved as '{save_path}'!")

    except Exception as e:
        st.error(f"Error processing image: {e}")
#===========Resume generator===========

prompt="""you are a helpful AI assistance
with job resume maker, your task is to give
HTML format resume, with proper designing using recent CSS and JS
code, with professional design format, user will upload data and return
HTML format resume"""
final_prompt=prompt+resume_maker_prompt()

user_info = st.text_input("Enter your information")

user_details=f"""user details: given below:
Resume info: {user_info}
Photo: {uploaded_file }
Photo present in current directory with name as
uploaded_file, and once resume generated give
download button in same html code.
Default if not given: Give Python Developer Resume"""


query = final_prompt + user_details

if st.button("Generate Resume"):
 with st.spinner("Running Agent...."):

    response=agent.invoke({'messages':[{'role':'user',"content":query}]})
    code=response['messages'][-1].content[-1]['text']


    st.markdown(code)
    st.html(code, width="stretch", unsafe_allow_javascript=True)
