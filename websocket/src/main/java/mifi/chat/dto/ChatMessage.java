package mifi.chat.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonProperty;
import mifi.chat.entities.MessageEntry;

import java.time.LocalDateTime;
import java.util.UUID;

public record ChatMessage(
        @JsonProperty("id")
        UUID id,
        @JsonProperty(value = "chat_id", alternate = {"chatId"})
        UUID chatId,
        @JsonProperty("text")
        String text,
        @JsonProperty(value = "is_from_specialist", alternate = {"fromSpecialist"})
        boolean fromSpecialist,
        @JsonProperty(value = "is_read", alternate = {"isRead", "read"})
        boolean read,
        @JsonProperty(value = "sent_at", alternate = {"sentAt"})
        @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss[.SSS][XXX]")
        LocalDateTime sentAt,
        @JsonProperty(value = "created_at", alternate = {"createdAt", "createAt"})
        @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss[.SSS][XXX]")
        LocalDateTime createAt
) {

    public ChatMessage(
            MessageEntry entry
    ) {
        this(
                entry.getId(),
                entry.getChatId(),
                entry.getText(),
                entry.isFromSpecialist(),
                entry.isRead(),
                entry.getSentAt(),
                entry.getCreateAt()
        );
    }

}
