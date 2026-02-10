import React, {useEffect, useState} from 'react';
import axios from 'axios';

export default function App() {
  const [svg, setSvg] = useState(null);

  useEffect(() => {
    async function fetchSvg(){
      try {
        const resp = await axios.get('/api/floorplans/svg_preview/');
        setSvg(resp.data);
      } catch (e) {
        console.error('SVG preview error', e);
      }
    }
    fetchSvg();
  }, []);

  return (
    <div style={{padding: 20}}>
      <h2>Blueprint Editor (MVP)</h2>
      <div style={{marginBottom: 12}}>
        <a href="/realtinytalk.html" target="_blank">Open realTinyTalk editor (stub)</a>
      </div>
      <div style={{border: '1px solid #ddd', height: 420, width: 420}}>
        {svg ? <div dangerouslySetInnerHTML={{__html: svg}} /> : <div style={{padding: 20}}>Loading preview…</div>}
      </div>
    </div>
  );
}
