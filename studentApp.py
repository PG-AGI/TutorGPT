import streamlit as st
from streamlit_chat import message
from mongo import authenticateStudent, signInsertStudentData, getSchoolClsSub
from langchain_community.llms import HuggingFaceTextGenInference
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.embeddings import VoyageEmbeddings
from langchain.vectorstores import FAISS

header = st.container()
logIn = st.container()
logOut = st.container()
main = st.container()
signIn = st.container()


if 'loggedIn' not in st.session_state:
   st.session_state['loggedIn'] = False
schoolName = None
cls = None
sub = None
chain  = None
def loadModels(schoolName, cls, sub):
   print(schoolName, cls, sub)
   ENDPOINT_URL = "http://44.203.87.25:8080/"
   #create llm
   llm = HuggingFaceTextGenInference(
      inference_server_url=ENDPOINT_URL,
      max_new_tokens=400,
      top_k=10,
      top_p=0.95,
      typical_p=0.95,
      temperature=0.7,
      repetition_penalty=1.03,
   )

   embedding_model = VoyageEmbeddings(voyage_api_key="pa-C_1gQndF0fx7QpliJB16WvpiB55Sv0j_Jvl2yjrc3CA", model = "voyage-lite-02-instruct", show_progress_bar=True)

   memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

   vector_store = FAISS.load_local(f"./{schoolName}_{cls}_{sub}", embedding_model)

   chain = ConversationalRetrievalChain.from_llm(llm=llm,chain_type='stuff',
                                                retriever=vector_store.as_retriever(search_kwargs={"k":2}),
                                                memory=memory)
   return chain

def initialize_session_state():
    if 'history' not in st.session_state:
        st.session_state['history'] = []

    if 'generated' not in st.session_state:
        st.session_state['generated'] = ["Hello! Ask me anything about your lessons"]

    if 'past' not in st.session_state:
        st.session_state['past'] = ["Hey!"]

def conversation_chat(query, chain):
    result = chain({"question": query, "chat_history": st.session_state['history']})
    st.session_state['history'].append((query, result["answer"]))
    return result["answer"]

def display_chat_history(chain):
    reply_container = st.container()
    container = st.container()

    with container:
        with st.form(key='my_form', clear_on_submit=True):
            user_input = st.text_input("Question:", key='input')
            submit_button = st.form_submit_button(label='Send')

        if submit_button and user_input:
            output = conversation_chat(user_input, chain)

            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)

    if st.session_state['generated']:
        with reply_container:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state["past"][i], is_user=True, key=str(i) + '_user', avatar_style="thumbs")
                message(st.session_state["generated"][i], key=str(i), avatar_style="fun-emoji")



def signin(user, passw, className, schoolName, subName):
   response = signInsertStudentData(user, passw, className, schoolName, subName)
   if response == "error":
      st.error("Error:", response)
   else:
      print(response, user, passw, className, schoolName, subName)
      st.success("Sign Up Success, Switch to login and login to you account")


def login(u, p):
   if authenticateStudent(u, p):
      st.session_state['loggedIn'] = True
      st.session_state['username'] = u
   else:
      st.session_state['loggedIn'] = False
      st.error("Invalid Username or Password")

def showLoginPage():
   with logIn:
      if st.session_state['loggedIn'] == False:
         toogleButton = st.toggle(label=" ", label_visibility="hidden")
         if toogleButton:
            st.write("Sign In")
         else:
            st.write("Sign Up")
            schoolName = st.selectbox("Select School", options=["School 1", "School 2", "School 3", "School 4"], placeholder="Choose your school", index=None)
            className = st.selectbox("Select Class", options=["1", "2", "3", "4"], placeholder="Choose your class", index=None)
            subName = st.selectbox("Select Subject", options=["Maths", "Science", "Social Science"], placeholder="Choose your subject", index=None)
         user = st.text_input(label=" ", placeholder="Username", key='username')
         passw = st.text_input(label=" ", placeholder="Password", max_chars=12, key='password')
         if not toogleButton:
            st.text_input(label=' ', placeholder="Confirm Password", max_chars=12, key='confirm')
            bt = st.button("Sign Up", key='signinbutton')
            if bt:
               signin(user, passw, className, schoolName, subName)
         else:
            print(user, passw)
            st.button("Sign In", on_click=login, args=(user, passw), key='loginbutton')

def mainPage():
   with main:
      schoolName, cls, sub = getSchoolClsSub(st.session_state['username'])
      # Initialize session state
      initialize_session_state()
      # Display chat history
      display_chat_history(loadModels(schoolName, cls, sub))
      logoutbt = st.button(label="Sign Out")
      if logoutbt:
         st.session_state['loggedIn'] = False

with header:
   st.title("Student")
   if 'loggedIn' not in st.session_state:
      st.session_state['loggedIn'] = False
      print("not yet logged in")
      showLoginPage()
   else:
      if st.session_state['loggedIn']:
         print("Logged In")
         mainPage()
      else:
         print("Log in first")
         showLoginPage()