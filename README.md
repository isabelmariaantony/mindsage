# MindSage

**MindSage** is a web-based application that provides personalized mental and physical health care advice, focusing on dementia-related care. It uses FAISS to search relevant documents and OpenAI's GPT-3.5-turbo to generate tailored responses. The application allows users to input their medical and lifestyle details, which are stored in an SQLite database and used to provide customized care advice.

## Features

- **User Information**: Collects details like age, location, medical conditions, eating habits, and lifestyle information.
- **Dementia Classification**: Allows users to select their dementia classification (e.g., "No dementia," "Very mild dementia," "Mild dementia," "Moderate dementia").
- **FAISS Search**: Uses FAISS to search relevant care-related documents based on the user's query and classification.
- **OpenAI GPT-3.5**: Provides personalized mental and physical health care advice using OpenAI's GPT-3.5-turbo model.
- **Database**: Stores user information, including their dementia classification, medical details, preferences, and last query, in an SQLite database.

## Prerequisites

Before you begin, ensure that you have the following installed on your machine:

- **Python 3.9** or higher
- **pip** (Python package manager)

## Installation

Follow these steps to set up and run the **MindSage** application:

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

The app requires an OpenAI API key to work. Create a `.env` file in the root directory of the project and add the following:

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

- **User Input**: Enter your name, age, location, medical details (e.g., other diseases), eating habits, lifestyle details (e.g., physical activity), and dementia classification.
- **Query**: Input a query for personalized mental and physical health care advice. The app will search the relevant documents and generate a personalized response using OpenAI's GPT-3.5-turbo model.
- **Personalization**: Your details and preferences will be stored in the database for future use, allowing the app to generate tailored advice based on your past inputs.

## File Structure

- `app.py`: Main Streamlit app file that handles user input, FAISS search, and OpenAI integration.
- `faiss_index.py`: Contains FAISS index setup and search functions.
- `database.py`: Handles SQLite database operations (e.g., storing and retrieving user information).
- `requirements.txt`: Lists all the dependencies required for the project.
- `.env`: File that contains your OpenAI API key (you need to create this file).

## Dependencies

The main dependencies for this application are:

- `streamlit`: The framework used for building the web interface.
- `openai`: Used for integrating OpenAI's GPT-3.5-turbo API.
- `faiss-cpu`: FAISS library used for document search.
- `sentence-transformers`: Used to convert text into embeddings for FAISS.
- `python-dotenv`: To load environment variables from a `.env` file.
- `sqlite3`: For storing user information in a local SQLite database.

You can find the complete list of dependencies in the `requirements.txt` file.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

---

### Notes:
- Make sure to replace `your_openai_api_key` with your actual API key.
- Adjust the repository URL if applicable.

Let me know if you need any additional sections or further changes!
