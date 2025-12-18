package mifi.chat.services;

import tools.jackson.databind.ObjectMapper;
import mifi.chat.dto.ChatMessage;
import mifi.chat.dto.Message;
import mifi.chat.entities.MessageEntry;
import mifi.chat.repositories.MessageRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import mifi.chat.dto.ChatCacheProperties;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.web.reactive.socket.HandshakeInfo;
import org.springframework.web.reactive.socket.WebSocketMessage;
import org.springframework.web.reactive.socket.WebSocketSession;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;
import reactor.core.publisher.Sinks;
import reactor.test.StepVerifier;

import java.net.URI;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.UUID;
import java.util.concurrent.TimeUnit;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ChatServiceTest {

    @Mock
    private MessageRepository messageRepository;

    @Mock
    private WebSocketSession webSocketSession;

    @Mock
    private HandshakeInfo handshakeInfo;

    private ChatService chatService;
    private ChatRoomManager chatRoomManager;
    private ObjectMapper objectMapper;
    private UUID chatId;
    private ChatRoomManager.ChatRoom chatRoom;
    private Sinks.Many<ChatMessage> messageSink;

    @BeforeEach
    void setUp() {
        objectMapper = new ObjectMapper();
        ChatCacheProperties chatCacheProperties = new ChatCacheProperties();
        chatCacheProperties.setKeepAlive(60);
        chatCacheProperties.setUnit(ChronoUnit.SECONDS);
        chatCacheProperties.setTickTimer(60);
        chatCacheProperties.setTickUnit(TimeUnit.SECONDS);
        chatRoomManager = new ChatRoomManager(chatCacheProperties);
        chatService = new ChatService(chatRoomManager, messageRepository, objectMapper);
        chatId = UUID.randomUUID();
        chatRoom = chatRoomManager.getRoom(chatId);
        messageSink = chatRoom.getSink();
    }

    @Test
    void shouldHandleIncomingMessage() throws Exception {
        // Arrange
        String messageText = "Привет, это тестовое сообщение";
        boolean fromSpecialist = true;
        Message.CreateRequest createRequest = new Message.CreateRequest(messageText, fromSpecialist);
        String jsonMessage = objectMapper.writeValueAsString(createRequest);

        MessageEntry savedMessage = MessageEntry.builder()
                .id(UUID.randomUUID())
                .chatId(chatId)
                .text(messageText)
                .fromSpecialist(fromSpecialist)
                .read(false)
                .sentAt(LocalDateTime.now())
                .createAt(LocalDateTime.now())
                .build();

        URI uri = new URI("ws://localhost:8080/chat/" + chatId);
        when(handshakeInfo.getUri()).thenReturn(uri);
        when(webSocketSession.getHandshakeInfo()).thenReturn(handshakeInfo);
        when(messageRepository.save(any(MessageEntry.class))).thenReturn(Mono.just(savedMessage));

        WebSocketMessage wsMessage = mock(WebSocketMessage.class);
        when(wsMessage.getPayloadAsText()).thenReturn(jsonMessage);
        when(webSocketSession.receive()).thenReturn(Flux.just(wsMessage));
        when(webSocketSession.send(any())).thenReturn(Mono.empty());
        lenient().when(webSocketSession.textMessage(anyString())).thenAnswer(invocation -> {
            String text = invocation.getArgument(0);
            WebSocketMessage msg = mock(WebSocketMessage.class);
            when(msg.getPayloadAsText()).thenReturn(text);
            return msg;
        });

        // Act
        Mono<Void> result = chatService.handle(webSocketSession);

        // Assert
        StepVerifier.create(result)
                .verifyComplete();

        ArgumentCaptor<MessageEntry> messageCaptor = ArgumentCaptor.forClass(MessageEntry.class);
        verify(messageRepository, times(1)).save(messageCaptor.capture());

        MessageEntry capturedMessage = messageCaptor.getValue();
        assertThat(capturedMessage.getChatId()).isEqualTo(chatId);
        assertThat(capturedMessage.getText()).isEqualTo(messageText);
        assertThat(capturedMessage.isFromSpecialist()).isEqualTo(fromSpecialist);
        assertThat(capturedMessage.isRead()).isFalse();

        verify(webSocketSession, times(1)).receive();
        verify(webSocketSession, times(1)).send(any());
    }

    @Test
    void shouldExtractChatUuidFromUri() throws Exception {
        // Arrange
        UUID expectedChatId = UUID.randomUUID();
        URI uri = new URI("ws://localhost:8080/chat/" + expectedChatId);
        when(handshakeInfo.getUri()).thenReturn(uri);
        when(webSocketSession.getHandshakeInfo()).thenReturn(handshakeInfo);
        when(webSocketSession.receive()).thenReturn(Flux.empty());
        when(webSocketSession.send(any())).thenReturn(Mono.empty());

        // Act
        Mono<Void> result = chatService.handle(webSocketSession);

        // Assert
        StepVerifier.create(result)
                .verifyComplete();

        // Verify that room was accessed (indirectly through getRoom call)
        ChatRoomManager.ChatRoom room = chatRoomManager.getRoom(expectedChatId);
        assertThat(room).isNotNull();
    }

    @Test
    void shouldHandleInvalidJsonMessage() throws Exception {
        // Arrange
        String invalidJson = "{invalid json}";
        URI uri = new URI("ws://localhost:8080/chat/" + chatId);
        when(handshakeInfo.getUri()).thenReturn(uri);
        when(webSocketSession.getHandshakeInfo()).thenReturn(handshakeInfo);

        WebSocketMessage wsMessage = mock(WebSocketMessage.class);
        when(wsMessage.getPayloadAsText()).thenReturn(invalidJson);
        when(webSocketSession.receive()).thenReturn(Flux.just(wsMessage));
        when(webSocketSession.send(any())).thenReturn(Mono.empty());

        // Act
        Mono<Void> result = chatService.handle(webSocketSession);

        // Assert
        StepVerifier.create(result)
                .verifyComplete();

        verify(messageRepository, never()).save(any(MessageEntry.class));
        verify(webSocketSession, times(1)).receive();
    }

    @Test
    void shouldSendOutgoingMessages() throws Exception {
        // Arrange
        URI uri = new URI("ws://localhost:8080/chat/" + chatId);
        when(handshakeInfo.getUri()).thenReturn(uri);
        when(webSocketSession.getHandshakeInfo()).thenReturn(handshakeInfo);
        when(webSocketSession.receive()).thenReturn(Flux.empty());

        ChatMessage outgoingMessage = new ChatMessage(
                UUID.randomUUID(),
                chatId,
                "Исходящее сообщение",
                false,
                false,
                LocalDateTime.now(),
                LocalDateTime.now()
        );

        @SuppressWarnings("unchecked")
        ArgumentCaptor<Flux<WebSocketMessage>> sendCaptor = ArgumentCaptor.forClass(Flux.class);
        when(webSocketSession.send(sendCaptor.capture())).thenReturn(Mono.empty());
        lenient().when(webSocketSession.textMessage(anyString())).thenAnswer(invocation -> {
            String text = invocation.getArgument(0);
            WebSocketMessage msg = mock(WebSocketMessage.class);
            when(msg.getPayloadAsText()).thenReturn(text);
            return msg;
        });

        // Act
        Mono<Void> result = chatService.handle(webSocketSession);

        // Assert
        verify(webSocketSession, times(1)).send(any());

        // Verify that outgoing messages are sent
        Flux<WebSocketMessage> sentMessages = sendCaptor.getValue();
        StepVerifier.create(sentMessages)
                .then(() -> messageSink.tryEmitNext(outgoingMessage))
                .assertNext(msg -> {
                    try {
                        String payload = msg.getPayloadAsText();
                        ChatMessage received = objectMapper.readValue(payload, ChatMessage.class);
                        assertThat(received.chatId()).isEqualTo(outgoingMessage.chatId());
                        assertThat(received.text()).isEqualTo(outgoingMessage.text());
                    } catch (Exception e) {
                        throw new RuntimeException(e);
                    }
                })
                .thenCancel()
                .verify();

        // Complete the handler
        StepVerifier.create(result)
                .verifyComplete();
    }

    @Test
    void shouldHandleMultipleIncomingMessages() throws Exception {
        // Arrange
        URI uri = new URI("ws://localhost:8080/chat/" + chatId);
        when(handshakeInfo.getUri()).thenReturn(uri);
        when(webSocketSession.getHandshakeInfo()).thenReturn(handshakeInfo);

        Message.CreateRequest request1 = new Message.CreateRequest("Сообщение 1", false);
        Message.CreateRequest request2 = new Message.CreateRequest("Сообщение 2", true);
        String json1 = objectMapper.writeValueAsString(request1);
        String json2 = objectMapper.writeValueAsString(request2);

        MessageEntry savedMessage1 = MessageEntry.builder()
                .id(UUID.randomUUID())
                .chatId(chatId)
                .text("Сообщение 1")
                .fromSpecialist(false)
                .read(false)
                .sentAt(LocalDateTime.now())
                .createAt(LocalDateTime.now())
                .build();

        MessageEntry savedMessage2 = MessageEntry.builder()
                .id(UUID.randomUUID())
                .chatId(chatId)
                .text("Сообщение 2")
                .fromSpecialist(true)
                .read(false)
                .sentAt(LocalDateTime.now())
                .createAt(LocalDateTime.now())
                .build();

        WebSocketMessage wsMessage1 = mock(WebSocketMessage.class);
        WebSocketMessage wsMessage2 = mock(WebSocketMessage.class);
        when(wsMessage1.getPayloadAsText()).thenReturn(json1);
        when(wsMessage2.getPayloadAsText()).thenReturn(json2);
        when(webSocketSession.receive()).thenReturn(Flux.just(wsMessage1, wsMessage2));
        when(messageRepository.save(any(MessageEntry.class)))
                .thenReturn(Mono.just(savedMessage1))
                .thenReturn(Mono.just(savedMessage2));
        when(webSocketSession.send(any())).thenReturn(Mono.empty());
        lenient().when(webSocketSession.textMessage(anyString())).thenAnswer(invocation -> {
            String text = invocation.getArgument(0);
            WebSocketMessage msg = mock(WebSocketMessage.class);
            when(msg.getPayloadAsText()).thenReturn(text);
            return msg;
        });

        // Act
        Mono<Void> result = chatService.handle(webSocketSession);

        // Assert
        StepVerifier.create(result)
                .verifyComplete();

        verify(messageRepository, times(2)).save(any(MessageEntry.class));
    }

    @Test
    void shouldHandleMessageFromSpecialist() throws Exception {
        // Arrange
        String messageText = "Сообщение от специалиста";
        Message.CreateRequest createRequest = new Message.CreateRequest(messageText, true);
        String jsonMessage = objectMapper.writeValueAsString(createRequest);

        MessageEntry savedMessage = MessageEntry.builder()
                .id(UUID.randomUUID())
                .chatId(chatId)
                .text(messageText)
                .fromSpecialist(true)
                .read(false)
                .sentAt(LocalDateTime.now())
                .createAt(LocalDateTime.now())
                .build();

        URI uri = new URI("ws://localhost:8080/chat/" + chatId);
        when(handshakeInfo.getUri()).thenReturn(uri);
        when(webSocketSession.getHandshakeInfo()).thenReturn(handshakeInfo);
        when(messageRepository.save(any(MessageEntry.class))).thenReturn(Mono.just(savedMessage));

        WebSocketMessage wsMessage = mock(WebSocketMessage.class);
        when(wsMessage.getPayloadAsText()).thenReturn(jsonMessage);
        when(webSocketSession.receive()).thenReturn(Flux.just(wsMessage));
        when(webSocketSession.send(any())).thenReturn(Mono.empty());
        lenient().when(webSocketSession.textMessage(anyString())).thenAnswer(invocation -> {
            String text = invocation.getArgument(0);
            WebSocketMessage msg = mock(WebSocketMessage.class);
            when(msg.getPayloadAsText()).thenReturn(text);
            return msg;
        });

        // Act
        Mono<Void> result = chatService.handle(webSocketSession);

        // Assert
        StepVerifier.create(result)
                .verifyComplete();

        ArgumentCaptor<MessageEntry> messageCaptor = ArgumentCaptor.forClass(MessageEntry.class);
        verify(messageRepository, times(1)).save(messageCaptor.capture());

        MessageEntry capturedMessage = messageCaptor.getValue();
        assertThat(capturedMessage.isFromSpecialist()).isTrue();
    }

    @Test
    void shouldHandleMessageFromClient() throws Exception {
        // Arrange
        String messageText = "Сообщение от клиента";
        Message.CreateRequest createRequest = new Message.CreateRequest(messageText, false);
        String jsonMessage = objectMapper.writeValueAsString(createRequest);

        MessageEntry savedMessage = MessageEntry.builder()
                .id(UUID.randomUUID())
                .chatId(chatId)
                .text(messageText)
                .fromSpecialist(false)
                .read(false)
                .sentAt(LocalDateTime.now())
                .createAt(LocalDateTime.now())
                .build();

        URI uri = new URI("ws://localhost:8080/chat/" + chatId);
        when(handshakeInfo.getUri()).thenReturn(uri);
        when(webSocketSession.getHandshakeInfo()).thenReturn(handshakeInfo);
        when(messageRepository.save(any(MessageEntry.class))).thenReturn(Mono.just(savedMessage));

        WebSocketMessage wsMessage = mock(WebSocketMessage.class);
        when(wsMessage.getPayloadAsText()).thenReturn(jsonMessage);
        when(webSocketSession.receive()).thenReturn(Flux.just(wsMessage));
        when(webSocketSession.send(any())).thenReturn(Mono.empty());
        lenient().when(webSocketSession.textMessage(anyString())).thenAnswer(invocation -> {
            String text = invocation.getArgument(0);
            WebSocketMessage msg = mock(WebSocketMessage.class);
            when(msg.getPayloadAsText()).thenReturn(text);
            return msg;
        });

        // Act
        Mono<Void> result = chatService.handle(webSocketSession);

        // Assert
        StepVerifier.create(result)
                .verifyComplete();

        ArgumentCaptor<MessageEntry> messageCaptor = ArgumentCaptor.forClass(MessageEntry.class);
        verify(messageRepository, times(1)).save(messageCaptor.capture());

        MessageEntry capturedMessage = messageCaptor.getValue();
        assertThat(capturedMessage.isFromSpecialist()).isFalse();
    }
}

