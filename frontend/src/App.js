import React, { useState } from 'react';
import Chat from './components/Chat';  
import FileTab from './components/FileTab';  
import './App.css';  

function App() {
  const [activeTab, setActiveTab] = useState('chat'); 

  // Function to switch tabs
  const switchTab = (tab) => {
    setActiveTab(tab);
  };

  return (
    <div className="app-container">
      {/* Tab Buttons */}
      <div className="tabs">
        <button onClick={() => switchTab('chat')}>Chat & Upload</button>
        <button onClick={() => switchTab('files')}>Files</button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {activeTab === 'chat' && <Chat />}
        {activeTab === 'files' && <FileTab />}
      </div>
    </div>
  );
}

export default App;
