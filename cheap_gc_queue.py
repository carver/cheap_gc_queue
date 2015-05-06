
class Q(object):
    '''
    Some goals are:
     * low space usage relative to queue length, even when length varies dramatically over time
     * cheap garbage collection

    Realistically, I expect this to be slower than a bare metal implementation (although I haven't
    tested with PyPy).  The point here is to build a prototype for understanding.
    '''
    def __init__(self):
        self.arrays = [[], []]
        self.qid = 0
        self.dqid = 1
        self.dqidx = 0
        self.len = 0

    def q(self, val):
        self.arrays[self.qid].append(val)
        self.len += 1

    def dq(self):
        val = self.peek() #peek must raise exception if length < 1
        self.len -= 1
        if self.dqidx == len(self.arrays[self.dqid]):
            self.arrays[self.dqid] = []
            self.qid ^= 1 #bit flip
            self.dqid ^= 1 #bit flip
            self.dqidx = 1 #set for the *next* dequeue
        else:
            self.dqidx += 1
        return val

    def peek(self):
        if not self.len:
            raise Exception('confirm queue length before trying to peek or dequeue, current length is 0')
        if self.dqidx == len(self.arrays[self.dqid]):
            return self.arrays[self.qid][0]
        return self.arrays[self.dqid][self.dqidx]

def test():
    q = Q()

    #basic add/remove repeated
    for _ in range(5):
        assert q.len == 0
        q.q(1)
        assert q.peek() == 1
        assert q.peek() == 1
        assert q.len == 1
        assert q.dq() == 1
        assert q.len == 0

    #check two in a row
    for i in range(2):
        q.q(i)

    assert q.len == 2
    assert q.dq() == 0
    assert q.dq() == 1

    #try longer sequences
    for i in range(10):
        q.q(i)

    for i in range(103):
        q.dq()
        q.q(i)
    last_insert = i

    while q.len:
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
