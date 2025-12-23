# syntax=docker/dockerfile:1
# Этап сборки
FROM eclipse-temurin:21-jdk-alpine AS build

WORKDIR /app

# Копируем Maven wrapper
COPY mvnw .
COPY .mvn .mvn
RUN chmod +x ./mvnw

# Копируем pom.xml для кэширования зависимостей
COPY pom.xml .

# Скачиваем зависимости (кэшируется если pom.xml не изменился)
RUN ./mvnw dependency:go-offline -B

# Копируем исходный код
COPY src ./src

# Собираем приложение
RUN ./mvnw clean package -DskipTests

# Этап запуска
FROM eclipse-temurin:21-jre-alpine

WORKDIR /app

# Копируем собранный JAR из этапа сборки
COPY --from=build /app/target/chat-0.0.1-SNAPSHOT.jar app.jar

# Запускаем приложение
ENTRYPOINT ["java", "-jar", "app.jar"]

EXPOSE 8080

