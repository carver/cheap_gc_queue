Playing around with implementing a Queue
=========

Some goals are:
 * low space usage relative to queue length, even when length varies dramatically over time
 * cheap garbage collection

Realistically, I expect this to be slower than a bare metal implementation (although I haven't tested with PyPy).  The point here is to build a prototype for understanding.

Imagine that the internal chunks are pre-allocated contiguous blocks of memory that you could access with pointer math for the fastest bare-metal equivalent.

Testing
=====

lazy test: `python -i cheap_gc_queue.py`

If it doesn't throw, then the tests passed.
