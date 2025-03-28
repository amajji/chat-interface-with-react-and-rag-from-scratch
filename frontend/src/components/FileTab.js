import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './FileTab.css';

function FileTab() {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [showFileDetails, setShowFileDetails] = useState(null); 

  // Fetch uploaded files from the server (and poll every 2 seconds to keep it updated)
  useEffect(() => {
    const fetchUploadedFiles = async () => {
      try {
        const response = await axios.get('http://localhost:8000/get_uploaded_files/');
        setUploadedFiles(response.data);
      } catch (error) {
        console.error("Error fetching files:", error);
        alert('Failed to fetch uploaded files.');
      }
    };

    fetchUploadedFiles(); 

    // Poll every 2 seconds to get updated file details
    const intervalId = setInterval(fetchUploadedFiles, 2000);

    // Cleanup the interval when the component is unmounted
    return () => clearInterval(intervalId);
  }, []);

  // Polling function to update chunks in real-time
  useEffect(() => {
    let intervalId;

    if (showFileDetails) {
      intervalId = setInterval(async () => {
        try {
          const response = await axios.get(`http://localhost:8000/get_file_chunks/${showFileDetails.filename}`);
          const updatedChunks = response.data.chunks;  

          // Update the file details with the new chunks
          setShowFileDetails((prevDetails) => ({
            ...prevDetails,
            chunks: updatedChunks
          }));
        } catch (error) {
          console.error("Error fetching chunks:", error);
        }
      }, 2000); 

      // Clean up the interval on component unmount or when file details change
      return () => clearInterval(intervalId);
    }

    return undefined; 
  }, [showFileDetails]);

  // Handle the start of file processing
  const handleStartProcessing = (file) => {
    // If the file is already being processed, do nothing
    if (file.status === 'Processing') return;

    // Always trigger processing (even if file is "Done")
    setUploadedFiles((prevFiles) =>
      prevFiles.map((f) =>
        f.filename === file.filename ? { ...f, status: 'Processing' } : f
      )
    );

    // Send request to backend to process the file
    const fileLocation = { file_location: `http://localhost:8000/static/${file.filename}`, filename: file.filename };

    // Make the API call to trigger processing
    axios
      .post('http://localhost:8000/process_file/', fileLocation)
      .then((response) => {
        // After processing is complete, set status to 'Done' (update frontend immediately)
        setUploadedFiles((prevFiles) =>
          prevFiles.map((f) =>
            f.filename === file.filename ? { ...f, status: 'Done' } : f
          )
        );
      })
      .catch((error) => {
        console.error('Error processing file:', error);
        alert('Failed to process the file.');

        // If there's an error, reset the status to 'Not started' (update frontend immediately)
        setUploadedFiles((prevFiles) =>
          prevFiles.map((f) =>
            f.filename === file.filename ? { ...f, status: 'Not started' } : f
          )
        );
      });
  };

  // Handle showing the file details
  const handleShowDetails = (file) => {
    // Parse the chunks JSON string into a JavaScript array (fallback to empty array if no chunks)
    const parsedChunks = file.chunks ? JSON.parse(file.chunks) : [];
    setShowFileDetails({ ...file, chunks: parsedChunks });  
  };

  // Close the file details modal
  const handleCloseDetails = () => {
    setShowFileDetails(null);  
  };

  // Toggle the 'take_into_account' status between 'Enable' and 'Disable'
  const handleToggleTakeIntoAccount = async (file) => {
    const newStatus = file.take_into_account === 'Disable' ? 'Enable' : 'Disable';
    
    try {
      // Send request to backend to update the take_into_account status
      await axios.post('http://localhost:8000/update_take_into_account/', {
        file_location: `http://localhost:8000/static/${file.filename}`,
        filename: file.filename
      });

      // Update the frontend with the new status
      setUploadedFiles((prevFiles) =>
        prevFiles.map((f) =>
          f.filename === file.filename ? { ...f, take_into_account: newStatus } : f
        )
      );
    } catch (error) {
      console.error('Error toggling take_into_account:', error);
      alert('Failed to update the take_into_account status.');
    }
  };

  return (
    <div className="file-tab-container">
      <h3>Uploaded Files</h3>
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Extension</th>
            <th>Date of Upload</th>
            <th>Details</th> {/* Moved Details column here */}
            <th>Start Processing</th> {/* Column for the start button */}
            <th>Status</th> {/* Column for the status icon */}
            <th>Take into account</th> {/* New column for Enable/Disable */}
          </tr>
        </thead>
        <tbody>
          {uploadedFiles.length > 0 ? (
            uploadedFiles.map((file, index) => (
              <tr key={file.filename}>
                <td>
                  <a href={`http://localhost:8000/static/${file.filename}`} target="_blank" rel="noopener noreferrer">
                    {file.filename}
                  </a>
                </td>
                <td>{file.extension}</td>
                <td>{file.upload_date}</td>
                <td>
                  {/* Eye icon for showing file details */}
                  <button
                    onClick={() => handleShowDetails(file)}
                    title="View Details"
                    className="eye-icon"
                  >
                    👁️
                  </button>
                </td>
                <td>
                  {/* "Start Processing" column - Always show the start button */}
                  <button 
                    onClick={() => handleStartProcessing(file)} 
                    className="start-icon"
                    title="Start Processing"
                    disabled={file.status === 'Processing'}  
                  >
                    {file.status === 'Processing' ? '⏳' : '▶️'}  {/* Show ⏳ when processing */}
                  </button>
                </td>
                <td>
                  {/* "Status" column - shows Processing or Done icon */}
                  {file.status === 'Processing' ? (
                    <span role="img" aria-label="Processing" style={{ fontSize: '20px', color: '#f39c12' }}>⏳</span> 
                  ) : file.status === 'Done' ? (
                    <span role="img" aria-label="Done" style={{ fontSize: '20px', color: 'green' }}>✅</span> 
                  ) : (
                    <span role="img" aria-label="Not started" style={{ fontSize: '20px', color: '#007bff' }}>❔</span>  
                  )}
                </td>
                <td>
                  {/* "Enable/Disable" toggle switch */}
                  <div 
                    onClick={() => handleToggleTakeIntoAccount(file)} 
                    className={`switch ${file.take_into_account === 'Enable' ? 'enabled' : 'disabled'}`}
                    title={file.take_into_account === 'Disable' ? 'Enable' : 'Disable'}
                  >
                    <div className={`circle ${file.take_into_account === 'Enable' ? 'right' : 'left'}`} />
                  </div>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan="7">No files uploaded yet.</td>
            </tr>
          )}
        </tbody>
      </table>

      {/* Modal for displaying file details */}
      {showFileDetails && (
        <div className="file-details-modal">
          <div className="modal-content">
            <span className="close-button" onClick={handleCloseDetails}>×</span>
            <h3>File Details</h3>
            <p><strong>Filename:</strong> {showFileDetails.filename}</p>
            <p><strong>Extension:</strong> {showFileDetails.extension}</p>
            <p><strong>Upload Date:</strong> {showFileDetails.upload_date}</p>
            <p><strong>Summary:</strong> {showFileDetails.summary}</p>
            <p><strong>Status:</strong> {showFileDetails.status}</p>
            <p><strong>Chunks:</strong></p>
            {/* Display chunks in a scrollable container */}
            <div style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid #ddd', padding: '10px', borderRadius: '5px', backgroundColor: '#f9f9f9' }}>
              <ul>
                {showFileDetails.chunks && showFileDetails.chunks.length > 0 ? (
                  showFileDetails.chunks.map((chunk, index) => (
                    <li key={index}>{chunk.chunk_text}</li>  
                  ))
                ) : (
                  <li>No chunks available</li>  
                )}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default FileTab;
