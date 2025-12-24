package mifi.chat.entities;

import lombok.Builder;
import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.annotation.Transient;
import org.springframework.data.relational.core.mapping.Column;
import org.springframework.data.relational.core.mapping.Table;

import java.time.LocalDateTime;
import java.util.UUID;

@Data
@Builder
@Table("messages")
public class MessageEntry {

    @Id
    @Transient
    private UUID id;

    @Column("chat_id")
    private final UUID chatId;

    @Column("text")
    private final String text;

    @Column("is_from_specialist")
    private final boolean fromSpecialist;

    @Column("is_read")
    private boolean read;

    @Column("sent_at")
    private LocalDateTime sentAt;

    @Column("created_at")
    private LocalDateTime createAt;

    public static MessageEntry ofText(String text, UUID chatId, boolean fromSpecialist) {
        return MessageEntry.builder()
                .text(text)
                .chatId(chatId)
                .fromSpecialist(fromSpecialist)
                .read(false)
                .sentAt(LocalDateTime.now())
                .createAt(LocalDateTime.now())
                .build();
    }

}
