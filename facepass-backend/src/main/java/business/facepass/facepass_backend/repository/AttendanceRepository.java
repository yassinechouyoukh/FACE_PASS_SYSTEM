package business.facepass.facepass_backend.repository;

import java.time.LocalDate;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import business.facepass.facepass_backend.entity.Attendance;
import business.facepass.facepass_backend.entity.Sessions;
import business.facepass.facepass_backend.entity.Student;

public interface AttendanceRepository extends JpaRepository<Attendance, Long> {
    Optional<Attendance> findByStudentAndSession(Student student, Sessions session);
    boolean existsByStudentAndSessionAndAttendanceDate(Student student, Sessions session, LocalDate attendanceDate);
}