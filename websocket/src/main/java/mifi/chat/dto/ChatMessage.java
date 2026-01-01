package mifi.chat.dto;

import com.fasterxml.jackson.annotation.JsonAlias;
import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonProperty;
import mifi.chat.entities.MessageEntry;

import java.time.LocalDateTime;
import java.util.UUID;

public record ChatMessage(
        @JsonProperty("id")
        UUID id,
        @JsonProperty("chat_id")
        @JsonAlias({"chatId"})
        UUID chatId,
        @JsonProperty("text")
        String text,
        @JsonProperty("is_from_specialist")
        @JsonAlias({"fromSpecialist"})
        boolean fromSpecialist,
        @JsonProperty("is_read")
        @JsonAlias({"isRead", "read"})
        boolean read,
        @JsonProperty("sent_at")
        @JsonAlias({"sentAt"})
        @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss[.SSS][XXX]")
        LocalDateTime sentAt,
        @JsonProperty("created_at")
        @JsonAlias({"createdAt", "createAt"})
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
