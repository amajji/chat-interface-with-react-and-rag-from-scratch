<h1 align="center">RAGBot: Chat Interface with React and RAG from Scratch</h1>

Data scientist | [Anass MAJJI](https://www.linkedin.com/in/anass-majji-729773157/)
***
<p align="center">
<img src="/assets/rag_bot_short.png" alt="RAGBot Logo" />
</p>


<!-- <p align="center">
<a href="https://www.producthunt.com/posts/simba-2?embed=true&utm_source=badge-featured&utm_medium=badge&utm_souce=badge-simba&#0045;2" target="_blank"><img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=863851&theme=light&t=1739449352356" alt="Simba&#0032; - Connect&#0032;your&#0032;Knowledge&#0032;into&#0032;any&#0032;RAG&#0032;based&#0032;system | Product Hunt" style="width: 250px; height: 54px;" width="250" height="54" /></a>
</p> -->

<p align="center">

## :monocle_face: Overview


This project provides a real-time Chat Interface powered by a custom-built Retrieval Augmented Generation (RAG) pipeline, developed from scratch. It incorporates both frontend (React) and backend (FastAPI) components, supporting file uploads, document chunking, embedding generation, and semantic search for efficient document retrieval.

The system enables plugging any LLM for document retrieval and allows efficient search through a collection of documents. The project includes functionality for document processing and chunk management, stored in an SQLite database.

## :fire: Demo of the Dashboard

<p align="center">
<img src="/assets/chat.PNG"  />
</p>

<p align="center">
<img src="/assets/take_into_account.PNG"  />
</p>


## 🌟 Features

The flow works as follows:

1. **File Upload** 📤: Allows users to upload documents easily to the backend.

2. **Document Chunking** ✂️: Automatically splits documents into smaller, manageable chunks for more efficient processing and analysis.

3. **Embedding Generation** 🧠: Uses transformer models to compute high-quality embeddings for each document chunk.

4. **Similarity Search** 🔍: Enables querying of document chunks and returns the most relevant ones based on cosine similarity with the input query.

5. **Customizable File Processing** ⚙️: Users can toggle whether files should be considered for processing through the take_into_account flag.

6. **Database Integration** 🗄️: Uses SQLite and SQLAlchemy for storing file metadata, chunk data, and processing status, ensuring efficient data management and querying.

7. **RAG System** 🔗: Developed from scratch, the RAG system allows for flexible integration with any LLM, providing advanced document retrieval and query answering capabilities.


## 🛠️ Technologies Used

- **Backend**: FastAPI ⚡️, Uvicorn 🚀 (Python 🐍)
- **Frontend**: React 🔵, Axios 🌐
- **Database**: SQLite 🗄️, SQLAlchemy 🔗




## 🚀 Getting Started 
1. Clone the repository
```bash
git clone https://github.com/amajji/chat-interface-with-react-and-rag-from-scratch.git
cd chat-interface-with-react-and-rag-from-scratch
```

2. Create a Virtual Environment 
```bash
python -m venv chatbotvenv
chatbotvenv/Scripts/activate
```

3. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

4. Install Frontend Dependencies
```bash
npm install
```

This will:

  - Start the backend (FastAPI) server using uvicorn.
  - Start the frontend React development server.

The backend will be available at http://127.0.0.1:8000, and the frontend React app will be available at http://localhost:3000.


## Contributing 🤝
Contributions to this project are welcome! Feel free to submit issues or pull requests for improvements.

## :mailbox_closed: Contact
For any information, feedback or questions, please [contact me][anass-email]