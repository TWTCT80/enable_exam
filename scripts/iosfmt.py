"""Shared IOS output renderers for exhibit generation.

Column rules verified against IOS 15.x `show ip route`:
  * top-level entry  -> code left-justified in a 6-wide field, prefix at col 7
  * child of a parent-> code left-justified in a 9-wide field, prefix at col 10
  * parent banner    -> 6 spaces, then the classful network

The parent banner must name the CLASSFUL network containing every child, and
says "variably subnetted, N subnets, M masks" only when M >= 2; with a single
mask IOS prints "is subnetted, N subnets". scripts/validate.py asserts all of
this against the generated exhibits, so build groups that satisfy it.
"""

LEGEND = """Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2
       i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
       ia - IS-IS inter area, * - candidate default, U - per-user static route
       o - ODR, P - periodic downloaded static route, H - NHRP, l - LISP
       a - application route
       + - replicated route, % - next hop override"""


def top(code, rest):
    """Top-level route entry (prefix at column 7)."""
    return f"{code:<6}{rest}"


def kid(code, rest):
    """Route entry beneath a subnetted parent (prefix at column 10)."""
    return f"{code:<9}{rest}"


def parent(rest):
    """The 'x.x.x.x/y is [variably ]subnetted, ...' banner."""
    return f"      {rest}"


def cont(anchor_line, rest):
    """Continuation line for an additional equal-cost path.

    Aligns the '[' under the '[' of the line above, as IOS does.
    """
    return " " * anchor_line.index("[") + rest


def route_table(prompt, golr, lines, legend=LEGEND):
    """A full `show ip route` capture."""
    parts = [f"{prompt}# show ip route", legend, "", golr, ""]
    parts.extend(lines)
    return "\n".join(parts)


def route_entry(prompt, query, prefix, known_via, distance, metric, extra_type,
                update_from, update_intf, age, rdb_from, share=1, tail=()):
    """A `show ip route <address>` capture (the single-entry detail view)."""
    lines = [
        f"{prompt}# show ip route {query}",
        f"Routing entry for {prefix}",
        f'  Known via "{known_via}", distance {distance}, metric {metric}'
        + (f", {extra_type}" if extra_type else ""),
        f"  Last update from {update_from} on {update_intf}, {age} ago",
        "  Routing Descriptor Blocks:",
        f"  * {update_from}, from {rdb_from}, {age} ago, via {update_intf}",
        f"      Route metric is {metric}, traffic share count is {share}",
    ]
    lines.extend(f"      {t}" for t in tail)
    return "\n".join(lines)


def opts(*texts):
    """Options A, B, C ... in the given order."""
    return [{"id": chr(65 + i), "text": t} for i, t in enumerate(texts)]


IPV6_LEGEND = """Codes: C - Connected, L - Local, S - Static, U - Per-user Static route
       B - BGP, R - RIP, H - NHRP, I1 - ISIS L1
       I2 - ISIS L2, IA - ISIS interarea, IS - ISIS summary, D - EIGRP
       EX - EIGRP external, ND - ND Default, NDp - ND Prefix, DCE - Destination
       NDr - Redirect, RL - RPL, O - OSPF Intra, OI - OSPF Inter
       OE1 - OSPF ext 1, OE2 - OSPF ext 2, ON1 - OSPF NSSA ext 1
       ON2 - OSPF NSSA ext 2, la - LISP alt, lr - LISP site-registrations
       ld - LISP dyn-eid, lA - LISP away, a - Application"""


def v6(code, prefix, ad_metric, via):
    """One IPv6 route: code at col 1, prefix at col 5, 'via' on the next line."""
    return f"{code:<4}{prefix} [{ad_metric}]\n     via {via}"


def ipv6_route_table(prompt, entries, total, suffix="static", legend=IPV6_LEGEND):
    """A `show ipv6 route [static]` capture."""
    head = f"{prompt}# show ipv6 route" + (f" {suffix}" if suffix else "")
    return "\n".join([head, f"IPv6 Routing Table - default - {total} entries",
                      legend] + list(entries))


# --- OSPF -----------------------------------------------------------------
# `show ip ospf neighbor` column layout (IOS 15.x):
#   Neighbor ID  16 wide | Pri right-justified in 3 | 3 spaces
#   State        16 wide | Dead Time 12 wide | Address 16 wide | Interface
OSPF_NBR_HEADER = (f"{'Neighbor ID':<16}{'Pri':>3}   {'State':<16}"
                   f"{'Dead Time':<12}{'Address':<16}Interface")


def ospf_nbr(nid, pri, state, dead, addr, intf):
    """One `show ip ospf neighbor` row.

    On a point-to-point link the state has no elected role and prints as
    'FULL/  -'; pass that literally as `state`.
    """
    return f"{nid:<16}{pri:>3}   {state:<16}{dead:<12}{addr:<16}{intf}"


def ospf_neighbors(prompt, rows):
    """A `show ip ospf neighbor` capture."""
    return "\n".join([f"{prompt}# show ip ospf neighbor", "", OSPF_NBR_HEADER] + list(rows))


OSPF_INTF_HEADER = (f"{'Interface':<13}{'PID':<6}{'Area':<16}"
                    f"{'IP Address/Mask':<19}{'Cost':<6}{'State':<6}Nbrs F/C")


def ospf_intf(intf, pid, area, addr, cost, state, nbrs):
    """One `show ip ospf interface brief` row."""
    return f"{intf:<13}{pid:<6}{area:<16}{addr:<19}{cost:<6}{state:<6}{nbrs}"


def ospf_intf_brief(prompt, rows):
    """A `show ip ospf interface brief` capture."""
    return "\n".join([f"{prompt}# show ip ospf interface brief", OSPF_INTF_HEADER]
                     + list(rows))


def ospf_intf_detail(prompt, intf, addr_mask, area, pid, rid, nettype, cost,
                     state, priority, dr_id=None, dr_addr=None, bdr=None,
                     hello=10, dead=40, wait=40, retransmit=5, nbr_count=0,
                     adj_count=0):
    """A `show ip ospf interface <name>` capture."""
    lines = [
        f"{prompt}# show ip ospf interface {intf}",
        f"{intf} is up, line protocol is up",
        f"  Internet Address {addr_mask}, Area {area}, Attached via Network Statement",
        f"  Process ID {pid}, Router ID {rid}, Network Type {nettype}, Cost: {cost}",
        f"  Transmit Delay is 1 sec, State {state}, Priority {priority}",
    ]
    if dr_id:
        lines.append(f"  Designated Router (ID) {dr_id}, Interface address {dr_addr}")
    lines.append(f"  Backup Designated router (ID) {bdr}" if bdr
                 else "  No backup designated router on this network")
    lines += [
        f"  Timer intervals configured, Hello {hello}, Dead {dead}, Wait {wait},"
        f" Retransmit {retransmit}",
        f"  Neighbor Count is {nbr_count}, Adjacent neighbor count is {adj_count}",
    ]
    return "\n".join(lines)
