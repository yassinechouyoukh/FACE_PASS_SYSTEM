package business.facepass.facepass_backend.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "classgroup")
public class Classgroup {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "classgroup_id")
    private Long classgroupId;

    @Column(name = "department_id")
    private Long departmentId;

    @Column(name = "section_nbr")
    private Integer sectionNumber;

    @Column(name = "academic_year")
    private String academicYear;

    public Classgroup() {}

    public Long getClassgroupId() {
        return classgroupId;
    }
    public void setClassgroupId(Long classgroupId) {
        this.classgroupId = classgroupId;
    }
    public Long getDepartmentId() {
        return departmentId;
    }
    public void setDepartmentId(Long departmentId) {
        this.departmentId = departmentId;
    }
    public Integer getSectionNumber() {
        return sectionNumber;
    }
    public void setSectionNumber(Integer sectionNumber) {
        this.sectionNumber = sectionNumber;
    }
    public String getAcademicYear() {
        return academicYear;
    }
    public void setAcademicYear(String academicYear) {
        this.academicYear = academicYear;
    }
    
}