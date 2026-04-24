## Fix flow for log4shell

First, read [problem-with-code](problem-with-code.md) markdown file. 

It can be seen on [IBM log4shell documentation](https://www.ibm.com/think/topics/log4shell#280060107) that the developers tried multiple times to solve the issue, but caused other CVEs. So we will focus here on: CVE-2021-45046, CVE-2021-45105 and CVE-2021-44832.

-----
### Solution Flow and Patch Timeline


**November 29, 2021**
The initial mitigation strategy began by disabling lookups by default. Following this change, lookups required explicit configuration to function.

  * **Commit:** [001aaada7d](https://www.google.com/search?q=https://github.com/apache/logging-log4j2/commit/001aaada7d)
  * **Jira:** [LOG4J2-3198](https://issues.apache.org/jira/browse/LOG4J2-3198)

**December 4–5, 2021**
To address the primary vulnerability, the developers disabled most JNDI protocols and restricted LDAP access. They implemented a JNDI manager that, by default, restricted lookups using `ALLOWED_PROTOCOLS`, `ALLOWED_HOSTS`, and `ALLOWED_CLASSES`.

  * **Commit:** [c77b3cb393](https://www.google.com/search?q=https://github.com/apache/logging-log4j2/commit/c77b3cb393)

An additional commit was integrated to further strengthen these LDAP restrictions.

  * **Commit:** [d82b47c6fa](https://www.google.com/search?q=https://github.com/apache/logging-log4j2/commit/d82b47c6fa)
  * **Jira:** [LOG4J2-3201](https://issues.apache.org/jira/browse/LOG4J2-3201)

While this was intended to resolve the issue, a bypass remained in `PatternLayout` involving Thread Context Lookups (e.g., `$ctx:userAgent`). If an attacker injected a payload via `MDC.put("userAgent", "${jndi:ldap://...")`, the engine's recursive evaluation still triggered the JNDI lookup. This bypass was tracked as **CVE-2021-45046**.

**December 13–14, 2021**
To resolve CVE-2021-45046, the string substitution recursion logic was completely removed.

  * **Commit:** [806023265f](https://www.google.com/search?q=https://github.com/apache/logging-log4j2/commit/806023265f)

Following this patch, a new vulnerability emerged: **CVE-2021-45105** (a Denial of Service attack). It was discovered that attackers could force infinite recursion using self-referential lookups, such as `${ctx:foo:-${ctx:foo}}`. This resulted in a `StackOverflowError`, crashing the application.

**December 18, 2021**
To mitigate the DoS vulnerability, the developers patched the `StackOverflowError` in `OptionConverter.substVars()` by adding logic to detect cycle references.

  * **Commit:** [dea97d90dd](https://www.google.com/search?q=https://github.com/apache/logging-log4j2/commit/dea97d90dd)

**December 28, 2021**
Despite previous restrictions, a final vulnerability was identified: **CVE-2021-44832**. This involved a Remote Code Execution flaw where the JDBC Appender could be manipulated to use a malicious JNDI URI.

To definitively solve the problem, the developers moved JNDI into its own isolated module and strictly limited it to the `java` protocol.

  * **Commits:** [14e307ac82](https://www.google.com/search?q=https://github.com/apache/logging-log4j2/commit/14e307ac82), [f6564bb993](https://www.google.com/search?q=https://github.com/apache/logging-log4j2/commit/f6564bb993), [95b24f77e7](https://www.google.com/search?q=https://github.com/apache/logging-log4j2/commit/95b24f77e7)
  * **Jira:** [LOG4J2-3242](https://issues.apache.org/jira/browse/LOG4J2-3242)

The series of architectural vulnerabilities was ultimately resolved with the release of Log4j version 2.17.1.



### Official document about log4shell

```bash
git log -S "CVE-2021-45046" --name-only --format="" | sort -u | awk 'NF' | xargs code
git log -p -S "CVE-2021-45046" > cve_commits.diff
```

The official document about how log4j solved the issue can be found in this repository as [cve_commits.txt](cve_commits.txt). 