import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';

function AdminPortal() {
  const [cases, setCases] = useState([]);
  const [newCaseName, setNewCaseName] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    // Fetch existing cases from the server
    fetch('/manage/api/cases')
      .then(response => response.json())
      .then(data => setCases(data.cases || []))
      .catch(error => console.error('Error fetching cases:', error));
  }, []);

  const createCase = async () => {
    if (!newCaseName) {
      setMessage('Case name cannot be empty.');
      return;
    }

    try {
      const response = await fetch('/manage/api/cases', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newCaseName }),
      });

      if (response.ok) {
        const result = await response.json();
        setCases([...cases, result.case]);
        setMessage('Case created successfully!');
        setNewCaseName('');
      } else {
        const error = await response.json();
        setMessage(`Error: ${error.message}`);
      }
    } catch (error) {
      console.error('Error creating case:', error);
      setMessage('An error occurred while creating the case.');
    }
  };

  return (
    <div className="admin-container">
      <h1 className="text-3xl font-bold text-center text-blue-600 mb-4">Admin Portal</h1>
      <div className="form-container">
        <h2>Create a New Case</h2>
        <input
          type="text"
          value={newCaseName}
          onChange={(e) => setNewCaseName(e.target.value)}
          placeholder="Enter case name"
          className="w-full border border-gray-300 p-2 rounded-lg mb-4"
        />
        <button onClick={createCase} className="btn-primary">
          Create Case
        </button>
        {message && <div className="mt-4 text-center">{message}</div>}
      </div>
      <h2 className="mt-8">Existing Cases</h2>
      <ul className="case-list">
        {cases.map((caseItem, index) => (
          <li key={index}>{caseItem}</li>
        ))}
      </ul>
    </div>
  );
}

ReactDOM.render(<AdminPortal />, document.getElementById('react-app'));