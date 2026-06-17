### Accessing Comparer
```
bash

# Tab: Comparer (next to Decoder)
# Send requests to Comparer by right-clicking -> "Send to Comparer"
```


### Comparing Two Requests/Responses

```
┌─────────────────────────────────────────────────────────────────────────────┐  
│ COMPARER - Request 1 vs Request 2 │  
├─────────────────────────────────────────────────────────────────────────────┤  
│ Words: 18 differences (88% different) │  
│ │  
│ ┌─────────────────────────────────────────────────────────────────────────┐ │  
│ │ Original: │ Modified: │ │  
│ ├─────────────────────────────────┼───────────────────────────────────────┤ │  
│ │ GET /products.php?id=1 │ GET /products.php?id=1' │ │  
│ │ │ │ │  
│ │ Product: Laptop │ <font color="red">You have an error │ │  
│ │ Description: High perf laptop │ in your SQL syntax...</font> │ │  
│ └─────────────────────────────────┴───────────────────────────────────────┘ │  
│ │  
│ [Words] [Bytes] [Sync] [Copy to Repeater] │  
└─────────────────────────────────────────────────────────────────────────────┘
```

### Use Case: Finding SQL Injection

```
┌─────────────────────────────────────────────────────────────────────────────┐  
│ COMPARER - True vs False Condition │  
├─────────────────────────────────────────────────────────────────────────────┤  
│ Original (True): Modified (False): │  
│ 1 AND 1=1 1 AND 1=2 │  
│ │  
│ Product: Laptop Product: No products found │  
│ Description: High perf Description: (empty) │  
│ Price: $999 Price: (empty) │  
│ │  
│ Differences detected! Boolean-based SQLi confirmed! │  
└─────────────────────────────────────────────────────────────────────────────┘
```