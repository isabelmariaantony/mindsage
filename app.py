import streamlit as st
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from faiss_index import build_faiss_index, search_faiss_index
from database import init_db, update_user, get_user
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key

# Initialize the SQLite database
init_db()

# Build FAISS indices for each classification (in-memory)
indices, embeddings_dict = build_faiss_index()

# Streamlit App Layout
st.title("Dementia Care Advice GPT")
username = st.text_input("Enter your name:")

if username:
    user = get_user(username)

    # Dementia Classification Options
    classification_options = ["No dementia", "Very mild dementia", "Mild dementia", "Moderate dementia"]

       # Preselect classification if it exists in the database
    if user and user[4]:  # Check if user exists and classification is not None
        selected_classification = user[4]
    else:
        selected_classification = "No dementia"  # Default value

    # Display the dropdown for dementia classification with preselection
    classification = st.selectbox("Select Dementia Classification", classification_options, index=classification_options.index(selected_classification))

    st.subheader("Query for dementia care advice:")
    query = st.text_input("Ask a question:")

    if query:

        # Search FAISS for relevant documents based on query and classification
        relevant_docs = search_faiss_index(query, indices, classification)

        # Print the relevant documents to the console
        print("Relevant documents returned by FAISS:")
        for doc in relevant_docs:
            print(doc)

        context = " ".join(relevant_docs)

        # Generate GPT response with OpenAI's ChatCompletion
        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert in dementia care."},
            {"role": "user", "content": f"Here are some tips for dementia care:\n{context}\n\nAnswer this question based on the above tips: {query}"}
        ],
        max_tokens=150)

        # Display the AI-generated response
        st.write(response.choices[0].message.content)

        # Update user last query and classification in the database
        update_user(username, last_query=query, classification=classification)

    if user:
        st.subheader("Your Last Query:")
        st.write(f"Your last query was: {user[3]}")
        st.subheader("Your Dementia Classification:")
        st.write(f"Your classification is: {user[4]}")  # Show the classification


    st.subheader("Personalize your experience:")
    preferences = st.text_area("Any preferences or specific dementia care challenges?")

    if preferences:
        update_user(username, preferences=preferences)
