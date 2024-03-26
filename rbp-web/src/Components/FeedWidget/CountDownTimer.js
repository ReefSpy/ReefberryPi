import React, { useState, useEffect } from 'react';

const CountdownTimer = ({time}) => {
    const [countdown, setCountdown] = useState(time);
  
    useEffect(() => {
      const interval = setInterval(() => {
        if (countdown > 0) {
          setCountdown(countdown - 1);
        }
      }, 1000);
  
      return () => clearInterval(interval);
    }, [countdown]);
  
    // const handleRestart = () => {
    //   setCountdown(time); // Reset countdown to 30 seconds
    // };
  
    return (
      <div>
        Time: {countdown}s
        {/* <button onClick={handleRestart}>Restart Timer</button> */}
      </div>
    );
  }

  export default CountdownTimer;