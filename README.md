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

It burdens the database with the message reads and writes, increases the total latency when consuming the messages, but it offers robustness, no concurrency issues, at least once delivery, and a transactional guarantee.

The implementation leverages a collection called `messages` and Mongo's flexible schema, with a worker polling the collection for new messages and publishing them to the queue.
