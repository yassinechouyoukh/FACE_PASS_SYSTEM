package business.facepass.facepass_backend.service;

import java.time.LocalDate;
import java.time.LocalDateTime;

import org.springframework.stereotype.Service;

import business.facepass.facepass_backend.entity.Attendance;
import business.facepass.facepass_backend.entity.Sessions;
import business.facepass.facepass_backend.entity.Student;
import business.facepass.facepass_backend.repository.AttendanceRepository;
import business.facepass.facepass_backend.repository.SessionsRepository;
import business.facepass.facepass_backend.repository.StudentRepository;

@Service
public class AttendanceService {

    private final AttendanceRepository attendanceRepository;
    private final StudentRepository studentRepository;
    private final SessionsRepository sessionsRepository;

    public AttendanceService(
            AttendanceRepository attendanceRepository,
            StudentRepository studentRepository,
            SessionsRepository sessionsRepository) {
        this.attendanceRepository = attendanceRepository;
        this.studentRepository = studentRepository;
        this.sessionsRepository = sessionsRepository;
    }

    public Attendance markAttendance(Long studentId) {

        Student student = studentRepository.findById(studentId)
                .orElseThrow(() -> new RuntimeException("Student not found"));

        LocalDateTime now = LocalDateTime.now();

        Sessions session = sessionsRepository.findActiveSession(now)
                .orElseThrow(() -> new RuntimeException("No active session"));

        if (attendanceRepository.findByStudentAndSession(student, session).isPresent()) {
            throw new RuntimeException("Attendance already marked");
        }

        Attendance attendance = new Attendance();
        attendance.setStudent(student);
        attendance.setSession(session);
        attendance.setStatus("PRESENT");
        attendance.setAttendanceDate(LocalDate.now());

        return attendanceRepository.save(attendance);
    }
}