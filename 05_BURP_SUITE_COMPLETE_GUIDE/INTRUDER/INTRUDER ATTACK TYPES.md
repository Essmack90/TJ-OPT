### Attack Type: Sniper (Single parameter)
```

┌─────────────────────────────────────────────────────────────────────────────┐  
│ ATTACK TYPE: Sniper │  
├─────────────────────────────────────────────────────────────────────────────┤  
│ GET /products.php?id=§1§&user=admin HTTP/1.1 │  
│ │  
│ Only position markers (§) matter - rest of request is static │  
│ │  
│ Payloads: 1,2,3,4,5 │  
│ │  
│ Requests sent: │  
│ 1. id=1&user=admin │  
│ 2. id=2&user=admin │  
│ 3. id=3&user=admin │  
│ 4. id=4&user=admin │  
│ 5. id=5&user=admin │  
│ │  
│ Use when: Testing one parameter at a time │  
└─────────────────────────────────────────────────────────────────────────────┘
```

### Attack Type: Battering Ram (Same value to all markers)

```
┌─────────────────────────────────────────────────────────────────────────────┐  
│ ATTACK TYPE: Battering Ram │  
├─────────────────────────────────────────────────────────────────────────────┤  
│ GET /products.php?id=§1§&user=§2§ HTTP/1.1 │  
│ │  
│ Both markers get the SAME value from payload list │  
│ │  
│ Payloads: admin, root, user │  
│ │  
│ Requests sent: │  
│ 1. id=admin&user=admin │  
│ 2. id=root&user=root │  
│ 3. id=user&user=user │  
│ │  
│ Use when: Both parameters should have same value (rare) │  
└─────────────────────────────────────────────────────────────────────────────┘
```

### Attack Type: Pitchfork (Different values per marker)

```
┌─────────────────────────────────────────────────────────────────────────────┐  
│ ATTACK TYPE: Pitchfork │  
├─────────────────────────────────────────────────────────────────────────────┤  
│ GET /products.php?id=§1§&user=§2§ HTTP/1.1 │  
│ │  
│ Payload Set 1: 1,2,3,4,5 │  
│ Payload Set 2: admin, root, user, guest, test │  
│ │  
│ Requests sent: │  
│ 1. id=1&user=admin │  
│ 2. id=2&user=root │  
│ 3. id=3&user=user │  
│ 4. id=4&user=guest │  
│ 5. id=5&user=test │  
│ │  
│ Use when: Testing pairs (user:password, id:token) │  
│ Stops when shortest payload list ends │  
└─────────────────────────────────────────────────────────────────────────────┘
```

### Attack Type: Cluster Bomb (All combinations)

```
┌─────────────────────────────────────────────────────────────────────────────┐  
│ ATTACK TYPE: Cluster Bomb │  
├─────────────────────────────────────────────────────────────────────────────┤  
│ POST /login.php HTTP/1.1 │  
│ user=§user§&pass=§pass§ │  
│ │  
│ Payload Set 1 (Users): admin, root, user │  
│ Payload Set 2 (Passwords): pass123, pass456, pass789 │  
│ │  
│ Requests sent (3x3=9 total): │  
│ 1. admin:pass123 │  
│ 2. admin:pass456 │  
│ 3. admin:pass789 │  
│ 4. root:pass123 │  
│ 5. root:pass456 │  
│ 6. root:pass789 │  
│ 7. user:pass123 │  
│ 8. user:pass456 │  
│ 9. user:pass789 │  
│ │  
│ Use when: Testing all combinations (password spraying, enumeration) │  
│ WARNING: Can generate huge numbers of requests! │  
└─────────────────────────────────────────────────────────────────────────────┘

```
