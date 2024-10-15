import streamlit as st
import os
import tempfile
from openai import OpenAI
import model
from faiss_index import build_faiss_index, search_faiss_index
from database import init_db, update_user, get_user
from dotenv import load_dotenv

# Mapping of prediction output to classification
class_mapping = {
    2: "No dementia",
    3: "Very mild dementia",
    0: "Mild dementia",
    1: "Moderate dementia"
}

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize the SQLite database
init_db()

# Build FAISS indices for each classification (in-memory)
indices, embeddings_dict = build_faiss_index()

# Function to handle the query, document retrieval, and GPT response generation
def handle_query(age, location, medical_details, eating_habits, lifestyle_details, classification, query):
    # Search FAISS for relevant documents based on query and classification
    relevant_docs = search_faiss_index(query, indices, classification)
    
    # Combine relevant documents into context for GPT-3
    context = (f"The user is {age} years old, located in {location}, with the following medical details: {medical_details}. "
               f"Their eating habits include: {eating_habits}, and their lifestyle details are: {lifestyle_details}. "
               f"Their dementia classification is: {classification}.\n\n"
               f"Here are some tips for dementia care based on their classification:\n"
               + " ".join(relevant_docs))
    
    # Generate GPT response with OpenAI's ChatCompletion
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert in dementia care."},
            {"role": "user", "content": f"{context}\n\nAnswer this question based on the above information: {query}"}
        ],
        max_tokens=150
    )
    
    # Display the AI-generated response
    st.write(response.choices[0].message.content)
    
    # Print relevant documents to the console (for debugging)
    print("Relevant documents returned by FAISS:")
    for doc in relevant_docs:
        print(doc)

# Streamlit App Layout
st.title("Dementia Care Advice GPT")
username = st.text_input("Enter your name:")

if username:
    user = get_user(username)

    # Dementia Classification Options
    classification_options = ["No dementia", "Very mild dementia", "Mild dementia", "Moderate dementia"]

    if user:
        # Prepopulate fields for existing users
        selected_classification = user[9] if user[9] else "No dementia"
        classification_index = classification_options.index(selected_classification)

        age = st.number_input("Enter your age:", min_value=1, max_value=120, step=1, value=user[2] if user and user[2] else 67)
        location = st.text_input("Enter your location:", value=user[3] if user and user[3] else "")
        medical_details = st.text_area("Enter medical details (other diseases):", value=user[4] if user and user[4] else "")
        eating_habits = st.text_area("Describe your eating habits:", value=user[5] if user and user[5] else "")
        lifestyle_details = st.text_area("Describe your lifestyle details (e.g., physical activity):", value=user[6] if user and user[6] else "")

        classification = st.selectbox("Select Dementia Classification", classification_options, index=classification_index)

        # Query and GPT response
        query = st.text_input("Ask a question:")
        if query:
            handle_query(age, location, medical_details, eating_habits, lifestyle_details, classification, query)
            update_user(username, age, location, medical_details, eating_habits, lifestyle_details, last_query=query, classification=classification)

        st.subheader("Your Last Query:")
        st.write(f"Your last query was: {user[8]}")

        # Personalize the experience
        preferences = st.text_area("Any preferences or specific dementia care challenges?", value=user[7] if user and user[7] else "")
        if preferences:
            update_user(username, preferences=preferences)
    else:
        # New User or Upload Image for Classification
        uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        if uploaded_image:
            # Save and pass image to the prediction model
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                temp_file.write(uploaded_image.read())
                temp_file_path = temp_file.name

            # Predict dementia classification from the image
            predicted_class_index = model.predict(temp_file_path)
            selected_classification = class_mapping.get(predicted_class_index, "No dementia")
            classification_index = classification_options.index(selected_classification)

            classification = st.selectbox("Select Dementia Classification", classification_options, index=classification_index)

            # Input for new users
            age = st.number_input("Enter your age:", min_value=1, max_value=120, step=1)
            location = st.text_input("Enter your location:")
            medical_details = st.text_area("Enter medical details (other diseases):")
            eating_habits = st.text_area("Describe your eating habits:")
            lifestyle_details = st.text_area("Describe your lifestyle details (e.g., physical activity):")

            # Query and GPT response for new users
            query = st.text_input("Ask a question:")
            if query:
                handle_query(age, location, medical_details, eating_habits, lifestyle_details, classification, query)
                update_user(username, age, location, medical_details, eating_habits, lifestyle_details, last_query=query, classification=classification)

            st.subheader("Personalize your experience:")
            preferences = st.text_area("Any preferences or specific dementia care challenges?")
            if preferences:
                update_user(username, preferences=preferences)

