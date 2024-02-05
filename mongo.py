from functools import cache
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import gridfs
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.embeddings import VoyageEmbeddings
from langchain_community.vectorstores import FAISS
from PyPDF2 import PdfReader

embed = VoyageEmbeddings(
    voyage_api_key="pa-C_1gQndF0fx7QpliJB16WvpiB55Sv0j_Jvl2yjrc3CA",
    model="voyage-lite-02-instruct",
    show_progress_bar=True,
)


@cache
def connectMongo():
    try:
        uri = "mongodb+srv://abhishek:Mongo82002@schooldata.qzzwfkp.mongodb.net/?retryWrites=true&w=majority"

        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi("1"))

        print("Mongo DB connected")
        return client.get_database("SchoolData")
    except Exception as e:
        return None


def getSchoolClsSub(user):
    db = connectMongo()
    if db == None:
        print("not connected")
    else:
        data = db.studentData.find_one({"username": user})
        return data["schoolName"], data["class"], data["subject"]


def signInsertStudentData(username, password, teacherClass, school):
    db = connectMongo()
    if db == None:
        return "error"
    else:
        try:
            db.studentData.insert_one(
                {
                    "username": username,
                    "password": password,
                    "class": teacherClass,
                    "schoolName": school,
                }
            )
        except Exception as e:
            return e


def signInsertTeacherData(username, password, school):
    db = connectMongo()
    if db == None:
        return "error"
    else:
        try:
            db.teacherData.insert_one(
                {"username": username, "password": password, "schoolName": school}
            )
        except Exception as e:
            return e


def authenticateStudent(username, password):
    db = connectMongo()
    if db == None:
        print("not connected")
    else:
        data = db.studentData.find_one({"username": username})
        if data : 
            if data["username"] == username and data["password"] == password:
                print(username, data["username"], data["password"])
                return (data["class"], data["schoolName"])
        else :
            return (None, None)
            

    return (None, None)


def authenticateTeacher(username, password):
    db = connectMongo()
    if db == None:
        print("not connected")
    else:
        data = db.teacherData.find_one({"username": username})
        if data["username"] == username and data["password"] == password:
            print(username, data["username"], data["password"])
            return data["schoolName"]
        else:
            print(False)
            return None
    return False


def checkFile(db, fileName):
    data = db.fs.files.find_one({"filename": fileName})
    return True if data else False


def upload(data, fileName):
    db = connectMongo()
    if db != None:
        print(fileName)
        print("db connected")
        if not checkFile(db, fileName):
            fs = gridfs.GridFS(db)
            fs.put(data, filename=fileName)
            print("upload done")
            return True
        else:
            print("File already present")
            return False
    else:
        print("upload failed")
        return False


def load_vdb(schoolName, cls, sub):
    try:
        return FAISS.load_local(f".Vector_DBs/{schoolName}_class_{cls}_{sub}", embeddings=embed)
    except Exception as e:
        print(e)
        return None


def updateVDB(files, schoolName, cls, sub):
    vdb = load_vdb(schoolName, cls, sub)
    # chunks = None
    print(not files, vdb)
    text_splitter = RecursiveCharacterTextSplitter()
    if not files:
        print("No PDF files found in the folder.")
    else:
        # for pdf_file in files:
        text = ""
        pdf_reader = PdfReader(files)
        print("pages = " + str(len(pdf_reader.pages)))
        pages = 0

        for page in pdf_reader.pages:
            pages += 1
            text += page.extract_text()
        # data = loader.load()
        chunks = text_splitter.split_text(text)
        print("data loaded")
        # texts.extend(text)
        # print(chunks)
        if vdb == None:
            # print(chunks)
            vdb = FAISS.from_texts(chunks, embedding=embed)
            vdb.save_local(f"./{schoolName}_class_{cls}_{sub}")
            print("vector db created and documents added")
            return True
        else:
            vdb.add_texts(chunks)
            print("Add to exiting db")
            return True
    return False
