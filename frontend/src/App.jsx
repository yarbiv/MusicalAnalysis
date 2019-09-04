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
        const responsePath = response.data.save_path;
        async function refresh() {
          const response = await axios.get(`${host}${responsePath}`);
          if (response.body.status) {
            setTimeout(refresh, 5000);
          }
          else {
            setApiData(response.body);
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
