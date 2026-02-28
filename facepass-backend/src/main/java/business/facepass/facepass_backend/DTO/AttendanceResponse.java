package business.facepass.facepass_backend.DTO;

import java.time.LocalDate;

public class AttendanceResponse {

    private Long studentId;
    private Long sessionId;
    private String status;
    private LocalDate attendanceDate;
    private String message;

    public AttendanceResponse(Long studentId,
                              Long sessionId,
                              String status,
                              LocalDate attendanceDate,
                              String message) {
        this.studentId = studentId;
        this.sessionId = sessionId;
        this.status = status;
        this.attendanceDate = attendanceDate;
        this.message = message;
    }

    public Long getStudentId() {
        return studentId;
    }

    public Long getSessionId() {
        return sessionId;
    }

    public String getStatus() {
        return status;
    }

    public LocalDate getAttendanceDate() {
        return attendanceDate;
    }

    public String getMessage() {
        return message;
    }
}