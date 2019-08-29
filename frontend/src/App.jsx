import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import ImageContainer from './ImageContainer';


function App() {
  const [apiData, setApiData] = useState(null);
  const [input, setInput] = useState('');

  function getDataRoutes() {
    setApiData('fetching');
    axios
      .get('http://localhost:5000/analyze', {
        params: {
          artist_name: input,
        },
      })
      .then((response) => {
        setApiData(response.data);
      });
  }

  return (
    <div className="App">
      <form>
        <input value={input} onInput={(e) => setInput(e.target.value)} />
        <button type="button" onClick={getDataRoutes}>Go</button>
      </form>
      <ImageContainer apiData={apiData} />
    </div>
  );
}

export default App;
