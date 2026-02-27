package business.facepass.facepass_backend.entity;

import java.util.List;

import jakarta.persistence.*;

@Entity
@Table(name = "student")
public class Student {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long studentId;

    @Column(name = "email")
    private String email;

    @Column(name = "first_name")
    private String firstName;

    @Column(name = "last_name")
    private String lastName;

    @Column(name = "ref_img")
    private String referenceImage;

    public Student(){};

    public Long getStudentId(){
        return studentId;
    }
    public void setStudentId(Long studentId){
        this.studentId = studentId;
    }
    public String getFirstName(){
        return firstName;
    }
    public void setFirstName(String firstName){
        this.firstName = firstName;
    }
    public String getLastName(){
        return lastName;
    }
    public void setLastName(String lastName){
        this.lastName = lastName;
    }
    public String getEmail(){
        return email;
    }
    public void setEmail(String email){
        this.email = email;
    }
    public String getReferenceImage(){
        return referenceImage;
    }
    public void setReferenceImage(String referenceImage){
        this.referenceImage = referenceImage;
    }

    @OneToMany(mappedBy = "student")
    private List<Attendance> attendances;

    @ManyToOne
    @JoinColumn(name = "classgroup_id")
    private Classgroup classgroup;
}