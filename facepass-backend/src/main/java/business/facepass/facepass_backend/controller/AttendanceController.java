package business.facepass.facepass_backend.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import business.facepass.facepass_backend.DTO.RecognitionResponse;
import business.facepass.facepass_backend.entity.Attendance;
import business.facepass.facepass_backend.entity.Sessions;
import business.facepass.facepass_backend.entity.Student;
import business.facepass.facepass_backend.repository.AttendanceRepository;
import business.facepass.facepass_backend.repository.SessionsRepository;
import business.facepass.facepass_backend.repository.StudentRepository;
import business.facepass.facepass_backend.service.AttendanceService;
import business.facepass.facepass_backend.service.PythonAiClient;

@RestController
@RequestMapping("/attendance")
public class AttendanceController {

    private final AttendanceRepository attendanceRepository;
    private final StudentRepository studentRepository;
    private final SessionsRepository sessionsRepository;
    private final AttendanceService attendanceService;

    public AttendanceController(
            AttendanceRepository attendanceRepository,
            StudentRepository studentRepository,
            SessionsRepository sessionsRepository,
            AttendanceService attendanceService) {

        this.attendanceRepository = attendanceRepository;
        this.studentRepository = studentRepository;
        this.sessionsRepository = sessionsRepository;
        this.attendanceService = attendanceService;
    }

    @PostMapping
    public Attendance createAttendance(@RequestBody Attendance attendance) {

        Student student = studentRepository
            .findById(attendance.getStudent().getStudentId())
            .orElseThrow(() -> new RuntimeException("Student not found"));

        Sessions session = sessionsRepository
            .findById(attendance.getSession().getSessionId())
            .orElseThrow(() -> new RuntimeException("Session not found"));

        attendance.setStudent(student);
        attendance.setSession(session);

        return attendanceRepository.save(attendance);
    }

    @GetMapping
    public List<Attendance> getAll() {
        return attendanceRepository.findAll();
    }

    @PostMapping("/auto/{studentId}")
    public Attendance autoMark(@PathVariable Long studentId) {
        return attendanceService.markAttendance(studentId);
    }

    @Autowired
    private PythonAiClient pythonAiClient;

    @GetMapping("/test-recognition")
    public RecognitionResponse testRecognition() {

        double[] fakeEmbedding = new double[512];

        for (int i = 0; i < 512; i++) {
            fakeEmbedding[i] = 0.1;
        }

        return pythonAiClient.recognize(fakeEmbedding);
    }

    @PostMapping("/recognize-and-mark")
    public String recognizeAndMark(@RequestBody double[] embedding) {

        RecognitionResponse response = pythonAiClient.recognize(embedding);

        if (response != null && response.isMatch()) {

            Long studentId = response.getStudent_id().longValue();

            attendanceService.markAttendance(studentId);

            return "Attendance marked for student " + studentId;
        }

        return "No match found";
    }
}