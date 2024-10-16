import streamlit as st
import os
import tempfile
from openai import OpenAI
import model
from faiss_index import build_faiss_index, search_faiss_index
from database import init_db, update_user, get_user
from dotenv import load_dotenv
from PIL import Image

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

# Streamlit App Layout with Tabs
st.title("Detect Dementia and receive care")

# Split the UI into 3 tabs
tabs = st.tabs(["Profile Setup", "Detect Dementia with MRI Scans", "Get Care/tips"])

# Tab 1: Profile Setup/Modification
with tabs[0]:
    st.header("Profile Setup/Modification")
    
    username = st.text_input("Enter your name:")
    
    if username:
        user = get_user(username)
        
        # Prepopulate fields for existing users
        if user:
            age = st.number_input("Enter your age:", min_value=1, max_value=120, step=1, value=user[2] if user[2] else 67)
            location = st.text_input("Enter your location:", value=user[3] if user[3] else "")
            medical_details = st.text_area("Enter medical details (other diseases):", value=user[4] if user[4] else "")
            eating_habits = st.text_area("Describe your eating habits:", value=user[5] if user[5] else "")
            lifestyle_details = st.text_area("Describe your lifestyle details (e.g., physical activity):", value=user[6] if user[6] else "")
            preferences = st.text_area("Any preferences or specific dementia care challenges?", value=user[7] if user[7] else "")
            
            # Update user details on change
            if st.button("Update Profile"):
                update_user(username, age, location, medical_details, eating_habits, lifestyle_details, preferences=preferences)
                st.success("Profile updated successfully!")
        else:
            # New user
            age = st.number_input("Enter your age:", min_value=1, max_value=120, step=1, value=67)
            location = st.text_input("Enter your location:")
            medical_details = st.text_area("Enter medical details (other diseases):")
            eating_habits = st.text_area("Describe your eating habits:")
            lifestyle_details = st.text_area("Describe your lifestyle details (e.g., physical activity):")
            preferences = st.text_area("Any preferences or specific dementia care challenges?")
            
            if st.button("Save Profile"):
                update_user(username, age, location, medical_details, eating_habits, lifestyle_details, preferences=preferences)
                st.success("Profile created successfully!")

# Tab 2: Expert MRI Upload
with tabs[1]:
    st.header("Upload MRI Scan for Dementia Classification")
    
    if username:
        user = get_user(username)
        # Load the initial dementia classification from the database
        if user and user[9]:
            st.session_state['dementia_classification'] = user[9]
            st.write(f"Current Dementia Classification: {user[9]}")
        else:
            st.write("No dementia classification available. Please upload an MRI image.")
        
        uploaded_image = st.file_uploader("Upload an MRI image", type=["jpg", "jpeg", "png"])
        
        if uploaded_image:
            # Save the uploaded image to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                temp_file.write(uploaded_image.read())
                temp_file_path = temp_file.name

            # Display the uploaded image
            st.image(Image.open(uploaded_image), caption="Uploaded MRI Image", use_column_width=True)
            
            # Predict dementia classification from the image
            predicted_class_index = model.predict(temp_file_path)
            new_classification = class_mapping.get(predicted_class_index, "No dementia")
            
            # Update the new classification in Streamlit's session state and in the database
            st.session_state['dementia_classification'] = new_classification
            st.write(f"New Dementia Classification: {new_classification}")
            
            # Store the new classification in the database
            update_user(username, classification=new_classification)
            st.success("New dementia classification updated in the profile.")
        

# Tab 3: Query Submission and Response
with tabs[2]:
    st.header("Query Submission and Dementia Care Advice")

    if username:
        user = get_user(username)

        if user:
            # Fetch details from the user's profile (set in Tab 1 and Tab 2)
            age = user[2]
            location = user[3]
            medical_details = user[4]
            eating_habits = user[5]
            lifestyle_details = user[6]
            classification = st.session_state.get('dementia_classification', user[9] if user[9] else "No dementia")
            
            # Query and GPT response
            query = st.text_input("Ask a question:")
            if query:
                handle_query(age, location, medical_details, eating_habits, lifestyle_details, classification, query)
                update_user(username, age, location, medical_details, eating_habits, lifestyle_details, last_query=query)

            st.subheader("Your Last Query:")
            st.write(f"Your last query was: {user[8]}")
        else:
            st.write("User not found. Please set up your profile in Tab 1.")
