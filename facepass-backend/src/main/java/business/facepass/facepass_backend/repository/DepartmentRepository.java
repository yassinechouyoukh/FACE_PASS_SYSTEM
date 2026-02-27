package business.facepass.facepass_backend.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import business.facepass.facepass_backend.entity.Department;

public interface DepartmentRepository extends JpaRepository<Department, Long> {
}