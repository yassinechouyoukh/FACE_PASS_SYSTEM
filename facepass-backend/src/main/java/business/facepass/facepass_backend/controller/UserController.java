package business.facepass.facepass_backend.controller;

import business.facepass.facepass_backend.entity.User;
import business.facepass.facepass_backend.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/users")
public class UserController {

    @Autowired
    private UserRepository userRepository;

    // Test POST to save a user
    @PostMapping("/add")
    public User addUser(@RequestBody User user) {
        return userRepository.save(user);
    }

    // Test GET to see if it reads from the database
    @GetMapping("/all")
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }
}