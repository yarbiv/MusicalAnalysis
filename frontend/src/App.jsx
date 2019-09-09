import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import ImageContainer from './ImageContainer';

const host = 'http://api.musicalanalysis.yoavarbiv.com/';

function App() {
  const [apiData, setApiData] = useState(null);
  const [input, setInput] = useState('');

  function handleKeyDown(e) {
    if (e.key === "Enter") {
      getDataRoute();
      e.preventDefault();
    }
  }

  function getDataRoute() {
    if (apiData === 'fetching') {
      return;
    }
    setApiData('fetching');
    axios
      .get(`${host}analyze`, {
        params: {
          artist_name: input,
        },
      })
      .then((response) => {
        const job_id = response.data.job_id;
        async function refresh() {
          const process_response = await axios.get(`${host}static/${job_id}/results.json`);
          if (process_response.data.status && process_response.data.status === 'processing') {
            setTimeout(refresh, 5000);
          } else {
            setApiData(process_response.data);
          }
        }
        refresh();
      });
  }

  return (
    <div className="App">
      <h1>MusicalAnalysis</h1>
      <h2>Take a deep dive into your favourite music by typing in an artist's name!</h2>
      <form>
        <input value={input} onInput={(e) => setInput(e.target.value)} onKeyDown={handleKeyDown} />
        <button type="button" onClick={getDataRoute} >Go</button>
      </form>
      <ImageContainer apiData={apiData} />
    </div>
  );
}

export default App;
