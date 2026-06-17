```
### Payload Type: Simple List

┌─────────────────────────────────────────────────────────────────────────────┐  
│ PAYLOAD TYPE: Simple List │  
├─────────────────────────────────────────────────────────────────────────────┤  
│ Manually enter payloads: │  
│ │  
│ [X] admin │  
│ [X] root │  
│ [X] user │  
│ [X] test │  
│ [ ] guest (uncheck to skip) │  
│ │  
│ [Add] [Add from list] [Load] [Remove] [Clear] │  
└─────────────────────────────────────────────────────────────────────────────┘
```

### Payload Type: Runtime File

```

┌─────────────────────────────────────────────────────────────────────────────┐  
│ PAYLOAD TYPE: Runtime File │  
├─────────────────────────────────────────────────────────────────────────────┤  
│ File: /usr/share/wordlists/rockyou.txt │  
│ │  
│ [X] Match regex: ^[a-zA-Z0-9]{6,}$ (only alphanumeric 6+ chars) │  
│ [ ] Replace line │  
│ │  
│ Preview (first 5 lines): │  
│ 123456 │  
│ password │  
│ 123456789 │  
│ 12345 │  
│ 12345678 │  
└─────────────────────────────────────────────────────────────────────────────┘
```

### Payload Type: Numbers

```
┌─────────────────────────────────────────────────────────────────────────────┐  
│ PAYLOAD TYPE: Numbers │  
├─────────────────────────────────────────────────────────────────────────────┤  
│ Number range: 1 to 1000 │  
│ Step: 1 │  
│ Number format: [ ] Decimal [X] Hex [ ] Octal │  
│ │  
│ Generated payloads: 1, 2, 3, 4, 5... 1000 │  
│ │  
│ Use case: Brute forcing IDs, finding column count, port scanning │  
└─────────────────────────────────────────────────────────────────────────────┘
```

### Payload Type: Date/Time

```
┌─────────────────────────────────────────────────────────────────────────────┤  
│ PAYLOAD TYPE: Date/Time │  
├─────────────────────────────────────────────────────────────────────────────┤  
│ Format: yyyy-MM-dd │  
│ From: 2020-01-01 │  
│ To: 2024-12-31 │  
│ Step: 1 day │  
│ │  
│ Generated: 2020-01-01, 2020-01-02, 2020-01-03... │  
│ │  
│ Use case: Finding backups, log files, posts by date │  
└─────────────────────────────────────────────────────────────────────────────┘
```

### Payload Type: Brute Forcer

```
┌─────────────────────────────────────────────────────────────────────────────┐  
│ PAYLOAD TYPE: Brute Forcer │  
├─────────────────────────────────────────────────────────────────────────────┤  
│ Character set: abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789│  
│ Min length: 4 │  
│ Max length: 6 │  
│ │  
│ [ ] Process case variants │  
│ [X] All characters in set │  
│ │  
│ Generated: 4 char combinations: aaaa, aaab, aaac... (16,777,216 combos) │  
│ WARNING: This will generate millions of payloads! │  
└─────────────────────────────────────────────────────────────────────────────┘
```

### Payload Type: Custom Iterator

```
┌─────────────────────────────────────────────────────────────────────────────┐  
│ PAYLOAD TYPE: Custom Iterator │  
├─────────────────────────────────────────────────────────────────────────────┤  
│ Position 1: [a b c] │  
│ Position 2: [1 2 3] │  
│ Position 3: [_ - ] │  
│ │  
│ Generated: a1_, a1-, a2_, a2-, a3_, a3-, b1_, b1-... │  
│ │  
│ Use case: Creating custom username patterns (admin1, admin2, admin3...) │  
└─────────────────────────────────────────────────────────────────────────────┘
```

### Payload Type: Case Modification

```
┌─────────────────────────────────────────────────────────────────────────────┐  
│ PAYLOAD TYPE: Case Modification │  
├─────────────────────────────────────────────────────────────────────────────┤  
│ Base word: admin │  
│ │  
│ [X] admin │  
│ [X] Admin │  
│ [X] ADMIN │  
│ [ ] aDMIN (random case) │  
│ [ ] AdMiN (toggle case) │  
│ │  
│ Use case: Trying different capitalizations of credentials │  
└─────────────────────────────────────────────────────────────────────────────┘
```