from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import shutil
from pathlib import Path
import sqlite3
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import asyncio
import os
from transformers import AutoTokenizer, AutoModel
from .rag.rag import get_chunks
from .db.database import File, get_db, DATABASE_URL
import openai 
import json



# Assuming you have a summary_function that generates the file summary
def summary_function(file_location):
    # Your summary logic goes here
    return "This is the file summary generated by summary_function."

# Directory to store uploaded files
UPLOAD_DIR = Path("backend/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Define FastAPI app
app = FastAPI()

# OpenAI API key (securely set your API key, do not hardcode in production)
openai.api_key = "your-openai-api-key"

# Allow CORS for all domains (you can limit to specific origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development purposes)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Serve static files (uploaded files)
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")

# Name of the model
model_name = "BAAI/bge-small-en-v1.5"

# Tokenizer initilization
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Model initilization
model = AutoModel.from_pretrained(model_name)


async def get_openai_response(message: str):
    try:
        # # Call OpenAI's API to generate a response for the given message
        # response = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",  # You can use "gpt-4" if available
        #     messages=[{"role": "user", "content": message}],
        #     max_tokens=200
        # )
        # # Extract the bot's response from the OpenAI API response
        # bot_message = response['choices'][0]['message']['content']
        return message
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return "Sorry, I couldn't generate a response at the moment."
    

@app.post("/send_message_and_upload/")
async def send_message_and_upload(
    message: str = Form(...),  # Message from the user
    file: Optional[UploadFile] = None,  # Optional file
    db: Session = Depends(get_db),  # Get the database session
):
    file_info = None
    if file:
        # Save the uploaded file
        file_location = UPLOAD_DIR / file.filename

        print(f"file_location -- : {file_location}")
        with open(file_location, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Extract file extension
        file_extension = file.filename.split('.')[-1]

        # Process the file and get its summary
        file_summary = summary_function(file_location)
        
        # Get the file's last modified date (upload date)
        upload_date = datetime.fromtimestamp(file_location.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")

        # Check if the file already exists in the database
        existing_file = db.query(File).filter(File.filename == file.filename).first()

        if not existing_file:
            # Store the file information in the database
            db_file = File(
                filename=file.filename,
                extension=file_extension,
                file_location=str(file_location),
                upload_date=upload_date,
                summary=file_summary,
                status='Not started',
                chunks=json.dumps([]),
                take_into_account='Disable'
            )
            db.add(db_file)
            db.commit()
            db.refresh(db_file)

        # Prepare file info to return
        file_info = {
            "filename": file.filename,
            "extension": file_extension,
            "upload_date": upload_date,
            "file_location": str(file_location),
            "file_url": f"http://localhost:8000/static/{file.filename}",
            "summary": file_summary,
            "status": 'Not started',  
            "chunks": [],
            "take_into_account": 'Disable',
        }

    # Simulate a bot response (for demonstration purposes)
    # bot_response = f"Bot received: {message}"

    # Get OpenAI bot response based on the user message
    bot_response = await get_openai_response(message)

    # Combine the message and file information (if available) in the response
    return JSONResponse(content={
        "message": bot_response,  # The bot's response to the user message
        "file": file_info  # Information about the uploaded file (if any)
    })


# Define a model to accept the file location
class FileLocation(BaseModel):
    filename: str  # Ensure that the 'filename' is part of the request payload
    file_location: str  # Ensure 'file_location' is passed as well

# This is a placeholder for the actual file processing logic
async def process_the_file(
        file_path: str,
        filename: str,
        db: Session):
    # Simulate file processing (this is where you would process the file)
    print(f"Processing file at {file_path}")

    ## Get the chunks of the file
    doc_chunks = get_chunks(file_path, tokenizer)

    if doc_chunks:
        # Convert the chunks dictionary into a list of dictionaries to store in JSON format
        chunks_list = [{"chunk_id": chunk_id, "chunk_text": chunk_data["text"]} for chunk_id, chunk_data in doc_chunks.items()]

        print(f"Yesss filename{filename}")

        # Query the file by filename
        db_file = db.query(File).filter(File.filename == filename).first()

        # If the file is not found in the database, raise an error
        if not db_file:
            raise HTTPException(status_code=404, detail=f"File '{filename}' not found in the database")

        print(f"File found. Saving chunks...")

        # Save the chunks as JSON in the 'chunks' column
        db_file.chunks = json.dumps(chunks_list)
        db.commit()  # Save changes to the database

    print("chunks -- : ", doc_chunks)

    await asyncio.sleep(5)  # Simulate a delay (e.g., for processing)
    return True  # Simulate successful processing


@app.post("/process_file/")
async def process_file(file_location: FileLocation, db: Session = Depends(get_db)):
    file_path = file_location.file_location  # Extract file location from the request
    filename = file_location.filename  # Extract filename from the request
    try:
        # Query the file by filename
        file = db.query(File).filter(File.filename == filename).first()
        
        if file:
            # Set the status to 'Processing'
            file.status = "Processing"
            db.commit()
            
            # Process the file (assume a `process_the_file()` function exists)
            if await process_the_file(file.file_location, filename, db):
                file.status = "Done"
                db.commit()
                return {"status": "success", "message": "File processed successfully"}
            else:
                raise HTTPException(status_code=500, detail="Error processing file")
        else:
            raise HTTPException(status_code=404, detail="File not found")

    except Exception as e:
        if file:
            file.status = "Failed"
            db.commit()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.post("/update_take_into_account/")
async def update_take_into_account(file_location: FileLocation, db: Session = Depends(get_db)):
    file_path = file_location.file_location  # Extract file location from the request
    filename = file_location.filename  # Extract filename from the request
    try:
        # Fetch the file from the database
        file = db.query(File).filter(File.filename == filename).first()

        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Update the take_into_account status
        if file.take_into_account == "Enable":
            file.take_into_account = "Disable"
        else:
            file.take_into_account = "Enable"

        db.commit()

        return {"status": "success", "message": f"File take_into_account updated to {file.take_into_account}"}
    except Exception as e:
        db.rollback()  # In case of an error, ensure the transaction is rolled back
        raise HTTPException(status_code=500, detail=f"Error updating take_into_account: {str(e)}")


# Endpoint for getting the list of uploaded files
@app.get("/get_uploaded_files/")
async def get_uploaded_files(db: Session = Depends(get_db)):
    # Fetch all files from the database
    files = db.query(File).all()
    file_list = []
    for file in files:
        file_list.append({
            "filename": file.filename,
            "extension": file.extension,
            "upload_date": file.upload_date,
            "summary": file.summary,
            "status": file.status,
            "chunks": file.chunks,
            "take_into_account": file.take_into_account,
        })
    return file_list
