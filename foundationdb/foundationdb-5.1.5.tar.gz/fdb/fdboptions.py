# FoundationDB Python API
# Copyright (c) 2013-2017 Apple Inc.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import types

NetworkOption = {
    "local_address" : (10, "Deprecated", type(''), "IP:PORT"),
    "cluster_file" : (20, "Deprecated", type(''), "path to cluster file"),
    "trace_enable" : (30, "Enables trace output to a file in a directory of the clients choosing", type(''), "path to output directory (or NULL for current working directory)"),
    "trace_roll_size" : (31, "Sets the maximum size in bytes of a single trace output file. This value should be in the range ``[0, INT64_MAX]``. If the value is set to 0, there is no limit on individual file size. The default is a maximum size of 10,485,760 bytes.", type(0), "max size of a single trace output file"),
    "trace_max_logs_size" : (32, "Sets the maximum size of all the trace output files put together. This value should be in the range ``[0, INT64_MAX]``. If the value is set to 0, there is no limit on the total size of the files. The default is a maximum size of 104,857,600 bytes. If the default roll size is used, this means that a maximum of 10 trace files will be written at a time.", type(0), "max total size of trace files"),
    "trace_log_group" : (33, "Sets the 'logGroup' attribute with the specified value for all events in the trace output files. The default log group is 'default'.", type(''), "value of the logGroup attribute"),
    "knob" : (40, "Set internal tuning or debugging knobs", type(''), "knob_name=knob_value"),
    "TLS_plugin" : (41, "Set the TLS plugin to load. This option, if used, must be set before any other TLS options", type(''), "file path or linker-resolved name"),
    "TLS_cert_bytes" : (42, "Set the certificate chain", type(b''), "certificates"),
    "TLS_cert_path" : (43, "Set the file from which to load the certificate chain", type(''), "file path"),
    "TLS_key_bytes" : (45, "Set the private key corresponding to your own certificate", type(b''), "key"),
    "TLS_key_path" : (46, "Set the file from which to load the private key corresponding to your own certificate", type(''), "file path"),
    "TLS_verify_peers" : (47, "Set the peer certificate field verification criteria", type(b''), "verification pattern"),
    "Buggify_enable" : (48, "", type(None), None),
    "Buggify_disable" : (49, "", type(None), None),
    "Buggify_section_activated_probability" : (50, "Set the probability of a BUGGIFY section being active for the current execution.  Only applies to code paths first traversed AFTER this option is changed.", type(0), "probability expressed as a percentage between 0 and 100"),
    "Buggify_section_fired_probability" : (51, "Set the probability of an active BUGGIFY section being fired", type(0), "probability expressed as a percentage between 0 and 100"),
    "disable_multi_version_client_api" : (60, "Disables the multi-version client API and instead uses the local client directly. Must be set before setting up the network.", type(None), None),
    "callbacks_on_external_threads" : (61, "If set, callbacks from external client libraries can be called from threads created by the FoundationDB client library. Otherwise, callbacks will be called from either the thread used to add the callback or the network thread. Setting this option can improve performance when connected using an external client, but may not be safe to use in all environments. Must be set before setting up the network. WARNING: This feature is considered experimental at this time. ", type(None), None),
    "external_client_library" : (62, "Adds an external client library for use by the multi-version client API. Must be set before setting up the network.", type(''), "path to client library"),
    "external_client_directory" : (63, "Searches the specified path for dynamic libraries and adds them to the list of client libraries for use by the multi-version client API. Must be set before setting up the network.", type(''), "path to directory containing client libraries"),
    "disable_local_client" : (64, "Prevents connections through the local client, allowing only connections through externally loaded client libraries. Intended primarily for testing.", type(None), None),
    "disable_client_statistics_logging" : (70, "Disables logging of client statistics, such as sampled transaction activity.", type(None), None),
    "enable_slow_task_profiling" : (71, "Enables debugging feature to perform slow task profiling. Requires trace logging to be enabled. WARNING: this feature is not recommended for use in production.", type(None), None),
}

ClusterOption = {

}

DatabaseOption = {
    "location_cache_size" : (10, "Set the size of the client location cache. Raising this value can boost performance in very large databases where clients access data in a near-random pattern. Defaults to 100000.", type(0), "Max location cache entries"),
    "max_watches" : (20, "Set the maximum number of watches allowed to be outstanding on a database connection. Increasing this number could result in increased resource usage. Reducing this number will not cancel any outstanding watches. Defaults to 10000 and cannot be larger than 1000000.", type(0), "Max outstanding watches"),
    "machine_id" : (21, "Specify the machine ID that was passed to fdbserver processes running on the same machine as this client, for better location-aware load balancing.", type(''), "Hexadecimal ID"),
    "datacenter_id" : (22, "Specify the datacenter ID that was passed to fdbserver processes running in the same datacenter as this client, for better location-aware load balancing.", type(''), "Hexadecimal ID"),
}

TransactionOption = {
    "causal_write_risky" : (10, "The transaction, if not self-conflicting, may be committed a second time after commit succeeds, in the event of a fault", type(None), None),
    "causal_read_risky" : (20, "The read version will be committed, and usually will be the latest committed, but might not be the latest committed in the event of a fault or partition", type(None), None),
    "causal_read_disable" : (21, "", type(None), None),
    "next_write_no_write_conflict_range" : (30, "The next write performed on this transaction will not generate a write conflict range. As a result, other transactions which read the key(s) being modified by the next write will not conflict with this transaction. Care needs to be taken when using this option on a transaction that is shared between multiple threads. When setting this option, write conflict ranges will be disabled on the next write operation, regardless of what thread it is on.", type(None), None),
    "commit_on_first_proxy" : (40, "Committing this transaction will bypass the normal load balancing across proxies and go directly to the specifically nominated 'first proxy'.", type(None), None),
    "check_writes_enable" : (50, "", type(None), None),
    "read_your_writes_disable" : (51, "Reads performed by a transaction will not see any prior mutations that occured in that transaction, instead seeing the value which was in the database at the transaction's read version. This option may provide a small performance benefit for the client, but also disables a number of client-side optimizations which are beneficial for transactions which tend to read and write the same keys within a single transaction.", type(None), None),
    "read_ahead_disable" : (52, "Disables read-ahead caching for range reads. Under normal operation, a transaction will read extra rows from the database into cache if range reads are used to page through a series of data one row at a time (i.e. if a range read with a one row limit is followed by another one row range read starting immediately after the result of the first).", type(None), None),
    "durability_datacenter" : (110, "", type(None), None),
    "durability_risky" : (120, "", type(None), None),
    "durability_dev_null_is_web_scale" : (130, "", type(None), None),
    "priority_system_immediate" : (200, "Specifies that this transaction should be treated as highest priority and that lower priority transactions should block behind this one. Use is discouraged outside of low-level tools", type(None), None),
    "priority_batch" : (201, "Specifies that this transaction should be treated as low priority and that default priority transactions should be processed first. Useful for doing batch work simultaneously with latency-sensitive work", type(None), None),
    "initialize_new_database" : (300, "This is a write-only transaction which sets the initial configuration. This option is designed for use by database system tools only.", type(None), None),
    "access_system_keys" : (301, "Allows this transaction to read and modify system keys (those that start with the byte 0xFF)", type(None), None),
    "read_system_keys" : (302, "Allows this transaction to read system keys (those that start with the byte 0xFF)", type(None), None),
    "debug_dump" : (400, "", type(None), None),
    "debug_retry_logging" : (401, "", type(''), "Optional transaction name"),
    "transaction_logging_enable" : (402, "Enables tracing for this transaction and logs results to the client trace logs. Client trace logging must be enabled to get log output.", type(''), "String identifier to be used in the logs when tracing this transaction. The identifier must not exceed 100 characters."),
    "timeout" : (500, "Set a timeout in milliseconds which, when elapsed, will cause the transaction automatically to be cancelled. Valid parameter values are ``[0, INT_MAX]``. If set to 0, will disable all timeouts. All pending and any future uses of the transaction will throw an exception. The transaction can be used again after it is reset. Like all transaction options, a timeout must be reset after a call to onError. This behavior allows the user to make the timeout dynamic.", type(0), "value in milliseconds of timeout"),
    "retry_limit" : (501, "Set a maximum number of retries after which additional calls to onError will throw the most recently seen error code. Valid parameter values are ``[-1, INT_MAX]``. If set to -1, will disable the retry limit. Like all transaction options, the retry limit must be reset after a call to onError. This behavior allows the user to make the retry limit dynamic.", type(0), "number of times to retry"),
    "max_retry_delay" : (502, "Set the maximum amount of backoff delay incurred in the call to onError if the error is retryable. Defaults to 1000 ms. Valid parameter values are ``[0, INT_MAX]``. Like all transaction options, the maximum retry delay must be reset after a call to onError. If the maximum retry delay is less than the current retry delay of the transaction, then the current retry delay will be clamped to the maximum retry delay.", type(0), "value in milliseconds of maximum delay"),
    "snapshot_ryw_enable" : (600, "Snapshot read operations will see the results of writes done in the same transaction.", type(None), None),
    "snapshot_ryw_disable" : (601, "Snapshot read operations will not see the results of writes done in the same transaction.", type(None), None),
    "lock_aware" : (700, "The transaction can read and write to locked databases, and is resposible for checking that it took the lock.", type(None), None),
    "used_during_commit_protection_disable" : (701, "By default, operations that are performed on a transaction while it is being committed will not only fail themselves, but they will attempt to fail other in-flight operations (such as the commit) as well. This behavior is intended to help developers discover situations where operations could be unintentionally executed after the transaction has been reset. Setting this option removes that protection, causing only the offending operation to fail.", type(None), None),
    "read_lock_aware" : (702, "The transaction can read from locked databases.", type(None), None),
}

StreamingMode = {
    "want_all" : (-2, "Client intends to consume the entire range and would like it all transferred as early as possible.", type(None), None),
    "iterator" : (-1, "The default. The client doesn't know how much of the range it is likely to used and wants different performance concerns to be balanced. Only a small portion of data is transferred to the client initially (in order to minimize costs if the client doesn't read the entire range), and as the caller iterates over more items in the range larger batches will be transferred in order to minimize latency.", type(None), None),
    "exact" : (0, "Infrequently used. The client has passed a specific row limit and wants that many rows delivered in a single batch. Because of iterator operation in client drivers make request batches transparent to the user, consider ``WANT_ALL`` StreamingMode instead. A row limit must be specified if this mode is used.", type(None), None),
    "small" : (1, "Infrequently used. Transfer data in batches small enough to not be much more expensive than reading individual rows, to minimize cost if iteration stops early.", type(None), None),
    "medium" : (2, "Infrequently used. Transfer data in batches sized in between small and large.", type(None), None),
    "large" : (3, "Infrequently used. Transfer data in batches large enough to be, in a high-concurrency environment, nearly as efficient as possible. If the client stops iteration early, some disk and network bandwidth may be wasted. The batch size may still be too small to allow a single client to get high throughput from the database, so if that is what you need consider the SERIAL StreamingMode.", type(None), None),
    "serial" : (4, "Transfer data in batches large enough that an individual client can get reasonable read bandwidth from the database. If the client stops iteration early, considerable disk and network bandwidth may be wasted.", type(None), None),
}

MutationType = {
    "add" : (2, "Performs an addition of little-endian integers. If the existing value in the database is not present or shorter than ``param``, it is first extended to the length of ``param`` with zero bytes.  If ``param`` is shorter than the existing value in the database, the existing value is truncated to match the length of ``param``. The integers to be added must be stored in a little-endian representation.  They can be signed in two's complement representation or unsigned. You can add to an integer at a known offset in the value by prepending the appropriate number of zero bytes to ``param`` and padding with zero bytes to match the length of the value. However, this offset technique requires that you know the addition will not cause the integer field within the value to overflow.", type(b''), "addend"),
    "and" : (6, "Deprecated", type(b''), "value with which to perform bitwise and"),
    "bit_and" : (6, "Performs a bitwise ``and`` operation.  If the existing value in the database is not present, then ``param`` is stored in the database. If the existing value in the database is shorter than ``param``, it is first extended to the length of ``param`` with zero bytes.  If ``param`` is shorter than the existing value in the database, the existing value is truncated to match the length of ``param``.", type(b''), "value with which to perform bitwise and"),
    "or" : (7, "Deprecated", type(b''), "value with which to perform bitwise or"),
    "bit_or" : (7, "Performs a bitwise ``or`` operation.  If the existing value in the database is not present or shorter than ``param``, it is first extended to the length of ``param`` with zero bytes.  If ``param`` is shorter than the existing value in the database, the existing value is truncated to match the length of ``param``.", type(b''), "value with which to perform bitwise or"),
    "xor" : (8, "Deprecated", type(b''), "value with which to perform bitwise xor"),
    "bit_xor" : (8, "Performs a bitwise ``xor`` operation.  If the existing value in the database is not present or shorter than ``param``, it is first extended to the length of ``param`` with zero bytes.  If ``param`` is shorter than the existing value in the database, the existing value is truncated to match the length of ``param``.", type(b''), "value with which to perform bitwise xor"),
    "max" : (12, "Performs a little-endian comparison of byte strings. If the existing value in the database is not present or shorter than ``param``, it is first extended to the length of ``param`` with zero bytes.  If ``param`` is shorter than the existing value in the database, the existing value is truncated to match the length of ``param``. The larger of the two values is then stored in the database.", type(b''), "value to check against database value"),
    "min" : (13, "Performs a little-endian comparison of byte strings. If the existing value in the database is not present, then ``param`` is stored in the database. If the existing value in the database is shorter than ``param``, it is first extended to the length of ``param`` with zero bytes.  If ``param`` is shorter than the existing value in the database, the existing value is truncated to match the length of ``param``. The smaller of the two values is then stored in the database.", type(b''), "value to check against database value"),
    "set_versionstamped_key" : (14, "Transforms ``key`` using a versionstamp for the transaction. Sets the transformed key in the database to ``param``. A versionstamp is a 10 byte, unique, monotonically (but not sequentially) increasing value for each committed transaction. The first 8 bytes are the committed version of the database. The last 2 bytes are monotonic in the serialization order for transactions. WARNING: At this time versionstamps are compatible with the Tuple layer only in the Java and Python bindings. Note that this implies versionstamped keys may not be used with the Subspace and Directory layers except in those languages.", type(b''), "value to which to set the transformed key"),
    "set_versionstamped_value" : (15, "Transforms ``param`` using a versionstamp for the transaction. Sets ``key`` in the database to the transformed parameter. A versionstamp is a 10 byte, unique, monotonically (but not sequentially) increasing value for each committed transaction. The first 8 bytes are the committed version of the database. The last 2 bytes are monotonic in the serialization order for transactions. WARNING: At this time versionstamped values are not compatible with the Tuple layer.", type(b''), "value to versionstamp and set"),
    "byte_min" : (16, "Performs lexicographic comparison of byte strings. If the existing value in the database is not present, then ``param`` is stored. Otherwise the smaller of the two values is then stored in the database.", type(b''), "value to check against database value"),
    "byte_max" : (17, "Performs lexicographic comparison of byte strings. If the existing value in the database is not present, then ``param`` is stored. Otherwise the larger of the two values is then stored in the database.", type(b''), "value to check against database value"),
}

ConflictRangeType = {
    "read" : (0, "Used to add a read conflict range", type(None), None),
    "write" : (1, "Used to add a write conflict range", type(None), None),
}

ErrorPredicate = {
    "retryable" : (50000, "Returns ``true`` if the error indicates the operations in the transactions should be retried because of transient error.", type(None), None),
    "maybe_committed" : (50001, "Returns ``true`` if the error indicates the transaction may have succeeded, though not in a way the system can verify.", type(None), None),
    "retryable_not_committed" : (50002, "Returns ``true`` if the error indicates the transaction has not committed, though in a way that can be retried.", type(None), None),
}

