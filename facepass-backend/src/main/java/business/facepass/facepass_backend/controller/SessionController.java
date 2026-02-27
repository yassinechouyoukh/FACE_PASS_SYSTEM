package business.facepass.facepass_backend.controller;

import org.springframework.web.bind.annotation.RestController;

import business.facepass.facepass_backend.entity.Sessions;
import business.facepass.facepass_backend.repository.SessionsRepository;

import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;


@RestController
@RequestMapping("/sessions")
public class SessionController {
    private final SessionsRepository sessionsRepository;
    public SessionController(SessionsRepository sessionsRepository) {
        this.sessionsRepository = sessionsRepository;
    }
    @PostMapping
    public Sessions create(@RequestParam Sessions session) {
        return sessionsRepository.save(session);
    }
    @GetMapping
    public List<Sessions> getAll() {
        return sessionsRepository.findAll();
    }
    @GetMapping("/test")
    public String Test() {
        return "Test sessions working";
    }
}
