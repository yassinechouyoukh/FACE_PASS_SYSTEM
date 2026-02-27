package business.facepass.facepass_backend.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import business.facepass.facepass_backend.entity.FaceEmbedding;

public interface FaceEmbeddingRepository extends JpaRepository<FaceEmbedding, Long> {
}