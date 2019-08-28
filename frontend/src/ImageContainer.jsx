import React from 'react';

const host = 'http://localhost:5000/';

function recurseForPaths(item) {
  if (typeof item === 'string') {
    return (
      <img style={{ width: '100%' }} key={item} src={host + item} alt="" />
    );
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
    return <div />;
  }
  return <div />;
};

export default ImageContainer;
