package business.facepass.facepass_backend.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "comportements_behavior")
public class Behavior {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "behavior_id")
    private Long behaviorId;

    @Column(name = "session_id")
    private Long sessionId;

    @Column(name = "behavior_type")
    private String behaviorType;

    @Column(name = "detected_at")
    private LocalDateTime detectedAt;

    public Behavior() {}

    public Long getBehaviorId() {
        return behaviorId;
    }
    public void setBehaviorId(Long behaviorId) {
        this.behaviorId = behaviorId;
    }
    public Long getSessionId() {
        return sessionId;
    }
    public void setSessionId(Long sessionId) {
        this.sessionId = sessionId;
    }
    public String getBehaviorType() {
        return behaviorType;
    }
    public void setBehaviorType(String behaviorType) {
        this.behaviorType = behaviorType;
    }
    public LocalDateTime getDetectedAt() {
        return detectedAt;
    }
    public void setDetectedAt(LocalDateTime detectedAt) {
        this.detectedAt = detectedAt;
    }

    @ManyToOne
    @JoinColumn(name = "student_id")
    private Student student;
}