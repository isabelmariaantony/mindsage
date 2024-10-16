import streamlit as st
import os
import tempfile
import bcrypt
from openai import OpenAI
import model
from faiss_index import build_faiss_index, search_faiss_index
from database import init_db, save_user, authenticate_user, get_user, update_user
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
    relevant_docs = search_faiss_index(query, indices, classification)
    context = (f"The user is {age} years old, located in {location}, with the following medical details: {medical_details}. "
               f"Their eating habits include: {eating_habits}, and their lifestyle details are: {lifestyle_details}. "
               f"Their dementia classification is: {classification}.\n\n"
               f"Here are some tips for dementia care based on their classification:\n"
               + " ".join(relevant_docs))
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert in dementia care."},
            {"role": "user", "content": f"{context}\n\nAnswer this question based on the above information: {query}"}
        ],
        max_tokens=150
    )
    
    st.write(response.choices[0].message.content)
    print("Relevant documents returned by FAISS:")
    for doc in relevant_docs:
        print(doc)

# Streamlit App Layout
st.title("Detect Dementia and Receive Care")

# Custom CSS for styling tabs
st.markdown("""
    <style>
    /* Style for the main tabs container */
    div[data-testid="stTabs"] div[role="tablist"] > button {
        border: 2px solid #f0f0f0;
        border-radius: 8px;
        background-color: #ADD8E6; /* Light blue */
        color: black;
        font-size: 16px;
        margin: 0 8px;
        padding: 10px;
        transition: background-color 0.3s ease;
    }
    
    /* Style for active tab */
    div[data-testid="stTabs"] div[role="tablist"] > button[aria-selected="true"] {
        background-color: #4682B4; /* Steel blue */
        color: white;
        border: 2px solid #4682B4;
    }
    
    /* Hover effect for tabs */
    div[data-testid="stTabs"] div[role="tablist"] > button:hover {
        background-color: #87CEEB; /* Sky blue */
        border: 2px solid #87CEEB;
    }
    </style>
""", unsafe_allow_html=True)

# Authentication state handling
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # Authentication (Login or Sign Up)
    auth_choice = st.radio("Choose an action", ["Login", "Sign Up"])

    if auth_choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if authenticate_user(username, password):
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success("Logged in successfully!")
                st.rerun()  # Refresh the UI to show the tabs after successful login
            else:
                st.error("Invalid username or password")

    elif auth_choice == "Sign Up":
        st.subheader("Sign Up")
        username = st.text_input("Username (for sign up)")
        password = st.text_input("Password", type="password")
        
        if st.button("Sign Up"):
            save_user(username, password)
            st.success("User registered successfully! Please log in.")
else:
    # Display welcome message and logout button
    col1, col2 = st.columns([3, 1])  # Creating two columns, one for the welcome message and one for the logout button
    
    with col1:
        st.write(f"Welcome, {st.session_state.username}!")
    
    with col2:
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()  # Refresh the app to go back to login/signup

    # Split the UI into 3 tabs
    tabs = st.tabs(["Setup Profile", "Detect Dementia", "Get Care"])

    # Tab 1: Profile Setup/Modification
    with tabs[0]:
        st.header("Profile Setup/Modification")
        
        user = get_user(st.session_state.username)
        
        if user:
            age = st.number_input("Enter your age:", min_value=1, max_value=120, step=1, value=user[2] if user[2] else 67)
            location = st.text_input("Enter your location:", value=user[3] if user[3] else "")
            medical_details = st.text_area("Enter medical details (other diseases):", value=user[4] if user[4] else "")
            eating_habits = st.text_area("Describe your eating habits:", value=user[5] if user[5] else "")
            lifestyle_details = st.text_area("Describe your lifestyle details (e.g., physical activity):", value=user[6] if user[6] else "")
            preferences = st.text_area("Any preferences or specific dementia care challenges?", value=user[7] if user[7] else "")
            
            if st.button("Update Profile"):
                update_user(st.session_state.username, age=age, location=location, medical_details=medical_details, eating_habits=eating_habits, lifestyle_details=lifestyle_details, preferences=preferences)
                st.success("Profile updated successfully!")
    
    # Tab 2: Expert MRI Upload
    with tabs[1]:
        st.header("Upload MRI Scan for Dementia Classification")
        
        if user:
            if user[9]:
                st.session_state['dementia_classification'] = user[9]
                st.write(f"Current Dementia Classification: {user[9]}")
            else:
                st.write("No dementia classification available. Please upload an MRI image.")
            
            uploaded_image = st.file_uploader("Upload an MRI image", type=["jpg", "jpeg", "png"])
            
            if uploaded_image:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                    temp_file.write(uploaded_image.read())
                    temp_file_path = temp_file.name

                st.image(Image.open(uploaded_image), caption="Uploaded MRI Image", use_column_width=True)
                
                predicted_class_index = model.predict(temp_file_path)
                new_classification = class_mapping.get(predicted_class_index, "No dementia")
                
                st.session_state['dementia_classification'] = new_classification
                st.write(f"New Dementia Classification: {new_classification}")
                
                update_user(st.session_state.username, classification=new_classification)
                st.success("New dementia classification updated in the profile.")
    
    # Tab 3: Query Submission and Response
    with tabs[2]:
        st.header("Dementia Care Advice")

        if user:
            age = user[2]
            location = user[3]
            medical_details = user[4]
            eating_habits = user[5]
            lifestyle_details = user[6]
            classification = st.session_state.get('dementia_classification', user[9] if user[9] else "No dementia")
            
            query = st.text_input("Ask a question:")
            if query:
                handle_query(age, location, medical_details, eating_habits, lifestyle_details, classification, query)
                update_user(st.session_state.username, last_query=query)
                
            st.subheader("Your Last Query:")
            st.write(f"Your last query was: {user[8]}")
