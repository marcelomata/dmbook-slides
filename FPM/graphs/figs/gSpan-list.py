#!/usr/bin/env python

import sys
import networkx as nx

def read_graphs(fname):
    #read graphs
    f = open(fname, "rU")
    D = {}
    for l in f.readlines():
        a = l.strip().split()
        if a[0] == 't': #graph id 
            gid = int(a[2])
            G = nx.Graph(gid=gid)
            D[gid] = G
        elif a[0] == 'v': #vertices
            vid = int(a[1])
            vlbl = a[2]
            G.add_node(vid, L=vlbl)
        elif a[0] == 'e': #edges
            vi = int(a[1])
            vj = int(a[2])
            elbl = 'e'
            if len(a) > 3: 
                elbl = a[3]
            G.add_edge(vi, vj, L=elbl)
    
    #for G in D:
    #    print G.graph['gid']
    #   print G.nodes(), G.nodes(data=True)
    #    print G.edges()
    return D

def edgecompare((vi, vj), (vx, vy)):
    fij = True
    fxy = True
    if vi > vj: fij = False
    if vx > vy: fxy = False

    if fij and fxy: #both are forward
        ff = cmp(vj, vy)
        if ff == 0: ff = cmp(vx,vi)
        return ff
    elif not fij and not fxy: #both are backward
        bb = cmp(vi, vx)
        if bb == 0: bb = cmp(vj,vy)
        return bb
    elif fij and not fxy: #forward, backward
        fb = 1
        if vj <= vx: fb = -1
        return fb
    else: #backward, forward
        bf = 1
        if vi < vy: bf = -1
        return bf

def dfscompare((vi, vj, li, lj, eij), (vx, vy, lx, ly, exy)):
    #print vi, vj, li, lj, vx, vy, lx, ly
    ecmp = edgecompare((vi,vj), (vx,vy))
    if ecmp == 0: #compare labels
        return cmp((li, lj, eij), (lx, ly, exy))
    else:
        return ecmp


#return the nodes on the rightmost path
def get_rmp(C): 
    rp = [0] #nodes on the rightmost path
    rc = 0 #rightmost child (last element of rp)
    if len(C) > 0:
        for t in C:
            (vi, vj, li, lj, eij) = t
            if vj > vi:
                v = rp.pop()
                while(v != vi):
                    v = rp.pop()
                rp.append(vi)
                rp.append(vj)
        rc = rp[-1]

    return (rp, rc)


def subgraph_isomorphisms2(C, G, ISO):
    (vi, vj, li, lj, eij) = C[0] #first tuple
    L = nx.get_node_attributes(G,'L')
    #find nodes with label li
    M = [[x] for x in L if L[x]==li] 
    #print "lset", gid, L, M

    #process remaining tuples
    for (vi, vj, li, lj, eij) in C:
        #print "now do", vi, vj, li, lj
        new_M = []
        for f in M:
            fv = f[vi]
            if vj > vi:#forward extensions
                valid = [x for x in G.neighbors(fv)
                            if x not in f and
                               G.node[x]['L'] == lj and
                               G.edge[fv][x]['L'] == eij]
                for x in valid:
                    new_f = list(f)
                    new_f.append(x)
                    new_M.append(new_f)
            else: #backward extension
                fx = f[vj]
                if fx in G.neighbors(fv):
                    new_M.append(f)
        #update the isomporphisms
        M = new_M

    return M

def subgraph_isomorphisms(C, DB, ISO):
    M = {}
    if len(C) == 0: 
        for gid in DB: M[gid] = []
    elif len(C) == 1:
        (vi, vj, li, lj, eij) = C[0] #first tuple
        for gid in DB:
            G = DB[gid]
            L = nx.get_node_attributes(G,'L')
            #find nodes with label li
            M[gid] = [[x] for x in L if L[x]==li] 
            #print "lset", gid, L, M
    else:
        M = ISO
    #process last tuples
    #print "CC", C
    #print ISO
    #print "now do", C[-1]

    if len(C) > 0:
        new_M = {}
        for gid in M:
            (vi, vj, li, lj, eij) = C[-1]
            G = DB[gid]
            for f in M[gid]:
                fv = f[vi]
                if vj > vi:#forward extensions
                    valid = [x for x in G.neighbors(fv)
                                if x not in f and
                                   G.node[x]['L'] == lj and
                                   G.edge[fv][x]['L'] == eij]
                    for x in valid:
                        new_f = list(f)
                        new_f.append(x)
                        if gid not in new_M: new_M[gid] = []
                        new_M[gid].append(new_f)
                else: #backward extension
                    fx = f[vj]
                    if fx in G.neighbors(fv):
                        if gid not in new_M: new_M[gid] = []
                        new_M[gid].append(f)
        M = new_M

    return M



# return set of rightmost path extensions
def rmpe(C, DB, ISO):
    #print "rmpe", C,
    rmp, rmc = get_rmp(C)
    #print rmp, rmc
    E = {}
    M = subgraph_isomorphisms(C, DB, ISO)
    #print "isox", M
    for gid in M:
        G = DB[gid]
        if len(C) > 0: #candidate is not empty
            #get all isomorphisms
            nM = M[gid]
     
            #get all extensions
            for f in nM:
                iso = [(v,f[v]) for v in rmp]
                iso.reverse() #process from rmc to the root
                #print "M", f, iso
                
                #backward extension
                vf = {}
                for v in rmp: 
                    vf[f[v]] = v #inverse iso from rmp
                (v, fv) = iso[0] #rmc mapping
                for x in G.neighbors(fv):
                    if x in vf:
                        e = (v,vf[x],G.node[fv]['L'], G.node[x]['L'],\
                             G.edge[fv][x]['L'])
                        be = (vf[x], v, G.node[x]['L'], G.node[fv]['L'],\
                              G.edge[x][fv]['L'])
                        if e not in C and be not in C:
                            if e not in E: E[e] = {}
                            E[e][gid] = True
                            #print "added back", fv, x, e

                #forward extensions
                for v, fv in iso:
                    #print v, fv
                    for x in G.neighbors(fv):
                        if x not in f:
                            e = (v, rmc+1, G.node[fv]['L'], G.node[x]['L'],\
                                 G.edge[fv][x]['L'])
                            if e not in E: E[e] = {}
                            E[e][gid] = True
                            #print "added for", fv, x, e
        else: #candidate is empty
            #add all edges in G into E
            for (u,v) in G.edges():
                e = (0,1,G.node[u]['L'], G.node[v]['L'],
                    G.edge[u][v]['L'])
                if e not in E: E[e] = {}
                E[e][gid] = True
                #reverse the nodes
                if G.node[v]['L'] != G.node[u]['L']:
                    e = (0,1,G.node[v]['L'], G.node[u]['L'],
                        G.edge[v][u]['L'])
                    if e not in E: E[e] = {}
                    E[e][gid] = True
               
    Eset = []
    for e in sorted(E, cmp=dfscompare):
        s = len(E[e])
        Eset.append((e, s))

    return Eset, M

#convert dfscode into graph
def make_graph(C):
    G = nx.Graph(gid=0)
    for (vi, vj, li, lj, eij) in C:
        G.add_node(vi, L=li)
        G.add_node(vj, L=lj)
        G.add_edge(vi, vj, L=eij)
    return G
        

def iscanonical(C):
    G = make_graph(C)
    #print "\niscan", C
    #print G.graph, G.edges(), G.nodes()
    DB = {0: G}
    nC = []
    M = {}
    for i in range(len(C)):
        #print "\tcann", nC,
        E, M = rmpe(nC, DB, M)
        #print E
        e,s = E[0] #look at the least extension
        #print "compare", e, i, C[i]
        if dfscompare(e,C[i]) == -1:
            return False
        nC.append(e)

    return True

def gspan(C, DB, ISO):
    gspan.cnt += 1 #static graph counter
    print gspan.cnt, C
    #print "isoA", ISO
    E, M = rmpe(C,DB,ISO) #rightmost path extensions and their supports
    #print "ext", E
    #print "iso", M
    for (e, s) in E:
        nC = list(C)
        nC.append(e)
        #print "\tcandidate", s, iscanonical(nC), nC
        if s >= minsup and iscanonical(nC):
            gspan(nC, DB, M)

######## main #########
fname = sys.argv[1] #graph filename
minsup = int(sys.argv[2]) #absolute min sup 

DB = read_graphs(fname)

gspan.cnt = 0
gspan([], DB, {})
