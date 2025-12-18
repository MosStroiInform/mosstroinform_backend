package mifi.chat.services;

import lombok.Getter;
import lombok.RequiredArgsConstructor;
import mifi.chat.dto.ChatCacheProperties;
import mifi.chat.dto.ChatMessage;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Sinks;

import java.time.LocalDateTime;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;

@Component
@RequiredArgsConstructor
public class ChatRoomManager {

    private final ChatCacheProperties chatCacheProperties;

    private final Map<UUID, ChatRoom> chatRoomMap = new ConcurrentHashMap<>();

    private final ScheduledExecutorService executorService = Executors.newScheduledThreadPool(1);

    public ChatRoom getRoom(UUID uuid) {
        ChatRoom chatRoom = chatRoomMap.computeIfAbsent(uuid, this::createRoom);
        chatRoom.tick();
        return chatRoom;
    }

    private ChatRoom createRoom(UUID uuid) {
        ChatRoom chatRoom = new ChatRoom(Sinks.many().multicast().onBackpressureBuffer(10), LocalDateTime.now());
        executorService.schedule(new CleanTask(uuid), chatCacheProperties.getTickTimer(), chatCacheProperties.getTickUnit());
        return chatRoom;
    }

    @RequiredArgsConstructor
    private class CleanTask implements Runnable {

        private final UUID uuid;

        @Override
        public void run() {
            ChatRoom chatRoom = chatRoomMap.get(uuid);
            if (chatRoom == null) return;
            LocalDateTime deadlineTime = chatRoom.getLastUpdate() != null
                    ? chatRoom.getLastUpdate().plus(chatCacheProperties.getKeepAlive(), chatCacheProperties.getUnit())
                    : null;
            if (deadlineTime == null || LocalDateTime.now().isAfter(deadlineTime)) {
                chatRoomMap.remove(uuid);
            } else {
                executorService.schedule(new CleanTask(uuid), chatCacheProperties.getTickTimer(), chatCacheProperties.getTickUnit());
            }
        }
    }

    @Getter
    @RequiredArgsConstructor
    static class ChatRoom {
        private final Sinks.Many<ChatMessage> sink;
        private final LocalDateTime createAt;
        private LocalDateTime lastUpdate;

        public void tick() {
            lastUpdate = LocalDateTime.now();
        }
    }
}
