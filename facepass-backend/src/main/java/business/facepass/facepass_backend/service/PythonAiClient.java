package business.facepass.facepass_backend.service;

import business.facepass.facepass_backend.DTO.RecognitionResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class PythonAiClient {

    @Autowired
    private RestTemplate restTemplate;

    private final String PYTHON_URL = "http://localhost:8000/recognize";

    public RecognitionResponse recognize(double[] embedding) {

        return restTemplate.postForObject(
                PYTHON_URL,
                embedding,
                RecognitionResponse.class
        );
    }
}