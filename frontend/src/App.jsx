import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import ClipLoader from 'react-spinners/ClipLoader';
import { css } from '@emotion/core';
import ImageContainer from './ImageContainer';

const override = css`
  display: block;
  margin: 0 auto;
  border-color: red;
`;

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
        console.log(response);
        setApiData(response.data);
      });
  }

  return (
    <div className="App">
      <header className="App-header">
        <form>
          <input value={input} onInput={(e) => setInput(e.target.value)} />
          <button type="button" onClick={getDataRoutes}>Go</button>
          <ImageContainer apiData={apiData} />
          <ClipLoader
            css={override}
            loading={apiData === 'fetching'}
          />
        </form>
      </header>
    </div>
  );
}

export default App;
