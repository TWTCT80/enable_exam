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
