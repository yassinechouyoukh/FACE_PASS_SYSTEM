package business.facepass.facepass_backend.entity;

import jakarta.persistence.*;
@Entity 
@Table(name = "professeur")
public class Professeur {
    
    @Id 
    @GeneratedValue(strategy = GenerationType.IDENTITY) 
    @Column(name = "id_prof") 
    private Long IdProf; 
    
    @Column(name = "department_id") 
    private Long departmentId; 
    
    @Column(name = "subject_id") 
    private Long subjectId; 

    @Column(name = "function") 
    private String function; 
    
    public Professeur() {} 

    public Long getIdProf() {
        return IdProf;
    }
    public void setIdProf(Long idProf) {
        IdProf = idProf;
    }
    public Long getDepartmentId() {
        return departmentId;
    }
    public void setDepartmentId(Long departmentId) {
        this.departmentId = departmentId;
    }
    public Long getSubjectId() {
        return subjectId;
    }
    public void setSubjectId(Long subjectId) {
        this.subjectId = subjectId;
    }
    public String getFunction() {
        return function;
    }
    public void setFunction(String function) {
        this.function = function;
    }
    
}
