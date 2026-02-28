package business.facepass.facepass_backend.service;

import java.time.LocalDate;
import java.time.LocalDateTime;

import org.springframework.stereotype.Service;

import business.facepass.facepass_backend.entity.Attendance;
import business.facepass.facepass_backend.entity.Sessions;
import business.facepass.facepass_backend.entity.Student;
import business.facepass.facepass_backend.exception.AttendanceAlreadyMarkedException;
import business.facepass.facepass_backend.exception.NoActiveSessionException;
import business.facepass.facepass_backend.exception.StudentNotFoundException;
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
                .orElseThrow(() -> new StudentNotFoundException("Student Not Found"));

        LocalDateTime now = LocalDateTime.now();
        LocalDate today = LocalDate.now();
        Sessions session = sessionsRepository
                .findActiveSession(now, today)
                .orElseThrow(() -> new NoActiveSessionException("No Active Session"));

       if (attendanceRepository.existsByStudentAndSessionAndAttendanceDate(student, session, LocalDate.now())) {
            throw new AttendanceAlreadyMarkedException("Attendance Already Marked");
        }

        Attendance attendance = new Attendance();
        attendance.setStudent(student);
        attendance.setSession(session);
        attendance.setStatus("PRESENT");
        attendance.setAttendanceDate(LocalDate.now());

        return attendanceRepository.save(attendance);
    }
}