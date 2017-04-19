
class Q(object):
    '''
    Some goals are:
     * low space usage relative to queue length, even when length varies dramatically over time
     * cheap garbage collection

    Realistically, I expect this to be slower than a bare metal implementation (although I haven't
    tested with PyPy).  The point here is to build a prototype for understanding.

    Imagine that these arrays are pre-allocated contiguous blocks of memory that you could access
    with pointer math for the fastest bare-metal equivalent.
    '''
    def __init__(self, queue_chunk_size=10000):
        '''
        This queue stores items in a variable list of arrays, each with a maximum length of
        queue_chunk_size. A C implementation might preallocate each element with queue_chunk_size
        elements. The user of the Queue might want to configure the tradeoff between allocated memory
        for small queues and allocation churn for long queues. This is an implementation abstraction
        violation, and should only be tweaked if performance is critical.

        @param queue_chunk_size is the maximum length of internal contiguous arrays
        '''
        self.queue_chunk_size = queue_chunk_size
        self.arrays = [[], []]
        self.qid = 0
        self.dqid = 1
        self.dqidx = 0
        self.__len = 0

    def q(self, val):
        q_array = self._resize_before_queue()
        self.arrays[self.qid].append(val)
        self.__len += 1

    def dq(self):
        val = self.peek() #peek must raise exception if length < 1
        self.__len -= 1
        if self.dqidx == len(self.arrays[self.dqid]):
            self.arrays[self.dqid] = []
            self.dqid = self._next_chunk_id(self.dqid)
            if self.dqid == self.qid:
                # oops, we caught up to the queue, prematurely bump the queue to simplify GC
                self.qid = self._next_chunk_id(self.qid)
            self.dqidx = 1 #set for the *next* dequeue
        else:
            self.dqidx += 1
        return val

    def peek(self):
        if not self.__len:
            raise Exception('confirm queue length before trying to peek or dequeue, current length is 0')
        if self.dqidx == len(self.arrays[self.dqid]):
            next_dqid = self._next_chunk_id(self.dqid)
            return self.arrays[next_dqid][0]
        return self.arrays[self.dqid][self.dqidx]

    def _resize_before_queue(self):
        # check if the current queue chunk will get too big
        if len(self.arrays[self.qid]) >= self.queue_chunk_size:
            # if so, move to the next chunk
            self.qid = self._next_chunk_id(self.qid)
            if self.qid == self.dqid:
                # oops, we caught up to the dequeue chunk
                if self.dqid == 0:
                    # if we wrapped around, append a new chunk
                    self.arrays.append([])
                    self.qid = len(self.arrays) - 1
                else:
                    # splice in a new chunk
                    self.arrays[self.qid:self.qid] = [[]]
                    self.dqid += 1
        return self.arrays[self.qid]

    def _next_chunk_id(self, current_chunk_id):
        return (current_chunk_id + 1) % len(self.arrays)

    def __len__(self):
        return self.__len

    def __nonzero__(self):
        return self.__len

def test():
    q = Q(queue_chunk_size=3)

    #basic add/remove repeated
    for _ in range(5):
        assert len(q) == 0
        q.q(1)
        assert q.peek() == 1
        assert q.peek() == 1
        assert len(q) == 1
        assert q.dq() == 1
        assert len(q) == 0

    #check two in a row
    for i in range(2):
        q.q(i)

    assert len(q) == 2
    assert q.dq() == 0
    assert q.dq() == 1

    #try longer sequences
    for i in range(10):
        q.q(i)

    for i in range(103):
        q.dq()
        q.q(i)
    last_insert = i

    while q:
        last_dq = q.dq()
    assert last_insert == last_dq, "%s found instead of %s" % (last_dq, last_insert)

    #this one's just to play with in the console
    for i in range(10):
        q.q(i)

    for i in range(103):
        q.dq()
        q.q(i)

    return q

if __name__ == '__main__':
    q = test()
