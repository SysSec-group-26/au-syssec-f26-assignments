# Stage 1: Build the JAR using Maven inside Docker (no local Maven needed)
FROM maven:3.6.3-jdk-8 AS builder

WORKDIR /build

# Copy Maven project descriptor and source
COPY pom.xml .
COPY src ./src

# Download dependencies and compile
RUN mvn clean package -DskipTests

# Stage 2: Run with JDK 8u111 where trustURLCodebase=true by default,
# enabling unauthenticated RCE via JNDI for study purposes.
FROM openjdk:8u111-jdk-alpine

WORKDIR /app

COPY --from=builder /build/target/log4j-replication-1.0.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]