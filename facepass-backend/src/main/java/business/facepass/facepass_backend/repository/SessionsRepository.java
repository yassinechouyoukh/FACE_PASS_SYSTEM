package business.facepass.facepass_backend.repository;

import java.time.LocalDateTime;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import business.facepass.facepass_backend.entity.Sessions;

public interface SessionsRepository extends JpaRepository<Sessions, Long> {
    @Query("SELECT s FROM Sessions s WHERE :now BETWEEN s.startTime AND s.endTime")
    Optional<Sessions> findActiveSession(@Param("now") LocalDateTime now);
}