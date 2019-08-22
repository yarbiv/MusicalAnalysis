import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [apiData, setApiData] = useState(null);

  function getDataRoutes(artistName) {
    axios
      .get('http://localhost:5000/analyze', {
        params: {
          artist_name: artistName,
        },
      })
      .then((response) => {
        console.log(response);
        setApiData(response);
      });
  }

  useEffect(getDataRoutes);

  return (
    <div className="App">
      <header className="App-header" />
      <p>{apiData ? apiData.length : 'Loading'}</p>
    </div>
  );
}

export default App;
