package business.facepass.facepass_backend.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import business.facepass.facepass_backend.entity.Classgroup;

public interface ClassGroupRepository extends JpaRepository<Classgroup, Long> {
}