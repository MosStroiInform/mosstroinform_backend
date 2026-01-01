package mifi.chat.services;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import mifi.chat.dto.Action;
import mifi.chat.dto.ChatMessage;
import mifi.chat.dto.Message;
import mifi.chat.entities.MessageEntry;
import mifi.chat.repositories.MessageRepository;
import org.springframework.r2dbc.core.DatabaseClient;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.socket.WebSocketHandler;
import org.springframework.web.reactive.socket.WebSocketMessage;
import org.springframework.web.reactive.socket.WebSocketSession;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;
import reactor.core.publisher.Sinks;
import tools.jackson.databind.ObjectMapper;

import java.net.URI;
import java.util.UUID;

@Slf4j
@Service
@RequiredArgsConstructor
public class ChatService implements WebSocketHandler {

    private final ChatRoomManager chatRoomManager;

    private final MessageRepository messageRepository;

    private final DatabaseClient databaseClient;

    private final ObjectMapper objectMapper;

    @Override
    public Mono<Void> handle(WebSocketSession session) {
        UUID uuid = getChatUuid(session);
        ChatRoomManager.ChatRoom chat = chatRoomManager.getRoom(uuid);
        
        log.info("WebSocket connection established for chat: {}", uuid);
        
        // Поток входящих сообщений - обрабатываем действия от клиента
        Flux<ChatMessage> incomingMessages = session.receive()
                .map(WebSocketMessage::getPayloadAsText)
                .doOnNext(text -> log.debug("Received WebSocket message: {}", text))
                .flatMap(it -> processAction(it, uuid, chat))
                .filter(it -> it != null)
                .doOnNext(message -> log.info("Processed message, broadcasting: id={}, text={}", message.id(), message.text()));
        
        // Поток исходящих сообщений - транслируем всем подключенным клиентам (включая отправителя)
        Flux<WebSocketMessage> outgoingMessages =
                chat.getSink().asFlux()
                        .doOnNext(message -> log.debug("Broadcasting message to client: id={}", message.id()))
                        .map(it -> {
                            try {
                                String json = objectMapper.writeValueAsString(it);
                                log.debug("Serialized message to JSON: {}", json);
                                return session.textMessage(json);
                            } catch (Exception e) {
                                log.error("Error serializing message", e);
                                throw new RuntimeException("Error serializing message", e);
                            }
                        });
        
        return session.send(outgoingMessages)
                .and(incomingMessages.then())
                .doOnError(error -> log.error("WebSocket error for chat: {}", uuid, error))
                .doOnTerminate(() -> log.info("WebSocket connection closed for chat: {}", uuid));
    }

    private Mono<ChatMessage> processAction(String json, UUID chatId, ChatRoomManager.ChatRoom chat) {
        return Mono.fromCallable(() -> objectMapper.readValue(json, Action.class))
                .flatMap(action -> switch (action.getType()) {
                    case CREATE -> {
                        Message.CreateRequest createRequest = (Message.CreateRequest) action;
                        yield handleCreateAction(createRequest, chatId, chat);
                    }
                    case READ -> {
                        Message.ReadRequest readRequest = (Message.ReadRequest) action;
                        yield handleReadAction(readRequest, chatId, chat);
                    }
                })
                .onErrorResume(ex -> {
                    log.error("Invalid message: {}", json, ex);
                    return Mono.empty();
                });
    }

    private Mono<ChatMessage> handleCreateAction(Message.CreateRequest request, UUID chatId, ChatRoomManager.ChatRoom chat) {
        log.info("Handling CREATE action: chatId={}, text={}, fromSpecialist={}", chatId, request.text(), request.fromSpecialist());
        
        MessageEntry messageEntry = MessageEntry.ofText(request.text(), chatId, request.fromSpecialist());

        return databaseClient.sql("""
                INSERT INTO messages (id, chat_id, text, sent_at, is_from_specialist, is_read, created_at)
                VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6)
                RETURNING id, chat_id, text, sent_at, is_from_specialist, is_read, created_at
                """)
                .bind("$1", messageEntry.getChatId())
                .bind("$2", messageEntry.getText())
                .bind("$3", messageEntry.getSentAt())
                .bind("$4", messageEntry.isFromSpecialist())
                .bind("$5", messageEntry.isRead())
                .bind("$6", messageEntry.getCreateAt())
                .map(row -> MessageEntry.builder()
                        .id(row.get("id", UUID.class))
                        .chatId(row.get("chat_id", UUID.class))
                        .text(row.get("text", String.class))
                        .fromSpecialist(row.get("is_from_specialist", Boolean.class))
                        .read(row.get("is_read", Boolean.class))
                        .sentAt(row.get("sent_at", java.time.LocalDateTime.class))
                        .createAt(row.get("created_at", java.time.LocalDateTime.class))
                        .build())
                .one()
                .map(ChatMessage::new)
                .doOnNext(message -> {
                    log.info("Message saved to DB: id={}, broadcasting to all clients", message.id());
                    Sinks.EmitResult result = chat.getSink().tryEmitNext(message);
                    if (result.isFailure()) {
                        log.error("Failed to emit message to sink: {}", result);
                    } else {
                        log.info("Message successfully emitted to sink: id={}", message.id());
                    }
                })
                .doOnError(error -> log.error("Error handling CREATE action", error));
    }

    private Mono<ChatMessage> handleReadAction(Message.ReadRequest request, UUID chatId, ChatRoomManager.ChatRoom chat) {
        return messageRepository.findById(request.messageId())
                .filter(message -> message.getChatId().equals(chatId))
                .filter(message -> !message.isRead())
                .flatMap(message -> {
                    message.setRead(true);
                    return messageRepository.save(message);
                })
                .map(ChatMessage::new)
                .doOnNext(message -> {
                    Sinks.EmitResult result = chat.getSink().tryEmitNext(message);
                    if (result.isFailure()) {
                        log.warn("Emit failed: {}", result);
                    }
                })
                .switchIfEmpty(Mono.defer(() -> {
                    log.debug("Message {} not found or already read", request.messageId());
                    return Mono.empty();
                }));
    }

    private UUID getChatUuid(WebSocketSession session) {
        URI uri = session.getHandshakeInfo().getUri();
        String path = uri.getPath();
        return UUID.fromString(path.substring(path.lastIndexOf("/") + 1));
    }
}
