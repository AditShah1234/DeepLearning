# # # pip install streamlit langchain lanchain-openai beautifulsoup4 python-dotenv chromadb
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
from langchain_community.embeddings import SentenceTransformerEmbeddings
# from langchain import hub
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import streamlit as st
from langchain.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_google_vertexai import ChatVertexAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
import vertexai
from PyPDF2 import PdfReader
vertexai.init(project='amazing-office-424201-t4')
load_dotenv()
# # # app config


def get_vectorstore_from_url(url):
    loader = WebBaseLoader(url)
    document = loader.load()
    text_splitter = RecursiveCharacterTextSplitter()
    document_chunks = text_splitter.split_documents(document)
    embed =  SentenceTransformerEmbeddings()
    vectorstore = Chroma.from_documents(document_chunks,embed)
    
    return vectorstore

def get_vectorstore_from_pdf():
    pdf = st.file_uploader("**Upload your PDF**", type='pdf')
    if pdf is not None:
        pdf_reader = PdfReader(pdf)

        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
            )
        chunks = text_splitter.split_text(text=text)

        # # embeddings
        store_name = pdf.name[:-4]
        st.write(f'{store_name}')
    embed =  SentenceTransformerEmbeddings()
    vectorstore = Chroma.from_documents(chunks,embed)
    return vectorstore
        
def get_context_retriever_chain(vectorstore):

    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})

    contextualize_q_system_prompt = """Given a chat history and the latest user question \
    which might reference context in the chat history, formulate a standalone question \
    which can be understood without the chat history. Do NOT answer the question, \
    just reformulate it if needed and otherwise return it as is."""
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    return retriever , contextualize_q_prompt 

def get_conversational_rag_chain(): 
    
    qa_system_prompt = """You are an assistant for question-answering tasks. \
        Use the following pieces of retrieved context to answer the question. \
        If you don't know the answer, just say that you don't know. \
        Use three sentences maximum and keep the answer concise.\

        {context}"""
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    return qa_prompt


def get_response(user_input):
    
    
    # llm = ChatGoogleGenerativeAI(model="gemini-pro")
    vertexai.init(project='amazing-office-424201-t4')   
    llm = ChatVertexAI(model="gemini-pro",convert_system_message_to_human=True)
    retriever , contextualize_q_prompt  = get_context_retriever_chain(st.session_state.vector_store)
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    question_answer_chain = get_conversational_rag_chain()
    stuff_documents_chain = create_stuff_documents_chain(llm, question_answer_chain)
    rag_chain = create_retrieval_chain(history_aware_retriever, stuff_documents_chain)

    
    
    response = rag_chain.invoke({
        "chat_history": st.session_state.chat_history,
        "input":user_input
    })
    
    return response["answer"]



# # # sidebar
# # # with st.sidebar:
st.set_page_config(page_title="Chat with websites", page_icon="🤖")
st.title("Chat with anything")


website_url = st.text_input("Website URL")
import asyncio
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
if website_url is None or website_url == "":
    st.info("Please enter a website URL")

else:
    # session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="Hello, I am a bot. How can I help you?"),
        ]
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = get_vectorstore_from_url(website_url)
        

    # user input
    user_query = st.chat_input("Type your message here...")
    if user_query is not None and user_query != "":
        response = get_response(user_query)
        st.session_state.chat_history.append(HumanMessage(content=user_query))
        st.session_state.chat_history.append(AIMessage(content=response))
        
       

    # conversation
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message("AI"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message("Human"):
                st.write(message.content)



