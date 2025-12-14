import { useEffect, useState, useRef } from 'react';

interface UseWebSocketOptions {
  onMessage?: (data: any) => void;
  onError?: (error: Event) => void;
  onOpen?: () => void;
  onClose?: () => void;
}

export function useWebSocket(url: string, options: UseWebSocketOptions = {}) {
  const [data, setData] = useState<any>(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    let isMounted = true;

    const connect = () => {
      try {
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
          if (isMounted) {
            setConnected(true);
            options.onOpen?.();
          }
        };

        ws.onmessage = (event) => {
          try {
            const parsed = JSON.parse(event.data);
            if (isMounted) {
              setData(parsed);
              options.onMessage?.(parsed);
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        ws.onerror = (error) => {
          if (isMounted) {
            setConnected(false);
            options.onError?.(error);
          }
        };

        ws.onclose = () => {
          if (isMounted) {
            setConnected(false);
            options.onClose?.();
            // Reconnect after 3 seconds
            reconnectTimeoutRef.current = setTimeout(() => {
              if (isMounted) {
                connect();
              }
            }, 3000);
          }
        };
      } catch (error) {
        console.error('WebSocket connection error:', error);
        if (isMounted) {
          setConnected(false);
        }
      }
    };

    connect();

    return () => {
      isMounted = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [url]);

  return { data, connected };
}

