package business.facepass.facepass_backend.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import business.facepass.facepass_backend.entity.Subject;

public interface SubjectRepository extends JpaRepository<Subject, Long> {
}