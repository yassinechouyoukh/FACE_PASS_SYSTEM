package business.facepass.facepass_backend.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "face_embedding")
public class FaceEmbedding {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "face_id")
    private Long faceId;

    @Column(name = "embedding", columnDefinition = "vector(512)")
    private float[] embedding;

    public FaceEmbedding() {}

    public Long getFaceId() {
        return faceId;
    }
    public void setFaceId(Long faceId) {
        this.faceId = faceId;
    }

    public float[] getEmbedding() {
        return embedding;
    }
    public void setEmbedding(float[] embedding) {
        this.embedding = embedding;
    }

    @OneToOne
    @JoinColumn(name = "student_id")
    private Student student;
}