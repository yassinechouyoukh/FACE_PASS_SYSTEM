package business.facepass.facepass_backend.entity;

import jakarta.persistence.*;

@Entity 
@Table(name = "admin")
public class Admin {
    
    @Id 
    @GeneratedValue(strategy = GenerationType.IDENTITY) 
    @Column(name = "id_admin")
    private Long idAdmin; 
    
    @Column(name = "function") 
    private String function;

    public Admin() {}
    
    public Long getIdAdmin() {
        return idAdmin;
    }

    public void setIdAdmin(Long idAdmin) {
        this.idAdmin = idAdmin;
    }

    public String getFunction() {
        return function;
    }

    public void setFunction(String function) {
        this.function = function;
    }

    
}
