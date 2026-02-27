package business.facepass.facepass_backend.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import business.facepass.facepass_backend.entity.Behavior;

public interface BehaviorRepository extends JpaRepository<Behavior, Long> {
}