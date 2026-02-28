import cv2
import numpy as np
from sqlalchemy import text
from storage.database import SessionLocal
from ai.recognizer.arcface import ArcFaceRecognizer

recognizer = ArcFaceRecognizer()

student_id = 4   # 🔥 PUT YOUR REAL STUDENT ID HERE

cap = cv2.VideoCapture(0)

print("Press SPACE to capture face")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Register Face", frame)
    key = cv2.waitKey(1)

    if key == 32:  # SPACE
        emb = recognizer.embed(frame)

        if emb is None:
            print("No face detected!")
            break

        print("Embedding captured:", len(emb))

        db = SessionLocal()
        try:
            db.execute(
                text("""
                    INSERT INTO face_embedding (student_id, embedding)
                    VALUES (:sid, :vec)
                """),
                {
                    "sid": student_id,
                    "vec": emb.tolist()
                }
            )
            db.commit()
            print("Embedding stored successfully!")
        finally:
            db.close()

        break

cap.release()
cv2.destroyAllWindows()