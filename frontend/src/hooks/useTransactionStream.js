import { useState, useEffect, useRef } from 'react';

export const useTransactionStream = () => {
  const [latestTransaction, setLatestTransaction] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  useEffect(() => {
    let reconnectCount = 0;
    
    const connect = () => {
      const getWsUrl = () => {
        if (import.meta.env.VITE_WS_URL) return import.meta.env.VITE_WS_URL;
        if (typeof window !== 'undefined' && (window.location.port === '5173' || window.location.port === '5174')) {
          return 'ws://localhost:8000/ws/transactions';
        }
        const protocol = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = typeof window !== 'undefined' ? window.location.host : 'localhost';
        return `${protocol}//${host}/ws/transactions`;
      };

      wsRef.current = new WebSocket(getWsUrl());
      
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
