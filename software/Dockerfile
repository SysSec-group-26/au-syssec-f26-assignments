# Stage 1: Build the fat JAR using Gradle inside Docker (no local Gradle needed)
FROM gradle:7.6-jdk8 AS builder

WORKDIR /build

# Copy Gradle build files and source
COPY settings.gradle.kts build.gradle.kts ./
COPY src ./src

# Build the shadow (fat) JAR with all dependencies bundled
RUN gradle shadowJar --no-daemon

# Stage 2: Run with JDK 8u111 where trustURLCodebase=true by default,
# enabling unauthenticated RCE via JNDI for study purposes.
FROM openjdk:8u111-jdk-alpine

WORKDIR /app

COPY --from=builder /build/build/libs/log4j-replication-1.0.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]