import streamlit as st
from mongo import authenticateTeacher, signInsertTeacherData, upload, updateVDB

header = st.container()
logIn = st.container()
logOut = st.container()
main = st.container()
signIn = st.container()


if "loggedIn" not in st.session_state:
    st.session_state["loggedIn"] = False


def signin(user, passw, schoolName):
    response = signInsertTeacherData(user, passw, schoolName)
    if response == "error":
        st.error("Error:", response)
    else:
        st.success("Sign Up Success, Switch to login and login to you account")


def login(u, p):
    data = authenticateTeacher(u, p)
    if data:
        st.session_state["loggedIn"] = True
        st.session_state["user_schoolName"] = data
    else:
        st.session_state["loggedIn"] = False
        st.error("Invalid Username or Password")


def showLoginPage():
    with logIn:
        if st.session_state["loggedIn"] == False:
            toogleButton = st.toggle(label=" ", label_visibility="hidden")
            if toogleButton:
                st.write("Sign In")
            else:
                st.write("Sign Up")
                schoolName = st.selectbox(
                    "Select School",
                    options=["School 1", "School 2"],
                    placeholder="Choose your school",
                    index=None,
                )
                # className = st.selectbox("Select Class", options=["1", "2", "3", "4"], placeholder="Choose your class", index=None)
                # subName = st.selectbox("Select Subject", options=["Maths", "Science", "Social Science"], placeholder="Choose your subject", index=None)
            user = st.text_input(label=" ", placeholder="Username", key="username")
            passw = st.text_input(
                label=" ", placeholder="Password", max_chars=12, key="password"
            )
            if not toogleButton:
                st.text_input(
                    label=" ",
                    placeholder="Confirm Password",
                    max_chars=12,
                    key="confirm",
                )
                bt = st.button("Sign Up", key="signinbutton")
                if bt:
                    signin(user, passw, schoolName)
            else:
                print(user, passw)
                st.button(
                    "Sign In", on_click=login, args=(user, passw), key="loginbutton"
                )


def upload_doc(cls, sub, data, schoolName):
    if cls == None or sub == None:
        st.error("Please select class and subject")
    else:
        # uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True)
        # print(data[0].name)
        for uploaded_file in data:
            print("read", uploaded_file)
            bytes_data = uploaded_file.read()
            # st.write("filename:", uploaded_file.name)
            # st.write(bytes_data)
            # if upload(bytes_data, uploaded_file.name):
            #    print(uploaded_file.__dir__)
            # progress_bar = st.progress(0)
            if updateVDB(uploaded_file, schoolName, cls, sub) and upload(bytes_data, uploaded_file.name):
                st.success("Files Uploaded")
            else:
                st.error("Files not uploaded")


def mainPage():
    with main:
        schoolName = st.session_state["user_schoolName"]
        st.header(st.session_state["user_schoolName"])
        cls = st.selectbox(
            "Select Class",
            options=["1", "2", "3", "4"],
            placeholder="Choose Class",
            index=None,
        )
        sub = st.selectbox(
            "Select Subject", options=["Maths", "Science", "Social Science"], index=None
        )

        data = st.file_uploader(
            label="Upload PDF", type="pdf", accept_multiple_files=True
        )
        # uploadButton = st.button(label="Upload")
        st.button(label="Upload", on_click=upload_doc, args=(cls, sub, data, schoolName))

        logoutbt = st.button(label="Sign Out")
        if logoutbt:
            st.session_state["loggedIn"] = False


with header:
    st.title("Teacher")
    if "loggedIn" not in st.session_state:
        st.session_state["loggedIn"] = False
        print("not yet logged in")
        showLoginPage()
    else:
        if st.session_state["loggedIn"]:
            print("Logged In")
            mainPage()
        else:
            print("Log in first")
            showLoginPage()
