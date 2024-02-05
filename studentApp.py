import streamlit as st
from streamlit_chat import message
from mongo import authenticateStudent, signInsertStudentData, getSchoolClsSub
from langchain_community.llms import HuggingFaceTextGenInference
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import VoyageEmbeddings
from langchain.vectorstores import FAISS
import os
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler  # for streaming response
from langchain.callbacks.manager import CallbackManager
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])


header = st.container()
logIn = st.container()
logOut = st.container()
main = st.container()
signIn = st.container()


if "loggedIn" not in st.session_state:
    st.session_state["loggedIn"] = False
    st.session_state["sessition_user"] = ""

schoolName = None
cls = None
sub = None
chain = None


def loadModels(schoolName, cls, sub):
    print(schoolName, cls, sub)
    ENDPOINT_URL = "http://44.203.87.25:8080/"
    # create llm
    llm = HuggingFaceTextGenInference(
        inference_server_url=ENDPOINT_URL,
        max_new_tokens=256,
        top_k=10,
        top_p=0.95,
        typical_p=0.95,
        temperature=0.1,
        repetition_penalty=1,
    )

    embedding_model = VoyageEmbeddings(
    voyage_api_key="pa-C_1gQndF0fx7QpliJB16WvpiB55Sv0j_Jvl2yjrc3CA",
    model="voyage-lite-02-instruct",
    show_progress_bar=True,
    )
    
    system_prompt = '''
    You are chatbot, who is going to help in what ever the human needs. You need to act like a human and greet them when they do. Initially when the human greet, you need to greet them back. Ignore the context whenever the person is greeting you or making a general conversation which is irrelevant from the given context.

    '''
    
    B_INST, E_INST = "<s>[INST] ", " [/INST]"

    prompt_template = (
                    B_INST
                    + system_prompt
                    + """

                Context: {history} \n {context}
                User: {question}"""
                    + E_INST
                )
    prompt = PromptTemplate(input_variables=["history", "context", "question"], template=prompt_template)
    
    memory = ConversationBufferMemory(input_key="question", memory_key="history")

    vector_store = FAISS.load_local(f"./{schoolName}_class_{cls}_{sub}", embedding_model)
    retriever = vector_store.as_retriever(search_kwargs={"k":3})

    chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt, "memory": memory},
        )
    return chain


def initialize_session_state():
    if "history" not in st.session_state:
        st.session_state["history"] = []

    if "generated" not in st.session_state:
        st.session_state["generated"] = ["Hello! Ask me anything about your lessons"]

    if "past" not in st.session_state:
        st.session_state["past"] = ["Hey!"]


def conversation_chat(query, chain):
    result = chain.invoke({"query": query, "chat_history": st.session_state["history"]})
    st.session_state["history"].append((query, result["result"]))
    return result["result"]


def genQuery(user_input, chain):
    print("user = " + str(user_input)+" .use the content to answer the question correctly.")
    if user_input != "":
        
        output = conversation_chat(user_input, chain)
        st.session_state["past"].append(user_input)
        st.session_state["generated"].append(output)
    else:
        st.error("Please enter query")


def display_chat_history(chain):
    reply_container = st.container()
    container = st.container(border=True)

    with container:
        # with st.form(key="my_form", clear_on_submit=True):
        user_input = st.text_input("Question:", key="input")
            # submit_button = st.form_submit_button(label='Send')
        st.button(
            label="Send", on_click=genQuery, args=(user_input, chain)
        )

    if st.session_state["generated"]:
        with reply_container:
            for i in range(len(st.session_state["generated"])):
                message(
                    st.session_state["past"][i],
                    is_user=True,
                    key=str(i) + "_user",
                    avatar_style="thumbs",
                )
                message(
                    st.session_state["generated"][i],
                    key=str(i),
                    avatar_style="fun-emoji",
                )


def signin(user, passw, className, schoolName):
    response = signInsertStudentData(user, passw, className, schoolName)
    if response == "error":
        st.error("Error:", response)
    else:
        print(response, user, passw, className, schoolName)
        st.success("Sign Up Success, Switch to login and login to you account")


def login(u, p):
    std_class, school = authenticateStudent(u, p)
    if std_class and school:
        st.session_state["loggedIn"] = True
        st.session_state["sessition_user"] = u
        st.session_state["sessition_class"] = std_class
        st.session_state["sessition_school"] = school
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
                className = st.selectbox(
                    "Select Class",
                    options=["1", "2", "3", "4"],
                    placeholder="Choose your class",
                    index=None,
                )
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
                    signin(user, passw, className, schoolName)
            else:
                print(user, passw)
                st.button(
                    "Sign In", on_click=login, args=(user, passw), key="loginbutton"
                )


def mainPage():
    with main:
        cls = st.session_state["sessition_class"]
        schoolName = st.session_state["sessition_school"]
        st.header(f"School : {schoolName}")
        st.header(f"Class : {cls}")
        sub = st.selectbox(
            "Select Subject", options=["Maths", "Science", "Social Science"], index=None
        )
        # uploadButton = st.button(label="Load")
        # if uploadButton:
        if sub:
            initialize_session_state()
            # Display chat history
            print(f"./{schoolName}_class_{cls}_{sub}")
            if os.path.exists(f"./{schoolName}_class_{cls}_{sub}"):
                display_chat_history(loadModels(schoolName, cls, sub))
            else:
                st.error("No books founds")
        logoutbt = st.button(label="Sign Out")
        if logoutbt:
            st.session_state["loggedIn"] = False
        # schoolName =st.session_state['user_schoolName']
        # schoolName, cls, sub = getSchoolClsSub(st.session_state['sessition_user'])
        # Initialize session state


with header:
    st.title("Student")
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
