# Post-Mortem: Kafka Consumer Group Rebalance Cascade
## Incident Summary
Event processing lag accumulated exponentially as Kafka consumers repeatedly dropped out of consumer groups.

## Root Cause
Heavy record processing times exceeded `max.poll.interval.ms` (300s), causing Kafka brokers to mark workers dead and trigger continuous rebalance loops.

## Stack Trace Pattern
`org.apache.kafka.clients.consumer.CommitFailedException: Commit cannot be completed since the group has already rebalanced and assigned the partitions to another member.`

## Resolution
1. Increased `max.poll.interval.ms` and decreased `max.poll.records` batch size.
2. Moved heavy record processing off the main polling thread into worker thread pools.