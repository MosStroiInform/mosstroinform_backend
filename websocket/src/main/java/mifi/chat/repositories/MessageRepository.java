package mifi.chat.repositories;

import mifi.chat.entities.MessageEntry;
import org.springframework.data.r2dbc.repository.Modifying;
import org.springframework.data.r2dbc.repository.Query;
import org.springframework.data.r2dbc.repository.R2dbcRepository;
import reactor.core.publisher.Mono;

import java.util.UUID;

public interface MessageRepository extends R2dbcRepository<MessageEntry, UUID> {

    @Modifying
    @Query("UPDATE message_entry SET is_read = true WHERE id = :messageId")
    Mono<Integer> markAsRead(UUID messageId);

    Mono<MessageEntry> findById(UUID id);

}
