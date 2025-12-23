package mifi.chat.dto;

import mifi.chat.entities.MessageEntry;

import java.time.LocalDateTime;
import java.util.UUID;

public record ChatMessage(
        UUID id,
        UUID chatId,
        String text,
        boolean fromSpecialist,
        boolean read,
        LocalDateTime sentAt,
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
