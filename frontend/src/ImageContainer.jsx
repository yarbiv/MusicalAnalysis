import ClipLoader from 'react-spinners/ClipLoader';

import { css } from '@emotion/core';
import React from 'react';

const host = 'http://localhost:5000/';

const override = css`
  display: block;
  margin: 0 auto;
  border-color: red;
`;

function getExt(filename) {
  return filename.split('.').pop();
}

function getNameFromPath(path) {
  return path.split('/').pop();
}

function recurseForPaths(item) {
  if (typeof item === 'string') {
    if (getExt(item) === 'png') {
      return (
        <img style={{ width: '100%' }} key={item} src={host + item} alt="" />
      );
    }
    if (getExt(item) === 'html') {
      return (
        <iframe key={item} src={host + item} title={getNameFromPath(item)} />
      );
    }
  }
  return (
    <div>
      {item.map((subitem) => recurseForPaths(subitem))}
    </div>
  );
}
const ImageContainer = (props) => {
  const { apiData } = props;
  if (apiData && apiData !== 'fetching') {
    return (
      <div style={{ width: '60vw' }}>
        {recurseForPaths(apiData)}
      </div>
    );
  }
  if (apiData === 'fetching') {
    return (
      <ClipLoader
        css={override}
        loading={apiData === 'fetching'}
      />
    );
  }
  return <div />;
};

export default ImageContainer;
