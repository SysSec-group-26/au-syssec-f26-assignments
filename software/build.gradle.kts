plugins {
    java
    id("com.github.johnrengelman.shadow") version "7.1.2"
}

group = "com.study"
version = "1.0"

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.apache.logging.log4j:log4j-core:2.0-rc1")
    implementation("org.apache.logging.log4j:log4j-api:2.0-rc1")
}

tasks.jar {
    manifest {
        attributes["Main-Class"] = "com.study.VulnerableApp"
    }
}

tasks.shadowJar {
    archiveBaseName.set("log4j-replication")
    archiveClassifier.set("")
    archiveVersion.set("1.0")
}
