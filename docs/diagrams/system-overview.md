# System Overview

```
+---------------------------+
|       Beamrider Node      |
+---------------------------+
|      pi-log Container     |
+---------------------------+
|  Sensor Drivers (plugins) |
+---------------------------+
|      Scheduler            |
+---------------------------+
|   SQLite Queue (WAL)      |
+---------------------------+
|       PushClient          |
+---------------------------+
|       Beamwarden          |
+---------------------------+
```

pi‑log is a portable ingestion hub deployed and managed by Quasar.
