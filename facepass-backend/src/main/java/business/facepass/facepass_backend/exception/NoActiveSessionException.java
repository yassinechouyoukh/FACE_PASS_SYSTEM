package business.facepass.facepass_backend.exception;

public class NoActiveSessionException extends RuntimeException {
    public NoActiveSessionException(String message) {
        super(message);
    }
}
