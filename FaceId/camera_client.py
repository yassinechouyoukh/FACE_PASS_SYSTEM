import cv2
import asyncio
import websockets
import time

WS_URL = "ws://localhost:8000/ws"

async def stream_camera():
    cap = cv2.VideoCapture(0)

    async with websockets.connect(
        WS_URL,
        ping_interval=60,
        ping_timeout=60
    ) as websocket:

        print("Connected to WebSocket")

        while True:
            start = time.time()

            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (320, 240))

            _, buffer = cv2.imencode('.jpg', frame)

            await websocket.send(buffer.tobytes())

            try:
                response = await websocket.recv()
                print("Server response:", response)
            except Exception as e:
                print("Receive error:", e)
                break

            cv2.imshow("Camera", frame)

            await asyncio.sleep(0.03)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

asyncio.run(stream_camera())