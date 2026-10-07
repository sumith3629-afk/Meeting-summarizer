# Meeting Minutes & Executive Record

## 1. Executive Summary
The weekly back-end engineering sync addressed high P99 latency spikes, database scaling options, and upcoming release tasks. Key decisions included maintaining PostgreSQL, implementing a readiness cache layer, and assigning specific tasks with deadlines. Legacy cleanup and load testing plan were noted for future assignment.

## 2. Organized Meeting Minutes
### 2.1 Database Migration and Consistency Trade-offs
Reviewed recent production telemetry showing a 45% degradation in response times during peak hours. Discussed Rahul’s proposal to migrate from PostgreSQL to MongoDB, but decided to retain PostgreSQL due to critical transactional ledger requirements and consistency trade-offs.

### 2.2 Latency Spike Mitigation
Explored options for addressing P99 latency spikes, including Alex’s proposal to switch from REST to gRPC. Deferred gRPC decision pending benchmarking. Approved adding a **readiness cache** layer for read-heavy endpoints to reduce latency below 120ms.

### 2.3 Monitoring and Observability
Noted the need for Prometheus alerts and Grafana dashboards for Kubernetes pods. Assigned Rahul to configure these before **October 14**.

### 2.4 Legacy Code and Documentation Cleanup
Identified clutter in Docker Compose configs and dead environment variables in the repository. No owner assigned yet; will address later.

### 2.5 Upcoming Release Tasks
Assigned Alex to draft an automated load testing plan, though no deadline was set.

## 3. Key Decisions
- Stick with PostgreSQL and **not migrate to MongoDB** this quarter due to transactional ledger requirements and consistency concerns.
- Implement a **readiness cache layer** for read-heavy endpoints to mitigate P99 latency spikes.

## 4. Action Items
| # | Task | Owner | Deadline |
|---|---|---|---|
| 1 | Implement and test the readiness cache cluster for read-heavy endpoints | **Zira** | October 10 |
| 2 | Configure Prometheus alerts and Grafana dashboards for Kubernetes pods | **Rahul** | October 14 |
| 3 | Draft the automated load testing plan | **Alex** | unspecified |
