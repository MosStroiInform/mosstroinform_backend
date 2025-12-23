package mifi.chat;

import mifi.chat.dto.ChatCacheProperties;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import reactor.core.publisher.Flux;

import java.time.Duration;

@SpringBootApplication
@EnableConfigurationProperties(ChatCacheProperties.class)
public class ChatApplication {

    public static void main(String[] args) {
        SpringApplication.run(ChatApplication.class, args);
    }


}
