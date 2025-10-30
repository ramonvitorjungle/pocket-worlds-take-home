# Ramon's PocketWorlds Take-Home

## On the Database choice

There are several great options for the database. I'll highlight a few candidates I considered and why I chose MongoDB.

### The candidates

All of these candidates would get the job done with different hardships and tradeoffs.
- MySQL/MariaDB
- PostgreSQL
- SQLite
- MongoDB
- Couchbase
- Redis

I'll go over each candidate in more details, to justify why MongoDB was chosen.

#### MySQL/MariaDB

This database needs no introduction. One of the most deployed databases in the world with a large community.

It would be a capable choice, especially if using Vitess, Aurora, MariaDB enterprise edition with asynchronous/synchronous replication.

The only downside is that it is somewhat challenging to shard the database. It would require significant effort to reach the design point of 10k qps.

Due to this reason, I chose MongoDB.

#### PostgreSQL

Another database that needs no introduction. A powerhouse in the relational world.

Postgres is ideal when you have a small number of connections, doing lots of inserts - due to MVCC - and reads.

For an application that might have many replicas connected to it, Postgres is not the best choice - requiring PGBouncer. Also, sharding and replicating is not as easy as it is with MongoDB.

#### SQLite

For a multi-tenant application, a small deployment, or a single-instance application, SQLite is a great choice. Litestream also makes it easy to replicate the database.

It is fast, easy to use, and can handle [quite the load](https://www.youtube.com/watch?v=VzQgr-TgBzc). Even the comparison of Turso vs SQLite is very anti-climatic, due to the ["bad operating region" being still 1ms queries and 50k reads per second.](https://turso.tech/blog/beyond-the-single-writer-limitation-with-tursos-concurrent-writes) 

SQLite can be very good for a high read load and a low write load, but not for a high write load. It is not a great choice for applications with multiple deployments and multiple instances, due to the locking mechanism when writing.

This limitation can be circumvented by using one database per tenant and isolating the writes into a service, but it is not a trivial task. Furthermore, once you reach the limits of the database, there are no levers to scale it.

Even in the scenario where using one database per tenant is viable, you still have to take into account the multiple migrations that need to be done. For instance, having 100k tenants, you would need to migrate 100k databases, possibly with multiple tables.

Technically, it would be possible to stick with this, but simplicity is king and MongoDB is a better choice in this case.

#### MongoDB

MongoDB has easy replication, easier - emphasis on the "er" - sharding, has lots of documentation, has a DBaaS, and is a great choice for a multi-tenant application.

Every time I used MongoDB, it was surprisingly easy to scale the database. Also, Mongo offers Map-Reduce interfaces, CDC built-in, and the flexible schema makes some hard relational problems trivial.

Of course, MongoDB has its hardships, such as `mongos` connection issues and the possibility of having a misconfigured write concern.

You cannot just connect infinite clients to the `mongos` instance - it will falter. There is a need to either proxy the connections or rebalance the shards.

When it comes to the write concern, `majority` with journaling and multi-az replicas will greatly reduce the risk of data loss.

Furthermore, since your company uses MongoDB, choosing it for the take-home makes it easier to communicate and explain my decisions with you.

#### Couchbase

Couchbase is a great database. It has a simple architecture, is easy to use, and scales almost linearly with the number of nodes.

Unfortunately, it is less popular than MongoDB and this might make it harder to find support.

Therefore, I chose MongoDB.

#### Redis

It is a great database for in-memory caching. Performant, Easy to use, but requires most of the dataset to live in memory.

Also, does not have a great indexing mechanism, relying on basic data structures instead. This makes it hard to query the database and perform complex operations.

Hence, I chose MongoDB.

## On the Event System

I chose RabbitMQ as the message broker. It is easy, simple, has an admin interface, and I'm familiar with it.

RabbitMQ also has its quirks, such as the fact that the Classic Queues aren't written to the disk immediately, nor are replicated by default.

Also, the mirroring for Classic Queues has been deprecated, with a weird ring architecture that would show cracks when having several replicas.

The current version of RabbitMQ has two different mechanisms for message passing: quorum queues and streams.

Quorum queues are a general replicated queue. The support dead-lettering, have durability, low memory footprint, and are easy to use.

Streams are great when low latency is a must. They are an append-only log with a retention period, little memory footprint, replay, and designed for high throughput.

I chose quorum queues for the take-home.

### A note on losing messages with RabbitMQ + Python

It is generally possible to lose messages when using RabbitMQ with Python. To avoid this, I chose to use the quorum queues - even though there is a single broker for this example.

With multiple brokers, the messages would not be lost in the event of a broker failure due to replication.

Additionally, there are considerations to be made involving the trio MongoDB - Python - RabbitMQ.

Ideally, we want to have a transaction for this operation. 2PC is inappropriate, due to the issues that might arise with it - dangling transactions, low throughput, etc.

There are a few candidate architectures that can be used to solve this problem:
- Command Queues/"Listen to Yourself"
- CDC
- Outbox Pattern

I'll discuss a little these alternatives and why I chose the Outbox Pattern.

#### Command Queues/"Listen to Yourself"

This pattern involves publishing the message to a queue and avoiding to write it to the database. When the consumer receives the message, it will then write it to the database.

This assures that there are no inconsistencies between the database and the queue, and no concurrency issues. Furthermore, it is easy to implement.

However, this pattern offers only eventual consistency, which is unsuitable for many applications.

It is not clear from the document whether this would be a great fit, but a sensible default is to use another pattern, as they offer better guarantees.

#### CDC - Change Data Capture

Since MongoDB has a CDC mechanism, it is possible to use it to solve this problem. It is essentially a tap on the database oplog, but more akin to a logical replication rather than raw commands.

This pattern offers strong consistency, and it is easy to implement. It also is robust to failures, since we have a pointer to the current state of the database stream.

Furthermore, it is possible to fetch the current state of the database, and establish a new stream from there.

Unfortunately, it is not the best fit for this application, since we are not interested in the current state of the database, but rather in the changes that happened since the last time we fetched the state.

#### Outbox Pattern

This pattern is significantly more complex than the previous ones. It involves writing the message to the database, and then publishing it to a queue using a worker or a CDC mechanism.

It burdens the database with the message reads and writes, increases the total latency when consuming the messages, but it offers robustness, no concurrency issues, at-least-once delivery, and a transactional guarantee.

The implementation leverages a collection called `messages` and Mongo's flexible schema, with a worker polling the collection for new messages and publishing them to the queue.

## Environment and Deployment

I set up a docker-compose.yml that you can use to run the application. The trickiest part was to make sure that the database was ready before the application started.

They all have healthchecks and restart on errors. The API is somewhat robust to the failure of the database. The workers might not be as robust, but since they are not client facing, they can be restarted safely.

## Observability

I started setting up open telemetry and prometheus on the application, but found it to be more involved than the time proposed in the shared document.

I'll describe what would be the ideal setup and how I would go about it.

For logging, I would use a log with the trace id, the timestamp, message, level, function or module that is calling and the line.

This makes it way easier to search for a specific trace id and to debug issues quickly. Infrastructure-wise, Loki with Promtail and Grafana would be a good choice.

For metrics, I would use Prometheus to expose the metrics. I'd have a Prometheus server that would scrape the metrics from the application every X seconds - X to be tuned for each application. 

General metrics I can't live without:
- Number of requests
- Requests per second
- Number of errors
- Errors per status code family or groups - 5XX, 404, 403, 401, etc.
- Latency
- Number of connections to the database
- Number of messages in the queue
- Number of messages in the DLQ
- Number of successfully processed messages
- Number of failures to process a message
- Number of times a message was delivered to the consumer
- Number of pending messages in the database

Tracing, I'd use something like Tempo. It enables distributed tracing, and it has a UI that can be used to visualize the traces along Grafana. The tracing view can go as deep as getting the payload a worker received, the query the database executed, which services are part of the request, etc.

In the absence of a tracing system, I'd use a log with the trace id to fetch the payload or id of the message. Then, I'd find that in the logs for the worker that processed the message.

## Fault Tolerance

### Broker and Database failures
If the broker goes down, the api will not fail to respond. The messages will be stored in the database and will be processed when the broker comes back. The outbox worker will likely be on crash loop, but it will be restarted automatically. So will the queue worker.

If the database goes down, the api will fail with a 500 error. The outbox worker will likely crash and be on crash loop, but will be restarted until the database comes back. The queue worker will be idle waiting for messages.

### Persistence errors
Regarding persistence errors, ideally each API being used is idempotent so that we can retry. Depending on the error, we might want to retry only a few times, or start a circuit breaker. For instance, a 500 error might be a temporary error, so we might want to retry a few times before opening a circuit breaker. For a 401, no retry is needed and we can just consume the message.

This is a great strategy for high throughput endpoints, to avoid the barraging of events after an internal failure.

### Idempotency
Regarding idempotency, in the current setup, each message has its own uuid. We can encapsulate the idempotency logic in a decorator, which goes to the database and checks if the message has already been processed. If it has, we can safely consume the message. If not, we can process it.

The idea is to start a transaction, and then commit the transaction if the message was processed successfully. By the end of the transaction, we can store in the database that the message was processed. I'll try to implement this in the project

## Scaling and Future Growth

### Scaling the API and the database
For scaling reads, the API can be scaled horizontally by adding more replicas, with a load balancer in front of them. MongoDB enables easy replication and it would be possible to implement a tiered caching mechanism, with a first layer of caching in the API and a second layer in a Redis cluster.

This caching comes with its challenges and tradeoffs, but I've found that even a 5s in-memory cache in the API can greatly help with the performance.

For scaling writes, MongoDB shards in an easier way than with PostgreSQL or MySQL. Though it has its challenges, such as sharding imbalaces and connection issues, it can be scaled horizontally by adding more shards - in a very simplistic summary.

I believe that 10k QPS in a very read heavy scenario can be achieved with a single shard, a N nodes replica set, a Redis, load-balancing + horizontal scaling in the API, and an in-memory cache.

For a 10k QPS in a very write heavy scenario, it would be possible to scale the database (the weak link here) by adding more shards - probably not the optimal way of doing it-, batching the writes with a queue or a stream - this would be my best bet.

The inner parts of the application could scale horizontally by adding more replicas - should the application tolerate this, i.e., it does not require message ordering or alike. 

The outbox worker could be rewritten in a different language, such as Go, to increase the throughput. Go would be a great candidate due to its ability to use multiple cores with ease. It would be possible to also partition the outbox worker by message type, so that it can be scaled independently.

### On multi-region setups

For a multi-region setup, I'd avoid it as much as possible due to one thing: egress. Egress is a b*tch. I'd start with a multi-AZ setup and should you need a multi-region setup, my recommendation would be to have an active-passive architecture.

A small cluster in the secondary region with few replicas. A replicated read-only replica for the database - to be promoted should the primary region fails, a read-only replica for the message broker - same idea, and an easy, automated way to failover and scale the cluster should the primary region fails.

A note on data loss budget: it is still possible to be behind the primary region due to replication lag. Some service offerings can be as much as 5 minutes behind the primary region.

### Event replay and eventual consistency

Using queues, event replay is possible but harder to do than in a streaming setup. We can always go to the database and fetch the messages sent, order them by timestamp, and replay them.

This is not ideal, but it is possible if the consumers are idempotent. As for the eventual consistency challenges, should the workers update the database state in a meaningful way, we might face a few challenges.

For instance, let's say we have a chat in-game where we persist every message, but we scan them for abuse. It would be ideal to have such abuse detection system on the request, but this is not always possible to implement.

Oftentimes, we perform these heavy operations in the background and have the messages be passed along to the clients. Should something be detected, we can come back and filter the messages, requesting an update of the messages from the clients.

For these issues, we have a few strategies that might work well:
- If the time between reads takes X seconds and the whole async operation reliably takes less than X/2 seconds, we can safely bet that the system will not be impacted by the event lag.
For instance, if players only check their inboxes every 10 seconds in a polling operation, and the whole async operation of collecting the messages takes less than 5 seconds, it would be as if the system was synchronous. There would be little to no impact on the user experience.
- If the feature can be implemented in an async manner, we can "set the expectation" that the system will process this on the background. For example, AWS does this all the time. They just return a message like "We got your request, we will process it in the background and will let you know when it is done."
This works nicely for features that absolutely need to be processed in the background, e.g. image processing.
- Another possibility is using an optimistic client. The client simulates the result of the async operation as if it was successful, while it is waiting for the result. Since games oftentimes have animations, rituals, intros, etc., the client leverages this to wait for the result.
Should the response be an error, the client can simply resync the state and show an error message to the user. Works well if the operations are extremely reliable.

However, this is not always possible. Some features annoyingly take a long time to process. Unfortunately, there is no magical solution for these cases and you either compromise by accepting the eventual consistency with intermediate states to give some visibility, or you block the client until the operation is done.

The greatest issue with eventual consistency happens when operations have requirements on the order of execution. In these cases, the best solution is to go with a SAGA pattern in a choreography or an orchestrator. I tend to go with the choreography pattern, since it is easier to implement.

In these cases, the workers need to be idempotent, the events need to be in an outbox pattern to avoid message loss, and each service must have a mechanism to make the operation in a single transaction. Then, it is a matter of finding the order of execution, and implementing.

The case I have to explain this in-depth relates to my current work, where we have visits, offers and contracts for buying houses.

In this case, we need the visit to be DONE before someone can put an offer on it. Also, the contract needs an offer before it can be signed. For this particular flow - grossly simplified - we publish the DONE events to a queue, which then consumes and enables the offer to be created.

As soon as the offer is created, it evolves in a state machine, eventually going into an ACCEPTED state. This then triggers the contract creation.

There is ordering, there are multiple services, and there is a lot of state to manage. That's where the SAGA truly shines.
