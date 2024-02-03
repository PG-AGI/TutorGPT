import streamlit as st
from mongo import authenticateTeacher, signInsertTeacherData, upload, updateVDB

header = st.container()
logIn = st.container()
logOut = st.container()
main = st.container()
signIn = st.container()


if 'loggedIn' not in st.session_state:
   st.session_state['loggedIn'] = False

def signin(user, passw, className, schoolName, subName):
   response = signInsertTeacherData(user, passw, className, schoolName, subName)
   if response == "error":
      st.error("Error:", response)
   else:
      st.success("Sign Up Success, Switch to login and login to you account")
      
def login(u, p):
   if authenticateTeacher(u, p):
      st.session_state['loggedIn'] = True
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
      schoolName = st.selectbox("Select School", options=["School 1", "School 2", "School 3", "School 4"], placeholder="Choose your school", index=None)
      cls = st.selectbox("Select Class", options=["1", "2", "3", "4"], placeholder="Choose Class", index=None)
      sub = st.selectbox("Select Subject", options=["Maths", "Science", "Social Science"], index=None)

      data = st.file_uploader(label="Upload PDF",type="pdf", accept_multiple_files=True)
      uploadButton = st.button(label="Upload")
      if uploadButton:
         # uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True)
         print(data[0].name)
         for uploaded_file in data:
            bytes_data = uploaded_file.read()
            # st.write("filename:", uploaded_file.name)
            # st.write(bytes_data)
            if upload(bytes_data, uploaded_file.name):
               print(uploaded_file.__dir__)
               if updateVDB(uploaded_file, schoolName, cls, sub):
                  st.success("Files Uploaded")
               else:
                  st.error("Files not uploaded")
      logoutbt = st.button(label="Sign Out")
      if logoutbt:
         st.session_state['loggedIn'] = False

with header:
   st.title("Teacher")
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