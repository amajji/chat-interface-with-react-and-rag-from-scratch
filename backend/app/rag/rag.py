import os
import re
import numpy as np
import uuid
import torch
import json
import openai




def get_chunks(file_path, tokenizer, separator=" ", para_seperator="\n\n", chunk_size = 100):
    """
    This function generates chunks of maximum size chunk_size for each document. 
    Input : 
        - file_path: Path's document
        - tokenizer: used to split each word into tokens

    Output:
        - Dictonary that contains chunk's ids and their corresponding texts. 
    """ 
    try:
        print(f"Start processing file: {file_path}")

        # Dictonary of chunks for each document
        doc_chunks = {}

        # Full file's name
        base = os.path.basename(file_path)

        # Only file's name without extension
        sku = os.path.splitext(base)[0]

        # Open and read the content of the file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            text = file.read()

        # Split text into paragraphs
        paragraphs = re.split(para_seperator, text)
        for paragraph in paragraphs:

            # List to store the chunks of each paragraph
            chunks_parag = []

            # Split each paragraph into words
            words = re.split(separator, paragraph.strip())

            # Initialize each chunk
            sub_chunk = ''

            for word in words:
                if sub_chunk:
                    # Check the number sub_chunk's tokens doesn't exceed chunk_size
                    if len(tokenizer.tokenize(sub_chunk)) < chunk_size:
                        sub_chunk = sub_chunk + separator + word

                    else: 
                        # Append sub_chunk and initilize it with the next word 
                        chunks_parag.append(sub_chunk)
                        sub_chunk = word + separator
                else:
                    # Initilialize sub_chunk with the first word
                    sub_chunk = word + separator

            if sub_chunk:
                # Append sub_chunk for each paragraph
                chunks_parag.append(sub_chunk)

            for chunk_item in chunks_parag:
                if chunk_item.strip():
                    
                    # Generate unique ID for each chunk and save it in doc_chunks
                    chunk_id = str(uuid.uuid4())
                    doc_chunks[chunk_id] = {"text": chunk_item, "metadata": {"file_name": sku}}
        return doc_chunks

    except Exception as e:
        print(f"Error getting chunks from file: {e}")
        return None
    

    


def document_map_embedding(dict_doc_store, tokenizer, model):
    """
    This function maps dict_doc_store which contains text chunks with their embeddings.  
    """
    dict_map_embeddings = {}  # Initialize a dictionary to hold all chunk embeddings

    for chunk_id, chunk_content in dict_doc_store.items():
        # Extract the text content of the chunk
        chunk_text = chunk_content.get("text")  # Use .get to avoid key errors

        #print(f"** Chunk ID: {chunk_id} - Chunk Text: {chunk_text}")

        # Tokenize the chunk text
        inputs = tokenizer(chunk_text, return_tensors="pt", padding=True, truncation=True)

        with torch.no_grad():
            # Get the embeddings for the chunk text
            embeddings = model(**inputs).last_hidden_state.mean(dim=1).squeeze().tolist()
            #print(f"Embeddings for {chunk_id}: {embeddings}")

        # Map the chunk ID with its embeddings
        dict_map_embeddings[chunk_id] = embeddings

    return dict_map_embeddings



def save_data(path, data):
    """
    This function saves data on path
    """
    with open(path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Save data on {path}")


def load_data(path):
    """
    This function loads data from path
    """
    if not os.path.exists(path):
        print(f"File '{path}' does not exist.")
        return None
    with open(path, 'r') as f:
        data = json.load(f)
    print(f"Load data from {path}")
    return data


def query_compute_embeddings(query, tokenizer, model):
    """
    This function compute the embeddings of the input query
    """
    # Transform the query into tokens
    query_inputs = tokenizer(query, return_tensors="pt", padding=True, truncation=True)

    with torch.no_grad():
        # Get the embeddings of the query from its tokens
        query_embeddings = model(**query_inputs).last_hidden_state.mean(dim=1).squeeze().tolist()

    return query_embeddings


def compute_cosinus_similarity(query_embeddings, chunk_embeddings):
    """
    This function computes the cosinus similarity score between two vectors.
    It takes into parameters query and chunk embeddings's vectors
    """
    # Compute the dot product
    dot_product = np.dot(query_embeddings, chunk_embeddings)

    # Normalize both query embeddings and chunks vectors
    query_embeddings_norm = np.linalg.norm(query_embeddings)
    chunk_embeddings_norm = np.linalg.norm(chunk_embeddings)

    # If one of the norms is null return 0
    if query_embeddings_norm == 0 or chunk_embeddings_norm == 0:
        return 0
    
    else:
        return dot_product/(query_embeddings_norm * chunk_embeddings_norm)


def select_top_k_chunks(query_embeddings, dict_map_documents, top_k = 3):
    """
    This function selects the top_k relevent chunks from the vector database based on the score similarity 
    between each chunk's and query's embeddings.
    """
    # Dictionary to store similarity scores
    dict_similarity_score = {}
    for doc_id, doc_content in dict_map_documents.items():
        for chunk_id, chunk_embeddings in doc_content.items():
            # For each doc and chunk compute the similarity score
            dict_similarity_score[(doc_id, chunk_id)] = compute_cosinus_similarity(query_embeddings, chunk_embeddings)

    # Sort the dictionary and select the top_k chunks with the highest scores
    retreived_top_k = sorted(dict_similarity_score.items(), key=lambda item: item[1], reverse=True)[:top_k]

    # Get their correspondings texts
    top_k_result = [(doc_id, chunk_id, score) for ((doc_id, chunk_id), score) in retreived_top_k]
    
    return top_k_result


def retreive_chunks_content(top_k_result, dict_doc_store):
    """
    Retreive the chunk with the highest score
    """
    if top_k_result:
        # Select the first chunk
        first_element = top_k_result[0]

        # Get doc'ID
        doc_id = first_element[0]

        # Get chunk's ID
        chunk_id = first_element[1]

        # Return the associated text of the chunk's ID
        return dict_doc_store[doc_id][chunk_id]
    else: 
        return None


def generate_llm_response(query, relevent_chunks):
    """
    This function generates responses based on the query and retrieved chunks using OpenAI's API.
    """
    if relevent_chunks:
        # Create the prompt using the provided query and relevant chunks
        template = f"""
        You are an intelligent search engine. You will be provided with some retrieved context, as well as the user's query.

        Your job is to understand the request and answer based on the retrieved context. If you can't find the answer, you can say "I don't know".

        Here is the retrieved context:
        {relevent_chunks['text']}

        Here is the user's query:
        {query}
        """
    else:
        # Create the prompt using the provided query and relevant chunks
        template = f"""
        You are an intelligent search engine. Your job is to understand the request and answer based on your knowledge If you can't find the answer, you can say "I don't know".
        Here is the user's query:
        {query}
        """

    # # Call OpenAI's API to generate a response for the given message
    # response = openai.ChatCompletion.create(
    #     model="gpt-3.5-turbo",  # Use the model passed as argument (e.g., "gpt-3.5-turbo")
    #     messages=[{"role": "user", "content": template}],
    #     max_tokens=200
    # )

    # # Extract the bot's response from the OpenAI API response
    # bot_message = response['choices'][0]['message']['content']

    # print("LLM Response:", bot_message)

    # if not bot_message:
    #     print("No response generated by LLM.")
    
    # return bot_message
    return template