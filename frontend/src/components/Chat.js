import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './Chat.css';


function Chat() {
  const [message, setMessage] = useState('');  
  const [chatHistory, setChatHistory] = useState([]);  
  const [file, setFile] = useState(null);  
  const chatBoxRef = useRef(null); 

  // Function to handle sending messages
const handleSendMessage = async () => {
  if (message.trim() || file) {  
    const formData = new FormData();
    formData.append("message", message);  
    if (file) formData.append("file", file);  

    try {
      // Send both the message and file to the backend
      const response = await axios.post('http://localhost:8000/send_message_and_upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Update chat history with user message, bot response, and file info (if any)
      setChatHistory([
        ...chatHistory,
        {
          user: message,
          bot: response.data.message,  
          file: response.data.file, 
        },
      ]);
      setMessage('');
      setFile(null);
    } catch (error) {
      console.error("Error sending message or uploading file:", error);
      alert('Failed to send message or upload file.');
    }
  }
};


  // Function to handle file selection and update the textarea with the file name
  const handleAddFile = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setMessage(selectedFile.name); 
    }
  };

  // Retrieve chat history from sessionStorage when the component mounts (persist across tabs but reset on reload)
  useEffect(() => {
    const savedChatHistory = JSON.parse(sessionStorage.getItem('chatHistory'));
    if (savedChatHistory) {
      setChatHistory(savedChatHistory);
    }
  }, []);

  // Store chat history in sessionStorage whenever it changes
  useEffect(() => {
    if (chatHistory.length > 0) {
      sessionStorage.setItem('chatHistory', JSON.stringify(chatHistory));
    }
  }, [chatHistory]);

  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [chatHistory]);
  

  return (
    <div className="chat-container">
      {/* Chat messages display */}
      <div className="chat-box" ref={chatBoxRef}>
        {chatHistory.map((chat, index) => (
          <div key={index} className="message">
            <div className="user-message">{chat.user}</div>
            <div className="bot-message">{chat.bot}</div>
            {/* If a file was uploaded, show the file details */}
            {chat.file && (
              <div className="file-info">
                <a href={chat.file.file_url} target="_blank" rel="noopener noreferrer">
                  View Uploaded File: {chat.file.filename}
                </a>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Input area for typing messages and file upload */}
      <div className="input-area">
        {/* Hidden file input field */}
        <input
          type="file"
          onChange={handleAddFile}
          style={{ display: 'none' }}
          id="file-input"
        />
        <button onClick={() => document.getElementById('file-input').click()}>+Add</button>

        {/* Textarea to display message or file name */}
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type a message or select a file..."
        />

        {/* Send button to send message and file */}
        <button onClick={handleSendMessage} disabled={!message.trim() && !file}>Send</button>
      </div>
    </div>
  );
}

export default Chat;
