from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, ForeignKey
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class FaceEmbedding(Base):
    __tablename__ = "face_embedding"
    face_id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("student.student_id"))
    embedding = Column(Vector(512))

class Student(Base):
    __tablename__ = "student"
    student_id = Column(Integer, primary_key=True)
