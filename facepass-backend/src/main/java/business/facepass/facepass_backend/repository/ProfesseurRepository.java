package business.facepass.facepass_backend.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import business.facepass.facepass_backend.entity.Professeur;

public interface ProfesseurRepository extends JpaRepository<Professeur, Long> {
}