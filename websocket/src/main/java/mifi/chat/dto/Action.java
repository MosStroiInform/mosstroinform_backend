package mifi.chat.dto;


import com.fasterxml.jackson.annotation.JsonSubTypes;
import com.fasterxml.jackson.annotation.JsonTypeInfo;

@JsonTypeInfo(
        use = JsonTypeInfo.Id.NAME,
        property = "type",
        include = JsonTypeInfo.As.PROPERTY
)
@JsonSubTypes({
        @JsonSubTypes.Type(value = mifi.chat.dto.Message.CreateRequest.class, name = "CREATE"),
        @JsonSubTypes.Type(value = mifi.chat.dto.Message.ReadRequest.class, name = "READ")
})
public interface Action {

    Type getType();

    enum Type {
        CREATE,
        READ
    }
}
