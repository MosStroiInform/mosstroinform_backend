package mifi.chat.dto;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;

import java.time.temporal.ChronoUnit;
import java.util.concurrent.TimeUnit;

@Data
@ConfigurationProperties(prefix = "chat.cache")
public class ChatCacheProperties {

    private long keepAlive;
    private ChronoUnit unit;

    private long tickTimer = 60;

    private TimeUnit tickUnit = TimeUnit.SECONDS;

}
