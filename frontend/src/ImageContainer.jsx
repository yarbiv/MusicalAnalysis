import ClipLoader from 'react-spinners/ClipLoader';

import { css } from '@emotion/core';
import React from 'react';

const host = 'http://api.musicalanalysis.yoavarbiv.com/';

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

function onLoad() {
  document.domain = "yoavarbiv.com";
  const iframes = document.getElementsByTagName('iframe');
  Array.from(iframes).forEach((iframe) => {
    iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';
  });
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
        <iframe key={item} src={host + item} title={getNameFromPath(item)} onLoad={onLoad} frameBorder='0px' />
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
