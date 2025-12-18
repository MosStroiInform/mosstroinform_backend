package mifi.chat.entities;

import lombok.Builder;
import lombok.Data;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.Id;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.relational.core.mapping.Column;

import java.time.LocalDateTime;
import java.util.UUID;

@Data
@Builder
public class MessageEntry {

    @Id
    private final UUID id;

    @Column("chat_id")
    private final UUID chatId;

    @Column("text")
    private final String text;

    @Column("is_from_specialist")
    private final boolean fromSpecialist;

    @Column("is_read")
    private boolean read;

    @CreatedDate
    @Column("sent_at")
    private LocalDateTime sentAt;

    @LastModifiedDate
    @Column("created_at")
    private LocalDateTime createAt;

    public static MessageEntry ofText(String text, UUID chatId, boolean fromSpecialist) {
        return MessageEntry.builder()
                .id(UUID.randomUUID())
                .text(text)
                .chatId(chatId)
                .fromSpecialist(fromSpecialist)
                .read(false)
                .sentAt(LocalDateTime.now())
                .createAt(LocalDateTime.now())
                .build();
    }

}
