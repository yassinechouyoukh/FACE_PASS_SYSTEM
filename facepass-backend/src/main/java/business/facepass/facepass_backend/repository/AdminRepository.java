package business.facepass.facepass_backend.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import business.facepass.facepass_backend.entity.Admin;

public interface AdminRepository extends JpaRepository<Admin, Long> {
}