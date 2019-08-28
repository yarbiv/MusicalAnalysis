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
        setApiData(response.data);
      });
  }

  return (
    <div className="App">
      <form>
        <input value={input} onInput={(e) => setInput(e.target.value)} />
        <button type="button" onClick={getDataRoutes}>Go</button>
        <ClipLoader
          css={override}
          loading={apiData === 'fetching'}
        />
      </form>
      <ImageContainer apiData={apiData} />
    </div>
  );
}

export default App;
