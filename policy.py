"""SAFE-Match: constraint-first, bundle-aware sequential reciprocal allocation.
Only consumes phase request; no hidden simulator data. Python >=3.10.
"""
import argparse
import itertools
import json
import math
import sys
from functools import lru_cache

HARD = ('age_min','age_max','who_to_meet','relationship_structure','smoking','partner_smoking',
        'has_children','partner_children','wants_children','acceptable_zones','schedule')
SOFT = ('relationship_goal','relationship_pace','lifestyle','conversations',
        'emotional_availability','space_for_relationship','relocate')
WEIGHTS = {'relationship_goal':0.7,'relationship_pace':0.4,'lifestyle':0.25,'conversations':0.2,
           'emotional_availability':0.12,'space_for_relationship':0.10,'relocate':0.06}


def hard_status(a,b):
    """Replicate reference kit's feasibility semantics, using public observations only."""
    if a['member_id']==b['member_id'] or a['pool_id']!=b['pool_id'] or min(a['age'],b['age'])<18:
        return 'infeasible'
    fa,fb=a['fields'],b['fields']
    for x,y,fx,fy in ((a,b,fa,fb),(b,a,fb,fa)):
        if fx.get('who_to_meet') is not None and y['gender'] not in fx['who_to_meet']: return 'infeasible'
        if fx.get('age_min') is not None and y['age']<fx['age_min']: return 'infeasible'
        if fx.get('age_max') is not None and y['age']>fx['age_max']: return 'infeasible'
        if fx.get('acceptable_zones') is not None and y['zone'] not in fx['acceptable_zones']: return 'infeasible'
        if fx.get('partner_smoking')=='no_smoking' and fy.get('smoking') in ('yes','occasionally'): return 'infeasible'
        if fx.get('partner_children')=='no_children' and fy.get('has_children') is True: return 'infeasible'
    if fa.get('relationship_structure') is not None and fb.get('relationship_structure') is not None and fa['relationship_structure'] != fb['relationship_structure']: return 'infeasible'
    if {fa.get('wants_children'),fb.get('wants_children')} == {'yes','no'}: return 'infeasible'
    if fa.get('schedule') is not None and fb.get('schedule') is not None and not set(fa['schedule']).intersection(fb['schedule']): return 'infeasible'
    if any(f.get(k) is None for f in (fa,fb) for k in HARD): return 'needs_clarification'
    return 'feasible'


def edge_score(a,b):
    """Fixed surrogate, not a calibrated MSMI probability."""
    s=1.0
    for k,w in WEIGHTS.items():
        x,y=a['fields'].get(k),b['fields'].get(k)
        if x is not None and y is not None: s+=w*(1 if x==y else -.5)
    return max(0.01,s)


def _exact_small_graph(edges):
    """Dependency-free exact weighted general matching for at most 16 vertices."""
    vertices = sorted({v for a, b, w in edges if w > 0 for v in (a, b)})
    indices = {v: i for i, v in enumerate(vertices)}
    adjacency = [[] for _ in vertices]
    for a, b, weight in edges:
        if a == b or weight <= 0:
            continue
        i, j = indices[a], indices[b]
        adjacency[i].append((j, float(weight)))
        adjacency[j].append((i, float(weight)))

    @lru_cache(maxsize=None)
    def best(mask):
        if not mask:
            return (0.0, ())
        bit = mask & -mask
        i = bit.bit_length() - 1
        remain = mask ^ bit
        result = best(remain)  # vertex i can remain unmatched
        for j, w in adjacency[i]:
            if remain & (1 << j):
                val, matching = best(remain ^ (1 << j))
                cand = (w + val, ((vertices[i], vertices[j]),) + matching)
                if cand[0] > result[0] + 1e-12:
                    result = cand
        return result
    return sorted(tuple(sorted(p)) for p in best((1 << len(vertices)) - 1)[1])


def greedy_augmented(edges):
    """Deterministic locally improving fallback. Supports 1->2 and 2->2 swaps.

    All moves strictly increase total positive edge weight, preserving disjointness.
    Not an exact solver; the exact Blossom implementation remains preferred.
    """
    if len({v for a,b,w in edges if w > 0 for v in (a,b)}) <= 16:
        return _exact_small_graph(edges)
    ordered = sorted((tuple(sorted((a,b)))+(float(w),) for a,b,w in edges if w > 0),
                     key=lambda e:(-e[2],e[0],e[1]))
    chosen = {}
    occupied = set()
    for a,b,w in ordered:
        if a not in occupied and b not in occupied:
            chosen[(a,b)] = w
            occupied.update((a,b))
    weight = {(a,b):w for a,b,w in ordered}
    adj = {}
    for (a,b),w in weight.items():
        adj.setdefault(a,[]).append((b,w))
        adj.setdefault(b,[]).append((a,w))
    # Strictly improving local augmentations are bounded for predictable runtime.
    for _ in range(4):
        improved=False
        occupied={v for pair in chosen for v in pair}
        for (a,b),old in sorted(chosen.items()):
            ca=sorted(((c,w) for c,w in adj.get(a,[]) if c not in occupied), key=lambda z:-z[1])[:25]
            cb=sorted(((d,w) for d,w in adj.get(b,[]) if d not in occupied), key=lambda z:-z[1])[:25]
            candidates=[(wa+wb,c,d) for c,wa in ca for d,wb in cb if c!=d and wa+wb>old+1e-9]
            if candidates:
                _,c,d=max(candidates)
                del chosen[(a,b)]
                chosen[tuple(sorted((a,c)))]=weight[tuple(sorted((a,c)))]
                chosen[tuple(sorted((b,d)))]=weight[tuple(sorted((b,d)))]
                improved=True
                break
        if improved: continue
        for (a,b),w1 in sorted(chosen.items()):
            for (c,d),w2 in sorted(chosen.items()):
                if (a,b)>=(c,d):continue
                swaps=(((a,c),(b,d)),((a,d),(b,c)))
                for new_pairs in swaps:
                    ks=[tuple(sorted(pair)) for pair in new_pairs]
                    if all(k in weight for k in ks) and sum(weight[k] for k in ks)>w1+w2+1e-9:
                        del chosen[(a,b)];del chosen[(c,d)]
                        for k in ks:chosen[k]=weight[k]
                        improved=True;break
                if improved:break
            if improved:break
        if not improved:break
    return sorted(chosen)


def allocate(state, use_exact=True):
    members=[m for m in state.get('members',[]) if m.get('available')]
    past={tuple(sorted((r['user_a'],r['user_b']))) for r in state.get('introductions',[])}
    edges=[]
    for a,b in itertools.combinations(members,2):
        key=tuple(sorted((a['member_id'],b['member_id'])))
        if key not in past and hard_status(a,b)=='feasible':edges.append((key[0],key[1],edge_score(a,b)))
    pairs=[]
    if use_exact and edges:
        try:
            import networkx as nx
            graph=nx.Graph();graph.add_weighted_edges_from(edges)
            pairs=[tuple(sorted(p)) for p in nx.algorithms.matching.max_weight_matching(graph, maxcardinality=False,weight='weight')]
        except Exception:
            # Any solver/dependency failure degrades to a legal local matcher
            # instead of discarding an otherwise feasible batch.
            pairs=greedy_augmented(edges)
    else:
        pairs=greedy_augmented(edges)
    ids={m['member_id']:m for m in members};used=set();out=[]
    for a,b in sorted(pairs):
        if a not in used and b not in used and a in ids and b in ids and (a,b) not in past and hard_status(ids[a],ids[b])=='feasible':
            out.append([a,b]);used.update((a,b))
    return out


def ask_policy(state, mode='bundle'):
    """Budget-safe, shortlist-based complementarity heuristic, NOT a formal VOI estimator.

    Constraint asks can be issued for both sides of a plausible edge, avoiding
    the zero-single-step gain problem. Known infeasibility and past matches block
    candidate edges. Soft questions are used only after hard questions, and only
    on already hard-feasible candidates. No declined field is re-asked.
    """
    budget=max(0,min(12,int(state.get('ask_budget_remaining',0))))
    members=[m for m in state.get('members',[]) if m.get('available')]
    past={tuple(sorted((x.get('user_a'),x.get('user_b')))) for x in state.get('introductions',[])}
    previous={(x.get('member_id'),x.get('field')) for x in state.get('ask_log',[])}
    pending={m['member_id']:m for m in members
             if (m['member_id'],'constraints') not in previous
             and any(m['fields'].get(k) is None for k in HARD)
             and not any(m.get('field_status',{}).get(k)=='declined' for k in HARD)}
    adjacency={mid:0.0 for mid in pending}
    feasible_adjacency={m['member_id']:set() for m in members}
    pair_candidates=[]
    soft_interest={}
    for a,b in itertools.combinations(members,2):
        i,j=a['member_id'],b['member_id']
        if tuple(sorted((i,j))) in past:continue
        status=hard_status(a,b)
        if status=='infeasible':continue
        if status=='needs_clarification':
            # Ignore edges whose remaining unknown fields can never be revealed.
            if ((any(a['fields'].get(k) is None for k in HARD) and i not in pending)
                or (any(b['fields'].get(k) is None for k in HARD) and j not in pending)):
                continue
        else:
            feasible_adjacency[i].add(j); feasible_adjacency[j].add(i)
        ia=i in pending; ib=j in pending
        value=edge_score(a,b)
        if ia:adjacency[i]+=value
        if ib:adjacency[j]+=value
        if ia and ib:pair_candidates.append((value,i,j))
        if status=='feasible':
            for m in (a,b):
                mid=m['member_id']
                for field,weight in WEIGHTS.items():
                    if (mid,field) not in previous and m['fields'].get(field) is None and m.get('field_status',{}).get(field)!='declined':
                        soft_interest[(mid,field)]=soft_interest.get((mid,field),0.0)+weight*value
    selected=[];chosen=set()
    if mode=='bundle':
        # Allocate joint queries only where both endpoints really need clarification.
        for value,i,j in sorted(pair_candidates,key=lambda x:(-x[0],x[1],x[2])):
            if budget<6:break
            if i not in chosen and j not in chosen:
                selected.extend([{'member_id':i,'field':'constraints'},{'member_id':j,'field':'constraints'}])
                chosen.update((i,j)); budget-=6
    for mid in sorted(pending,key=lambda m:(-adjacency[m],m)):
        if budget<3:break
        if mid not in chosen and adjacency[mid]>0:
            selected.append({'member_id':mid,'field':'constraints'})
            chosen.add(mid); budget-=3
    # Soft fields are less actionable than feasibility: only spend remaining units.
    for (mid,field),value in sorted(soft_interest.items(),key=lambda item:(-item[1],item[0])):
        if budget<=0:break
        if value<=0:continue
        neighbors=feasible_adjacency[mid]
        # If there is only one isolated feasible pair, the answer cannot change allocation.
        if len(neighbors)<2 and not any(len(feasible_adjacency[j])>=2 for j in neighbors):continue
        selected.append({'member_id':mid,'field':field})
        budget-=1
    # Marginal soft clarification has fewer remaining allocation rounds late in
    # the episode. Keep feasibility questions, but stop spending on soft fields.
    # Threshold was selected on public validation seeds only; independently audit it.
    if state.get('day', 0) >= 40:
        selected = [request for request in selected if request['field'] == 'constraints']
    # Uninformative soft fields do not enter the public MSMI outcome model.
    # Filter after the original selection so candidate hard questions and
    # decisions remain unchanged; unused budget is preferable to speculative asks.
    return [question for question in selected if question['field'] in
            ('constraints','relationship_goal','relationship_pace','lifestyle','conversations')]


def decide(request,mode='safe'):
    state=request.get('state') or {};memory=request.get('memory')
    if request.get('phase')=='ask':
        return {'asks':ask_policy(state,'single' if mode=='single' else 'bundle'), 'memory':memory}
    if request.get('phase')=='match':
        return {'pairs':allocate(state,use_exact=mode!='augmented'),'memory':memory}
    raise ValueError('Unknown phase')


def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',default='safe');args=p.parse_args()
    try:
        request=json.load(sys.stdin)
        response=decide(request,args.baseline)
    except Exception as error:
        print('SAFE-Match safe fallback: '+str(error)[:500],file=sys.stderr)
        phase=request.get('phase','match') if 'request' in locals() and isinstance(request,dict) else 'match'
        # Keep valid carried memory even on an unexpected safe-empty fallback.
        # Losing it can alter future decisions after a recoverable request error.
        carry=request.get('memory') if 'request' in locals() and isinstance(request,dict) else None
        try:
            encoded=json.dumps(carry,allow_nan=False,separators=(',',':')).encode('utf-8')
            if len(encoded)>1024*1024: carry=None
        except (TypeError,ValueError,OverflowError):
            carry=None
        response={'asks':[],'memory':carry} if phase=='ask' else {'pairs':[],'memory':carry}
    print(json.dumps(response,allow_nan=False,separators=(',',':')))
if __name__=='__main__':main()
