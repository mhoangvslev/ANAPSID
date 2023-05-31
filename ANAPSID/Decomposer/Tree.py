
import math
import heapq
import string
import abc

class Tree(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def instantiate(self, d):
        return

    @abc.abstractmethod
    def instantiateFilter(self, d, filter_str):
        return

    def degree(self):
        return getDegree(self.vars, self.dict)

    def __leq__ (self, other):
        return (self.size < other.size or (self.size == other.size 
                                           and self.degree() <= other.degree()))

    def __lt__ (self, other):
        return (self.size < other.size or (self.size == other.size 
                                           and self.degree() < other.degree()))

    @abc.abstractmethod
    def __eq__(self, other):
        return

    @abc.abstractmethod
    def __hash__(self):
        return

    def __ne__(self, other):
        return not self == other

    @abc.abstractmethod
    def __repr__(self):
        return

    @abc.abstractmethod
    def aux(self, n):
        return

    @abc.abstractmethod
    def aux2(self, n):
        return

    def show(self, n):
        return self.aux(n)

    def show2(self, n):
        return self.aux2(n)

    @abc.abstractmethod
    def getVars(self):
        return

    @abc.abstractmethod
    def places(self):
        return

    @abc.abstractmethod
    def constantNumber(self):
        return

    def constantPercentage(self):
        return self.constantNumber()/self.places()

class Node(Tree):

    def __init__(self, l, r, filters=[]):
        self.left = l
        self.right = r
        self.vars = unify(l.vars, r.vars, l.dict)
        self.dict = l.dict = r.dict
        self.size = l.size + r.size
        self.filters = filters

    def instantiate(self, d):
        return Node(self.left.instantiate(d), self.right.instantiate(d))

    def instantiateFilter(self, d, filter_str):
        return Node(self.left.instantiateFilter(d, filter_str), self.right.instantiateFilter(d, filter_str))

    def __eq__(self, other):
        return ((isinstance(other, Node)) and (self.vars == other.vars) and 
                (self.dict == other.dict) and (self.degree() == other.degree()) and 
                (self.size == other.size) and (self.left == other.left) and
                (self.right == other.right))

    def __hash__(self):
        return hash((self.vars, self.dict, self.size, self.degree(),
                     self.left, self.right))

    def __repr__(self):
        return self.aux(" ")

    def aux(self, n):
        s = ""
        if self.left:
            s = s + n + "{\n" + self.left.aux(n+"  ") + "\n" + n + "}\n" + n + "  . \n"
            
        if self.right:
            s = s + n + "{\n" + self.right.aux(n+"  ") + "\n"+ n+"}"
        return s

    def show(self, n):
        return self.aux(n)

    def show2(self, n):
        return self.aux2(n)

    def aux2(self, n):
        s = ""
        if self.left:
            s = s + n + "{\n" + self.left.aux2(n+"  ") + "\n" + n + "}\n" + n + "  UNION \n"
            
        if self.right:
            s = s + n + "{\n" + self.right.aux2(n+"  ") + "\n"+ n+"}"
        return s

    def places(self):
        return self.left.places() + self.right.places()

    def constantNumber(self):
        return self.left.constantNumber() + self.right.constantNumber()

    def getVars(self):
        vs = []
        if self.left:
            vs = vs +self.left.getVars()
        if self.right:
            vs = vs +self.right.getVars()
        return vs

def unify (vars0, vars1, dict0):

    vars2 = set(vars0)
    for v in vars1:
       if v in vars2:
           dict0[v] = dict0[v] - 1
           if v in dict0 and dict0[v] == 0:
              del dict0[v]
              vars2.remove(v)
       else:
           vars2.add(v)
    return vars2

def getDegree(vars0, dict0):

    s = 0
    for v in vars0:
        s = s + dict0[v]
    return s

class Leaf(Tree):
    def __init__(self, s, vs, dc, filter=[]):
        self.vars = vs
        self.dict = dc
        self.size = 1
        self.service = s
        self.filters=[]
        serviceVars= s.getVars()
        for f in filter:
          vars_f = f.getVars()
          if set(serviceVars) & set(vars_f) == set(vars_f):
             self.filters.append(f)

    def __hash__(self):
        return hash((self.vars, self.dict, self.size, self.degree(), 
                     self.service))

    def __repr__(self):
        return str(self.service)

    def __eq__(self, other):
        return ((isinstance(other, Leaf)) and (self.vars == other.vars) and 
                (self.dict == other.dict) and (self.degree() == other.degree()) and 
                (self.service == other.service))

    def instantiate(self, d):
        newvars = self.vars - set(d.keys())
        newdict = self.dict.copy()
        for c in d:
            if c in newdict:
                del newdict[c]
        return Leaf(self.service.instantiate(d), newvars, newdict)

    def instantiateFilter(self, d, filter_str):
        newvars = self.vars - set(d)
        newdict = self.dict.copy()
        for c in d:
            if c in newdict:
                del newdict[c]
        return Leaf(self.service.instantiateFilter(d, filter_str), newvars, newdict)

    
    def aux(self, n):
        return self.service.show(n)

    def aux2(self, n):
        return self.service.show2(n)

    def show(self, n):
        return self.aux(n)

    def show2(self, n):
        return self.aux2(n)

    def getInfoIO(self, query):
        subquery = self.service.getTriples()
        vars_order_by=[x for v in query.order_by for x in v.getVars() ]
        vs = list(set(self.service.getVars()))# - set(self.service.filters_vars)) # Modified this by mac: 31-01-2014
        #print "service", vs, self.service.filters_vars
        predictVar=set(self.service.getPredVars())
        variables = [str.lstrip(str.lstrip(v, "?"), "$") for v in vs]
        if query.args == []:
            projvars = vs
        else:
            projvars = list(set([v.name for v in query.args if not v.constant]))
        subvars = list((query.join_vars | set(projvars)) & set(vs) )
        if subvars == []:
          subvars=vs
        subvars = list(set(subvars) | predictVar | set(vars_order_by))
        # This corresponds to the case when the subquery is the same as the original query.
        # In this case, we project the variables of the original query.
        if query.body.show(" ").count("SERVICE") == 1:
          subvars = list(set(projvars) | set(vars_order_by)) 
        
        #subvars = str.joinfields(subvars, " ")
        subvars = " ".join(subvars)
        #MEV distinct pushed down to the sources
        if query.distinct:
            d = "DISTINCT "
        else:
            d = ""
        
        subquery = "SELECT "+d+ subvars + " WHERE {" + subquery + "\n" + query.filter_nested + "\n}"
        return (self.service.endpoint, query.getPrefixes()+subquery, set(variables))

    def getCount(self, query, vars, endpointType):
        subquery = self.service.getTriples()
        if len(vars) == 0:
            vs = self.service.getVars()
            variables = [str.lstrip(str.lstrip(v, "?"), "$") for v in vs]
            vars_str = "*"
        else:
            variables = vars
            service_vars = self.service.getVars()
            vars2 = []
            for v1 in vars:
                for v2 in service_vars:
                    if (v1 == v2[1:]):
                        vars2.append(v2)
                        break
            if len(vars2) > 0:
                #vars_str = str.joinfields(vars2, " ")
                vars_str = " ".join(vars2)
            else:
                vars_str = "*"

        d = "DISTINCT "
        if (endpointType=="V"):
             subquery = "SELECT COUNT "+d+ vars_str + "  WHERE {" + subquery + "\n"+ query.filter_nested +"}"
        else:
            subquery = "SELECT ( COUNT ("+d+ vars_str + ") AS ?cnt)  WHERE {" + subquery +"\n"+ query.filter_nested + "}"
        return (self.service.endpoint, query.getPrefixes()+subquery)

    def getVars(self):
        return self.service.getVars()

    def places(self):
        return self.service.places()

    def constantNumber(self):
        return self.service.constantNumber()

def sort(lss):

    lo = []
    while not(lss == []):
        m = 0
        for i in range(len(lss)):
            if lss[i].constantPercentage() > lss[m].constantPercentage():
                m = i
        lo.append(lss[m])
        lss.pop(m)
    return lo

def createLeafs(lss,filters=[]):

    d = dict()
    for s in lss:
        l = s.getVars()
        l = set(l)
        for e in l:
            d[e] = d.get(e, 0) + 1
    el = []
    for e in d:
        d[e] = d[e] - 1
        if d[e] <= 0:
            el.append(e)
    for e in el:
        del d[e]
    ls = []
    lo = sort(lss)

    for s in lo:
        e = set()
        l = s.getVars()
        for v in l:
            if v in d:
                e.add(v)
        ls.append(Leaf(s, e, d,filters))

    return (d, ls)

def shareAtLeastOneVar(l, r):

    return len(l.vars & r.vars) > 0

def sortedInclude(l, e):

    for i in range(0, len(l)):
        if e < l[i]:
            l.insert(i, e)
            return
    l.insert(len(l), e)

def updateFilters(node,filters):
    if isinstance(node,Leaf):
      return  Leaf(node.service,node.vars,node.dict,node.filters+filters)
    elif isinstance(node,Node):
      return Node(node.left,node.right,node.filters+filters)  
      
def makeNode(l, r,filters=[]):
    if l.constantPercentage() > r.constantPercentage():
        n = Node(l, r, filters)
    else:
        n = Node(r, l, filters)
    return n

def makeBushyTree(ss,filters=[]):
    (d, pq) = createLeafs(ss,filters)
    heapq.heapify(pq)
    others = []
    while len(pq) > 1:
        done = False
        l = heapq.heappop(pq)

        lpq = heapq.nsmallest(len(pq), pq)

        for i in range(0, len(pq)):
            r = lpq[i]

            if shareAtLeastOneVar(l,r):
                pq.remove(r)
                n = makeNode(l, r,filters)
                heapq.heappush(pq, n)
                done = True
                break
        if not done: 
            others.append(l)

    if len(pq) == 1:
          for e in others:
            pq[0] = makeNode(pq[0], e,filters)
          return pq[0]
    elif others:
        while len(others) > 1:
            l = others.pop(0)
            r = others.pop(0)

            n = Node(l, r,filters)
            others.append(n)
        if others:
            return others[0]
        return None

def makeNaiveTree(ss,filters=[]):
    (_, pq) = createLeafs(ss)
    while len(pq) > 1:
        l = pq.pop(0)
        r = pq.pop(0)

        n = makeNode(l, r,filters)
        pq.append(n)

    if len(pq) == 1:
        return pq[0]
    else:
        return None

def makeLLTree(ss,filters=[]):

    (_, pq) = createLeafs(ss)
    while len(pq) > 1:
        l = pq.pop(0)
        r = pq.pop(0)

        n = makeNode(l, r,filters)
        pq.insert(0, n)

    if len(pq) == 1:
        return pq[0]
    else:
        return None

