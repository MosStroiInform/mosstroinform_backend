package mifi.chat.dto;


import com.fasterxml.jackson.annotation.JsonTypeName;

import java.util.UUID;

public class Message {

    @JsonTypeName("CREATE")
    public record CreateRequest(String text, boolean fromSpecialist) implements Action {
        @Override
        public Type getType() {
            return Type.CREATE;
        }
    }

    @JsonTypeName("READ")
    public record ReadRequest(UUID messageId) implements Action {
        @Override
        public Type getType() {
            return Type.READ;
        }
    }

}
