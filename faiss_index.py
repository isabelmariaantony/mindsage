import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Load pre-trained model to convert text into embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# Sample dementia care documents mapped to classifications
classification_to_docs = {
    "No dementia": [
        "Stay mentally active: Engage in activities that challenge your brain, such as learning new skills, solving puzzles, reading, or playing memory-enhancing games to strengthen cognitive function.",

        "Exercise regularly: Physical activity like walking, swimming, or strength training increases blood flow to the brain and may help slow down cognitive decline. Aim for at least 150 minutes of moderate exercise each week.",

        "Eat a brain-healthy diet: Adopt a diet rich in fruits, vegetables, whole grains, lean proteins, and healthy fats. The Mediterranean or DASH diets are known to promote brain health and reduce the risk of dementia.",

        "Maintain social connections: Stay socially engaged by spending time with family, friends, or community groups. Social interaction stimulates the brain and helps reduce the risk of cognitive decline.",

        "Get enough quality sleep: Poor sleep can increase the risk of dementia. Aim for 7-9 hours of restful sleep each night, and address any issues like sleep apnea or insomnia.",

        "Manage stress: Chronic stress can negatively affect memory and brain health. Practice relaxation techniques such as meditation, deep breathing, or mindfulness to reduce stress levels.",

        "Keep learning: Continuing education or acquiring new skills, like learning a new language or playing an instrument, helps keep the brain active and builds cognitive reserve.",

        "Control chronic conditions: Manage health conditions like high blood pressure, diabetes, and high cholesterol, which are linked to increased dementia risk. Regular medical check-ups and proper treatment are key.",

        "Avoid smoking and excessive alcohol consumption: Smoking and heavy drinking are linked to a higher risk of dementia. Quitting smoking and drinking alcohol in moderation can help protect brain health.",

        "Stay hydrated: Dehydration can impair cognitive function, so make sure you drink enough water throughout the day to support brain health."
    ],
    "Very mild dementia": [
       "Stay mentally active: Engage in brain-challenging activities like puzzles, reading, crosswords, or learning new skills. Cognitive exercises can help slow memory decline.",

        "Create a daily routine: Establishing a consistent schedule for meals, medication, and activities can reduce confusion and make daily life more manageable.",

        "Use memory aids: Utilize tools like calendars, sticky notes, reminder apps, or even voice assistants to help with appointments, tasks, or medication schedules.",

        "Stay socially connected: Regular interaction with family, friends, or social groups can boost mood and cognitive function. Join community activities or consider virtual chats to stay connected.",

        "Exercise regularly: Physical activity, like walking, yoga, or light aerobics, supports brain health and improves overall well-being.",

        "Follow a healthy diet: A diet rich in fruits, vegetables, whole grains, and omega-3 fatty acids (like in fish) can support brain function. The Mediterranean diet is particularly beneficial for cognitive health.",

        "Get enough sleep: Aim for 7-9 hours of quality sleep per night. Good sleep is essential for memory consolidation and overall brain health.",

        "Manage stress: Practice relaxation techniques like deep breathing, meditation, or mindfulness to manage stress, which can exacerbate cognitive issues.",

        "Stay hydrated: Dehydration can impair cognitive function, so ensure you're drinking enough water throughout the day." ,     

        "Keep important items in the same place: Always placing essential items (like keys, phone, or wallet) in a designated spot helps avoid frustration and confusion when looking for them."
    ],
    "Mild dementia": [
        "Simplify tasks and break them into steps: For daily activities, break tasks into smaller, manageable steps, providing visual or verbal cues to stay on track.",

        "Use written reminders: Keep a calendar or whiteboard with daily tasks and appointments in a visible place to serve as a reminder for important events.",

        "Establish a consistent routine: Regular schedules reduce confusion. Try to follow a similar structure each day to help with memory recall and reduce anxiety.",

        "Label items around the house: Use labels on drawers, cupboards, and other areas to help locate frequently used items like utensils, clothes, or medications.",

        "Carry a notepad or smartphone: Write down important information, such as names, phone numbers, and addresses. Use a reminder app on your smartphone for added convenience.",

        "Use medication management tools: Utilize pill organizers or set alarms on a phone or watch to remember when to take medications.",

        "Stay socially engaged: Join support groups, attend community events, or participate in group activities. Social interactions can improve mood and cognitive function.",

        "Maintain a healthy diet and exercise routine: Regular physical activity like walking, swimming, or yoga, along with a diet rich in fruits, vegetables, and whole grains, can support both brain and body health.",

        "Ensure home safety: Reduce risks by making small modifications, such as installing grab bars, removing tripping hazards, and improving lighting to avoid accidents.",

        "Stay mentally stimulated: Engage in hobbies, such as playing card games, solving puzzles, painting, or listening to music. These activities stimulate the brain and promote mental well-being."
    ],

    "Moderate dementia": [
        "Establish a calm, structured routine: A regular daily schedule can reduce confusion and anxiety. Consistency with meals, activities, and sleep helps patients feel secure.",

        "Provide clear, simple instructions: When communicating, use short sentences and clear language. Break instructions into simple steps, offering one task at a time.",

        "Use visual cues and labels: Label doors, rooms, and objects around the house to help with orientation. Visual cues, like color-coded labels, can make navigation easier.",

        "Supervise activities: As judgment and decision-making become impaired, supervision during activities like cooking, driving, and using appliances ensures safety and prevents accidents.",

        "Create a safe home environment: Remove sharp objects, install locks on dangerous areas, ensure good lighting, and place grab bars in bathrooms. Secure loose rugs or cords that could cause falls.",

        "Promote independence with adaptive tools: Use dementia-friendly tools such as large-button phones, simplified remote controls, and easy-to-open containers to help patients manage daily tasks with less frustration.",

        "Encourage physical activity: Gentle exercises, like walking, stretching, or chair yoga, can improve mood and maintain mobility. Supervise activities to prevent wandering.",

        "Engage in familiar activities: Encourage participation in hobbies or activities that they have always enjoyed, such as gardening, listening to music, or looking through photo albums. Familiar tasks are comforting and stimulating.",

        "Offer choices: To maintain a sense of independence, offer simple, limited choices—such as \"Do you want tea or water?\"—rather than open-ended questions that may cause confusion.",

        "Monitor nutrition and hydration: People with moderate dementia may forget to eat or drink. Offer small, regular meals with finger foods if necessary, and provide reminders to stay hydrated."
    ]
}

# Function to build FAISS index for each classification
def build_faiss_index():
    # Dictionary to store indices and embeddings for each classification
    indices = {}
    embeddings_dict = {}

    # Loop through each classification and build an index
    for classification, docs in classification_to_docs.items():
        embeddings = model.encode(docs)  # Convert docs into embeddings

        # Create a FAISS index for the classification-specific documents
        index = faiss.IndexFlatL2(embeddings.shape[1])  # L2 distance
        index.add(np.array(embeddings))

        # Store the index and embeddings in the dictionary
        indices[classification] = index
        embeddings_dict[classification] = embeddings

    return indices, embeddings_dict

# Function to search the pre-built FAISS index based on the query and classification
def search_faiss_index(query, indices, classification):
    # Get the relevant index and documents for the selected classification
    index = indices.get(classification)

    if index is None:
        raise ValueError(f"No FAISS index found for classification: {classification}")

    # Convert query to embedding
    query_embedding = model.encode([query])

    # Search the FAISS index for the top matches (k=3)
    D, I = index.search(np.array(query_embedding), k=3)

    # Retrieve the relevant documents for the classification
    classification_docs = classification_to_docs.get(classification, [])

    # Retrieve the documents based on FAISS indices and remove duplicates
    relevant_docs = [classification_docs[i] for i in I[0]]

    # Remove duplicates by converting the list to a set and back to a list
    unique_docs = list(dict.fromkeys(relevant_docs))  # Ensure order is maintained

    return unique_docs
