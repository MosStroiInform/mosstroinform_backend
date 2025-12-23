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
public class ChatEntity {

    @Id
    private final UUID id;
    @Column("project_id")
    private final UUID projectId;
    @Column("specialist_name")
    private final String specialistName;
    @Column("specialist_avatar_url")
    private final String specialistAvatarUrl;

    @Builder.Default
    @Column("is_active")
    private boolean active = true;

    @CreatedDate
    @Column("created_at")
    private LocalDateTime createdAt;

    @LastModifiedDate
    @Column("updated_at")
    private LocalDateTime updatedAt;

}
