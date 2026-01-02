import React from 'react';
import { Athena } from './components';

function App() {
  return (
    <Athena
      onRecordingStart={() => console.log('Recording started')}
      onRecordingEnd={(duration) => console.log(`Recording ended: ${duration}ms`)}
      onModeChange={(mode) => console.log(`Mode changed: ${mode}`)}
      size={350}
    />
  );
}

export default App;
