# fire-risk-monitoring 

## System Architecture

          ┌─────────────────────────────────────────────┐
          │              Environment Data Sources        │
          │                                              │
          │   • Sensor Simulator (temperature, humidity, │
          │     soil moisture, smoke, wind)              │
          │   • Weather API / Weather Simulator          │
          └───────────────────┬──────────────────────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │    Message Bus    │
                     │      (Kafka)      │
                     │  env_raw_sensors  │
                     │    env_weather    │
                     └─────────┬──────────┘
                               │
                               ▼
                     ┌──────────────────┐
                     │     RisingWave    │
                     │   Sources & MVs   │
                     │  • mv_zone_env    │
                     │  • mv_risk        │
                     │  • mv_alerts      │
                     └───────┬────┬──────┘
                             │    │
               ┌─────────────┘    └───────────────┐
               ▼                                    ▼
     ┌────────────────────┐               ┌────────────────────┐
     │     Serving DB      │               │    Alerts Topic     │
     │      (Postgres)     │               │    fire_alerts      │
     └──────────┬──────────┘               └─────────┬───────────┘
                │                                     │
                ▼                                     ▼
      ┌────────────────────┐               ┌────────────────────┐
      │     API Backend     │               │  Notification Svc   │
      │   (REST/GraphQL)    │               │ (Email / Slack / SMS)│
      └──────────┬──────────┘               └────────────────────┘
                 │
                 ▼
      ┌────────────────────┐
      │   Dashboard / UI   │
      │  (Map + Graphs)    │
      └────────────────────┘

