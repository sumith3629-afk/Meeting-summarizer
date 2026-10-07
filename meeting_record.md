# Meeting Minutes & Executive Record

## 1. Executive Summary
The meeting addressed high P99 latency spikes, database scaling options, and release preparations. Key decisions included maintaining PostgreSQL, implementing a readies cache layer for latency reduction, and assigning tasks for monitoring setup, legacy cleanup, and load testing planning. Owners and deadlines were assigned for most tasks, with two items deferred for later assignment or deadline confirmation.

## 2. Organized Meeting Minutes
### 2.1 Database Migration and Consistency Trade-offs
Reviewed recent production telemetry showing a 45% degradation in response times during peak hours. Discussed Rahul’s suggestion to migrate from PostgreSQL to MongoDB, but concluded that the relational schema is critical for the transactional ledger. Decided to **not** migrate to MongoDB this quarter due to consistency concerns.

### 2.2 Latency Spike Mitigation
Explored options to address P99 latency spikes, including Alex’s proposal to switch from REST to gRPC. Agreed that gRPC requires further benchmarking before implementation. Approved adding a **readies** cache layer in front of read-heavy endpoints as an immediate solution to reduce latency below 120ms.

### 2.3 Monitoring and Alerting Setup
Assigned Rahul to configure Prometheus alerts and Grafana dashboards for Kubernetes pods, with a deadline of **October 14**.

### 2.4 Legacy Code and Documentation Cleanup
Noted clutter in the repository from old Docker Compose configs and dead environment variables. No owner or deadline assigned yet; will be addressed later.

### 2.5 Load Testing Plan
Assigned Alex to draft an automated load testing plan, though no deadline was specified.

## 3. Key Decisions
- Stick with PostgreSQL and **not** migrate to MongoDB this quarter.
- Implement a **readies** cache layer for read-heavy endpoints to reduce P99 latency below 120ms.

## 4. Action Items
| # | Task | Owner | Deadline |
|---|---|---|---|
| 1 | Implement and test the readies cache cluster for read-heavy endpoints | **Zira** | October 10 |
| 2 | Configure Prometheus alerts and Grafana dashboards for Kubernetes pods | **Rahul** | October 14 |
| 3 | Draft an automated load testing plan | **Alex** | unspecified |
