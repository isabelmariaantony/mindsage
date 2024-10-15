# MindSage - Dementia Detection and Advice GPT

**MindSage** is a web-based application that allows users to upload images for dementia classification using a pre-trained VGG16 model. The classification result is used to pre-select the user's dementia type and provide tailored advice. It also provides personalized dementia care advice using FAISS for document retrieval and OpenAI's GPT for generating responses.

![Mindsage3](https://github.com/user-attachments/assets/fc803ee0-610d-47b4-b2cd-cd9bc96a5c47)


## Features

- **User Information**: Collects details like age, location, medical conditions, eating habits, and lifestyle information.
- **Dementia Classification**: Allows users to upload images for dementia classification or select their classification manually.
- **FAISS Search**: Uses FAISS to search relevant dementia care documents based on user queries and classifications.
- **OpenAI GPT Integration**: Provides personalized dementia care advice using OpenAI's GPT-3.5-turbo model.
- **Database**: Stores user information, including their dementia classification, medical details, preferences, and last query, in an SQLite database.

## Prerequisites

Before you begin, ensure that you have the following installed on your machine:

- **Python 3.9** or higher
- **pip** (Python package manager)
- An **OpenAI API key** for accessing the GPT model.

## Installation

Follow these steps to set up and run the application:

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/mindsage.git
cd mindsage
```

### 2. Create a Virtual Environment

It is recommended to create a virtual environment to avoid conflicts with other dependencies on your system:

```bash
python -m venv venv
```

Activate the virtual environment:

- On **Linux/macOS**:
  ```bash
  source venv/bin/activate
  ```

- On **Windows**:
  ```bash
  venv\Scripts\activate
  ```

### 3. Install Dependencies

Install the required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

The app requires an **OpenAI API key** to work. Create a `.env` file in the root directory of the project and add the following:

```bash
OPENAI_API_KEY=your_openai_api_key
```

Replace `your_openai_api_key` with your actual OpenAI API key.

### 5. Initialize the Database

Before running the app, you need to initialize the SQLite database. The app will automatically create the necessary tables when started, but you can ensure that the database is ready by running:

```bash
python -c "from database import init_db; init_db()"
```

This will initialize the database with the required tables.

## Running the Application

To start the Streamlit web application, run the following command:

```bash
streamlit run app.py
```

This will launch the app locally, and you can access it by opening your browser and navigating to:

```
http://localhost:8501
```

## Usage

### Returning Users:

1. **Log in** by entering your name. If you're already in the system, your details will be pre-populated, including your last query and dementia classification.
2. **Ask a question** related to dementia care, and the app will retrieve relevant documents and generate a personalized response using GPT.
3. **Modify your preferences** or update your medical details, eating habits, and lifestyle information as needed.

### New Users:

1. **Upload an image** of a dementia-related scan or picture for classification. The app will use a pre-trained VGG16 model to predict your dementia classification.
2. **Manually input your details**, including age, location, medical conditions, eating habits, and lifestyle.
3. **Ask a question**, and the app will provide a personalized dementia care response based on your classification and the documents retrieved from FAISS.

## File Structure

- `app.py`: Main Streamlit app file that handles user input, FAISS search, image classification, and OpenAI integration.
- `model.py`: Contains the dementia classification model (VGG16) and exposes a `predict` method for image classification.
- `faiss_index.py`: Contains FAISS index setup and search functions for retrieving relevant documents.
- `database.py`: Handles SQLite database operations (e.g., storing and retrieving user information).
- `requirements.txt`: Lists all the dependencies required for the project.
- `.env`: File that contains your OpenAI API key (you need to create this file).

## Dependencies

The main dependencies for this application are:

- **streamlit**: The framework used for building the web interface.
- **openai**: Used for integrating OpenAI's GPT-3.5-turbo API.
- **faiss-cpu**: FAISS library used for document search.
- **sentence-transformers**: Used to convert text into embeddings for FAISS.
- **tensorflow**: Used for loading and predicting the dementia classification model (VGG16).
- **python-dotenv**: To load environment variables from a `.env` file.
- **sqlite3**: For storing user information in a local SQLite database.

You can find the complete list of dependencies in the `requirements.txt` file.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

---

### Notes:
- Make sure to replace `your_openai_api_key` with your actual API key in the `.env` file.
- Ensure the **model file** (`best_model_vgg16.h5`) and the **image folder** exist in the appropriate directories for the image-based dementia classification to work.
