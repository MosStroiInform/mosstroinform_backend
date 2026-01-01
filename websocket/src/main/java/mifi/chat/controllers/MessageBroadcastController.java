package mifi.chat.controllers;

import com.fasterxml.jackson.annotation.JsonFormat;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import mifi.chat.dto.ChatMessage;
import mifi.chat.services.ChatRoomManager;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Sinks;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.UUID;

@Slf4j
@RestController
@RequestMapping("/api/broadcast")
@RequiredArgsConstructor
public class MessageBroadcastController {

    private final ChatRoomManager chatRoomManager;

    @PostMapping("/message")
    public ResponseEntity<String> broadcastMessage(
            @RequestBody BroadcastMessageRequest request
    ) {
        try {
            UUID chatId = UUID.fromString(request.chatId());
            ChatRoomManager.ChatRoom room = chatRoomManager.getRoom(chatId);
            
            // Парсим дату из ISO формата (если пришла строка) или используем как есть
            LocalDateTime sentAt = request.sentAt() != null 
                    ? request.sentAt() 
                    : LocalDateTime.now();
            
            // Если sentAt пришла как строка, нужно парсить (но Jackson должен это делать автоматически)
            // Используем текущее время для createAt, так как это время создания записи в Java сервисе
            LocalDateTime createAt = LocalDateTime.now();
            
            ChatMessage message = new ChatMessage(
                    UUID.fromString(request.messageId()),
                    chatId,
                    request.text(),
                    request.fromSpecialist(),
                    request.isRead(),
                    sentAt,
                    createAt
            );
            
            Sinks.EmitResult result = room.getSink().tryEmitNext(message);
            if (result.isFailure()) {
                log.warn("Failed to broadcast message: {}", result);
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                        .body("Failed to broadcast message");
            }
            
            log.info("Message broadcasted successfully: {} to chat: {}", request.messageId(), chatId);
            return ResponseEntity.ok("Message broadcasted");
        } catch (Exception e) {
            log.error("Error broadcasting message", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error: " + e.getMessage());
        }
    }

    public record BroadcastMessageRequest(
            String messageId,
            String chatId,
            String text,
            boolean fromSpecialist,
            boolean isRead,
            @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss")
            LocalDateTime sentAt
    ) {}
}

