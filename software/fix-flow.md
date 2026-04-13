## Fix flow for log4shell

First, read [problem-with-code](problem-with-code.md) markdown file. 

It can be seen on [IBM log4shell documentation](https://www.ibm.com/think/topics/log4shell#280060107) that the developers tried multiple times to solve the issue, but caused other CVEs. So we will focus here on: CVE-2021-45046, CVE-2021-45105 and CVE-2021-44832.

### Find code changes

We ran first in the log4j repository a command to see if they talked about this: 

```bash
git log -S "CVE-2021-45046" --name-only --format="" | sort -u | awk 'NF' | xargs code
git log -p -S "CVE-2021-45046" > cve_commits.diff
```

## CVE-2021-45046 (First patch)


> The first patch Apache released, Log4J version 2.15.0, closed much of the Log4Shell vulnerability. However, hackers could still send malicious JNDI lookups to systems that used certain non-default settings. Apache addressed this flaw with Log4J version 2.16.0. "IBM"

Jira ticket: [JNDI lookups in layout (not message patterns) enabled in Log4j2 < 2.16.0](https://issues.apache.org/jira/browse/LOG4J2-3221) 

What they talked about it: 
```diff
-[#CVE-2021-45046]
-=== {cve-url-prefix}/CVE-2021-45046[CVE-2021-45046]
-
-[cols="1h,5"]
-|===
-|Summary |Thread Context Lookup is vulnerable to remote code execution in certain configurations
-|CVSS 3.x Score & Vector |9.0 CRITICAL (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
-|Components affected |`log4j-core`
-|Versions affected |`[2.0-beta9, 2.3.1) ∪ [2.4, 2.12.3) ∪ [2.13.0, 2.17.0)`
-|Versions fixed |`2.3.1` (for Java 6), `2.12.3` (for Java 7), and `2.17.0` (for Java 8 and later)
-|===
-
-[#CVE-2021-45046-description]
-==== Description
-
-It was found that the fix to address <<CVE-2021-44228>> in Log4j `2.15.0` was incomplete in certain non-default configurations.
-When the logging configuration uses a non-default Pattern Layout with a Thread Context Lookup (for example, `$${ctx:loginId}`), attackers with control over Thread Context Map (MDC) can craft malicious input data using a JNDI Lookup pattern, resulting in an information leak and remote code execution in some environments and local code execution in all environments.
-Remote code execution has been demonstrated on macOS, Fedora, Arch Linux, and Alpine Linux.
-
-Note that this vulnerability is not limited to just the JNDI lookup.
-Any other Lookup could also be included in a Thread Context Map variable and possibly have private details exposed to anyone with access to the logs.
-
-Note that only the `log4j-core` JAR file is impacted by this vulnerability.
-Applications using only the `log4j-api` JAR file without the `log4j-core` JAR file are not impacted by this vulnerability.
-
-[#CVE-2021-45046-mitigation]
-==== Mitigation
-
-Upgrade to Log4j `2.3.1` (for Java 6), `2.12.3` (for Java 7), or `2.17.0` (for Java 8 and later).
-
-[#CVE-2021-45046-credits]
-==== Credits
-
-This issue was discovered by Kai Mindermann of iC Consult and separately by 4ra1n.
-
-Additional vulnerability details discovered independently by Ash Fox of Google, Alvaro Muñoz and Tony Torralba from GitHub, Anthony Weems of Praetorian, and RyotaK (@ryotkak).
-
-[#CVE-2021-45046-references]
-==== References
-
-- {cve-url-prefix}/CVE-2021-45046[CVE-2021-45046]
-- https://issues.apache.org/jira/browse/LOG4J2-3221[LOG4J2-3221]
```


From `git log --oneline --grep="JNDI"` we identified the first commit patch: `d82b47c6fa LOG4J2-3201 - Limit the protocols JNDI can use by default. Limit the servers and classes that can be accessed via LDAP.` so lets start investigating the commit. We can use one of those commands: 
```
git show d82b47c6fa > cve-2021-45046.diff
```
or 
```
git config --global diff.tool vscode
git config --global difftool.vscode.cmd 'code --wait --diff $LOCAL $REMOTE'
git difftool d82b47c6fa^ d82b47c6fa
```