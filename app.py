import streamlit as st
import os
import tempfile

from openai import OpenAI
import model

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    if user and user[9]:  # Check if user exists and classification is not None
        selected_classification = user[9]

        # Display the dropdown for dementia classification with preselection
        classification = st.selectbox("Select Dementia Classification", classification_options, index=classification_options.index(selected_classification))

        # Fields for user details
        age = st.number_input("Enter your age:", min_value=1, max_value=120, step=1, value=user[2] if user and user[2] else 67)
        location = st.text_input("Enter your location:", value=user[3] if user and user[3] else "")
        medical_details = st.text_area("Enter medical details (other diseases):", value=user[4] if user and user[4] else "")
        eating_habits = st.text_area("Describe your eating habits:", value=user[5] if user and user[5] else "")
        lifestyle_details = st.text_area("Describe your lifestyle details (e.g., physical activity):", value=user[6] if user and user[6] else "")


        st.subheader("Query for dementia care advice:")
        query = st.text_input("Ask a question:")

        if query:

            # Search FAISS for relevant documents based on query and classification
            relevant_docs = search_faiss_index(query, indices, classification)

            # Print the relevant documents to the console
            print("Relevant documents returned by FAISS:")
            for doc in relevant_docs:
                print(doc)

        # Combine relevant documents into context for GPT-3
            context = f"The user is {age} years old, located in {location}, with the following medical details: {medical_details}. " \
                    f"Their eating habits include: {eating_habits}, and their lifestyle details are: {lifestyle_details}. " \
                    f"Their dementia classification is: {classification}.\n\n" \
                    f"Here are some tips for dementia care based on their classification:\n" \
                    + " ".join(relevant_docs)

            # Generate GPT response with OpenAI's ChatCompletion
            response = client.chat.completions.create(model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in dementia care."},
                {"role": "user", "content": f"{context}\n\nAnswer this question based on the above information: {query}"}
            ],
            max_tokens=150)

            # Display the AI-generated response
            st.write(response.choices[0].message.content)

            # Update user last query and classification in the database
            update_user(username, age, location, medical_details, eating_habits, lifestyle_details, last_query=query, classification=classification)

        if user:
            st.subheader("Your Last Query:")
            st.write(f"Your last query was: {user[8]}")

        st.subheader("Personalize your experience:")
        preferences = st.text_area("Any preferences or specific dementia care challenges?", value=user[7] if user and user[7] else "")

        if preferences:
            update_user(username, preferences=preferences)
    
    else:

        # Upload image
        uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

        # Only proceed if an image has been uploaded
        if uploaded_image:
            # Save the uploaded image to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                temp_file.write(uploaded_image.read())  # Write the uploaded image content to the temp file
                temp_file_path = temp_file.name  # Get the path of the temporary file

            # Use the model's predict method to get the classification index
            predicted_class_index = model.predict(temp_file_path)  # Pass the image path to predict()

            # Map the prediction index to the corresponding classification
            selected_classification = class_mapping.get(predicted_class_index, "No dementia")

             # Display the dropdown for dementia classification with preselection
            classification = st.selectbox("Select Dementia Classification", classification_options, index=classification_options.index(selected_classification))

            # Fields for user details
            age = st.number_input("Enter your age:", min_value=1, max_value=120, step=1, value=user[2] if user and user[2] else 67)
            location = st.text_input("Enter your location:", value=user[3] if user and user[3] else "")
            medical_details = st.text_area("Enter medical details (other diseases):", value=user[4] if user and user[4] else "")
            eating_habits = st.text_area("Describe your eating habits:", value=user[5] if user and user[5] else "")
            lifestyle_details = st.text_area("Describe your lifestyle details (e.g., physical activity):", value=user[6] if user and user[6] else "")


            st.subheader("Query for dementia care advice:")
            query = st.text_input("Ask a question:")

            if query:

                # Search FAISS for relevant documents based on query and classification
                relevant_docs = search_faiss_index(query, indices, classification)

                # Print the relevant documents to the console
                print("Relevant documents returned by FAISS:")
                for doc in relevant_docs:
                    print(doc)

            # Combine relevant documents into context for GPT-3
                context = f"The user is {age} years old, located in {location}, with the following medical details: {medical_details}. " \
                        f"Their eating habits include: {eating_habits}, and their lifestyle details are: {lifestyle_details}. " \
                        f"Their dementia classification is: {classification}.\n\n" \
                        f"Here are some tips for dementia care based on their classification:\n" \
                        + " ".join(relevant_docs)

                # Generate GPT response with OpenAI's ChatCompletion
                response = client.chat.completions.create(model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in dementia care."},
                    {"role": "user", "content": f"{context}\n\nAnswer this question based on the above information: {query}"}
                ],
                max_tokens=150)

                # Display the AI-generated response
                st.write(response.choices[0].message.content)

                # Update user last query and classification in the database
                update_user(username, age, location, medical_details, eating_habits, lifestyle_details, last_query=query, classification=classification)

            if user:
                st.subheader("Your Last Query:")
                st.write(f"Your last query was: {user[8]}")

            st.subheader("Personalize your experience:")
            preferences = st.text_area("Any preferences or specific dementia care challenges?", value=user[7] if user and user[7] else "")

            if preferences:
                update_user(username, preferences=preferences)

