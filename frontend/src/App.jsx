import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import ImageContainer from './ImageContainer';

const host = 'http://localhost:5000/';

function App() {
  const [apiData, setApiData] = useState(null);
  const [input, setInput] = useState('');



  function getDataRoute() {
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
      <form>
        <input value={input} onInput={(e) => setInput(e.target.value)} />
        <button type="button" onClick={getDataRoute}>Go</button>
      </form>
      <ImageContainer apiData={apiData} />
    </div>
  );
}

export default App;
