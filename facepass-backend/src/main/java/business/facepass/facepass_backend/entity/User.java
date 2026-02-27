package business.facepass.facepass_backend.entity;

import jakarta.persistence.*;

@Entity 
@Table(name = "user")
public class User {
    
    @Id 
    @GeneratedValue(strategy = GenerationType.IDENTITY) 
    @Column(name = "id_user")
    private Long idUser; 
    
    @Column(name = "first_name")
    private String firstName;
    
    @Column(name = "last_name") 
    private String lastName; 
    
    @Column(name = "email")
    private String email;
    
    @Column(name = "password") 
    private String password; 
    
    @Column(name = "role") 
    private String userRole; 

    public User() {}

    public Long getIdUser() {
        return idUser; 
    } 
    public void setIdUser(Long idUser) { 
        this.idUser = idUser; 
    } 
    public String getFirstName() { 
        return firstName; 
    } 
    public void setFirstName(String firstName) { 
        this.firstName = firstName; 
    } 
    public String getLastName() { 
        return lastName; 
    } 
    public void setLastName(String lastName) { 
        this.lastName = lastName; 
    } 
    public String getEmail() { 
        return email; 
    } 
    public void setEmail(String email) { 
        this.email = email; 
    } 
    public String getPassword() { 
        return password; 
    } 
    public void setPassword(String password) { 
        this.password = password; 
    } 
    public String getUserRole() { 
        return userRole; 
    } 
    public void setUserRole(String userRole) { 
        this.userRole = userRole; 
    } 
}