import { useState, useEffect, useRef } from 'react';

export const useTransactionStream = () => {
  const [latestTransaction, setLatestTransaction] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  useEffect(() => {
    let reconnectCount = 0;
    
    const connect = () => {
      wsRef.current = new WebSocket('ws://localhost:8000/ws/transactions');
      
      wsRef.current.onopen = () => {
        setIsConnected(true);
        reconnectCount = 0;
      };
      
      wsRef.current.onmessage = (event) => {
        try {
          const tx = JSON.parse(event.data);
          setLatestTransaction(tx);
        } catch (e) {
          console.error('Error parsing transaction data:', e);
        }
      };
      
      wsRef.current.onclose = () => {
        setIsConnected(false);
        const backoff = Math.min(1000 * Math.pow(2, reconnectCount), 10000);
        reconnectCount++;
        reconnectTimeoutRef.current = setTimeout(connect, backoff);
      };
      
      wsRef.current.onerror = (err) => {
        console.error('WebSocket error:', err);
        wsRef.current.close();
      };
    };

    connect();

    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  return { latestTransaction, isConnected };
};
