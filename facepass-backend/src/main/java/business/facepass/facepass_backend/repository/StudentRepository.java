package business.facepass.facepass_backend.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import business.facepass.facepass_backend.entity.Student;

public interface StudentRepository extends JpaRepository<Student, Long> {
    
}