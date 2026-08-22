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


# --- HSRP / FHRP ----------------------------------------------------------
# `show standby brief` column layout (IOS 15.x). The 'P' column sits at
# column 22, which is what the legend's '|' points at.
STANDBY_COLS = (f"{'Interface':<12}{'Grp':<5}{'Pri':<4}{'P':<2}{'State':<8}"
                f"{'Active':<16}{'Standby':<16}Virtual IP")
_P_COL = 12 + 5 + 4  # zero-based index of the P column


def standby_row(intf, grp, pri, preempt, state, active, standby, vip):
    """One `show standby brief` row. `preempt` True prints P in the P column."""
    return (f"{intf:<12}{grp:<5}{pri:<4}{'P' if preempt else ' ':<2}"
            f"{state:<8}{active:<16}{standby:<16}{vip}")


def standby_brief(prompt, rows):
    """A `show standby brief` capture, including the preempt legend."""
    pad = " " * _P_COL
    return "\n".join([
        f"{prompt}# show standby brief",
        f"{pad}P indicates configured to preempt.",
        f"{pad}|",
        STANDBY_COLS,
    ] + list(rows))


def hsrp_v1_vmac(group):
    """HSRP version 1 virtual MAC: 0000.0C07.ACxx where xx is the group in hex."""
    return f"0000.0c07.ac{group:02x}"


# --- show ip interface brief ----------------------------------------------
IPINT_HEADER = (f"{'Interface':<23}{'IP-Address':<16}{'OK?':<4}{'Method':<7}"
                f"{'Status':<22}Protocol")


def ipint(intf, addr, ok="YES", method="manual", status="up", proto="up"):
    """One `show ip interface brief` row."""
    return f"{intf:<23}{addr:<16}{ok:<4}{method:<7}{status:<22}{proto}"


def ip_int_brief(prompt, rows):
    """A `show ip interface brief` capture."""
    return "\n".join([f"{prompt}# show ip interface brief", IPINT_HEADER] + list(rows))


# --- show ipv6 interface brief --------------------------------------------
def ipv6_int(intf, status, addrs):
    """One `show ipv6 interface brief` block: name, [status], indented addresses."""
    return "\n".join([f"{intf:<23}[{status}]"] + [f"    {a}" for a in addrs])


def ipv6_int_brief(prompt, blocks):
    """A `show ipv6 interface brief` capture."""
    return "\n".join([f"{prompt}# show ipv6 interface brief"] + list(blocks))


# --- show interfaces status -----------------------------------------------
# Duplex and Speed are right-justified in 6, which is why "auto" shows with
# leading spaces and "a-full a-1000" lines up the way it does on a real switch.
INTF_STATUS_HEADER = (f"{'Port':<10}{'Name':<19}{'Status':<13}{'Vlan':<11}"
                      f"{'Duplex':>6} {'Speed':>6} Type")


def intf_status(port, name, status, vlan, duplex, speed,
                media="10/100/1000BaseTX"):
    """One `show interfaces status` row."""
    return (f"{port:<10}{name:<19}{status:<13}{vlan:<11}"
            f"{duplex:>6} {speed:>6} {media}")


def interfaces_status(prompt, rows):
    """A `show interfaces status` capture."""
    return "\n".join([f"{prompt}# show interfaces status", INTF_STATUS_HEADER]
                     + list(rows))


# --- show mac address-table -----------------------------------------------
def mac_row(vlan, mac, kind, port):
    """One `show mac address-table` row."""
    return f"{vlan:>4}    {mac:<18}{kind:<12}{port}"


def mac_table(prompt, rows, criterion=None):
    """A `show mac address-table` capture."""
    n = criterion if criterion is not None else len(rows)
    return "\n".join([
        f"{prompt}# show mac address-table",
        "          Mac Address Table",
        "-------------------------------------------",
        "",
        f"{'Vlan':<8}{'Mac Address':<18}{'Type':<12}Ports",
        f"{'----':<8}{'-----------':<18}{'--------':<12}-----",
    ] + list(rows) + [f"Total Mac Addresses for this criterion: {n}"])


# --- packet capture (analyser summary view, not IOS) ----------------------
CAPTURE_HEADER = (f"{'No.':<5}{'Time':<10}{'Source':<16}{'Destination':<16}"
                  f"{'Protocol':<10}{'Length':<8}Info")


def capture_row(no, time, src, dst, proto, length, info):
    """One summary row from a protocol analyser."""
    return (f"{no:<5}{time:<10}{src:<16}{dst:<16}"
            f"{proto:<10}{length:<8}{info}")


def packet_capture(rows, title=None):
    """A protocol-analyser summary listing."""
    head = [title] if title else []
    return "\n".join(head + [CAPTURE_HEADER] + list(rows))


# --- show power inline ----------------------------------------------------
POE_HEADER = (f"{'Interface':<10}{'Admin':<7}{'Oper':<11}{'Power':<8}"
              f"{'Device':<20}{'Class':<6}Max")
POE_UNITS = f"{'':<10}{'':<7}{'':<11}{'(Watts)':<8}"
POE_RULE = "--------- ------ ---------- ------- ------------------- ----- ----"


def poe_row(intf, admin, oper, power, device, cls, mx):
    """One `show power inline` row."""
    return f"{intf:<10}{admin:<7}{oper:<11}{power:<8}{device:<20}{cls:<6}{mx}"


def power_inline(prompt, available, used, rows):
    """A `show power inline` capture, with the budget summary line."""
    remaining = round(available - used, 1)
    return "\n".join([
        f"{prompt}# show power inline",
        f"Available:{available}(w)  Used:{used}(w)  Remaining:{remaining}(w)",
        "",
        POE_HEADER, POE_UNITS, POE_RULE,
    ] + list(rows))


# --- show vrf -------------------------------------------------------------
VRF_HEADER = f"  {'Name':<33}{'Default RD':<22}{'Protocols':<12}Interfaces"


def vrf_row(name, rd, protocols, interfaces):
    """One `show vrf` row."""
    return f"  {name:<33}{rd:<22}{protocols:<12}{interfaces}"


def show_vrf(prompt, rows):
    """A `show vrf` capture."""
    return "\n".join([f"{prompt}# show vrf", VRF_HEADER] + list(rows))


# --- show vlan brief ------------------------------------------------------
VLAN_HEADER = f"{'VLAN':<5}{'Name':<33}{'Status':<10}Ports"
VLAN_RULE = ("---- -------------------------------- --------- "
             "-------------------------------")

RESERVED_VLANS = [
    (1002, "fddi-default", "act/unsup", ""),
    (1003, "token-ring-default", "act/unsup", ""),
    (1004, "fddinet-default", "act/unsup", ""),
    (1005, "trnet-default", "act/unsup", ""),
]


def vlan_row(vlan, name, status, ports=""):
    """One `show vlan brief` row."""
    return f"{vlan:<5}{name:<33}{status:<10}{ports}".rstrip()


def vlan_brief(prompt, rows, reserved=True):
    """A `show vlan brief` capture."""
    body = list(rows)
    if reserved:
        body += [vlan_row(v, n, s, p) for v, n, s, p in RESERVED_VLANS]
    return "\n".join([f"{prompt}# show vlan brief", "", VLAN_HEADER, VLAN_RULE] + body)


# --- show lldp neighbors --------------------------------------------------
LLDP_CAPS = """Capability codes:
    (R) Router, (B) Bridge, (T) Telephone, (C) DOCSIS Cable Device
    (W) WLAN Access Point, (P) Repeater, (S) Station, (O) Other"""

LLDP_HEADER = (f"{'Device ID':<20}{'Local Intf':<15}{'Hold-time':<11}"
               f"{'Capability':<16}Port ID")


def lldp_row(device, local, hold, cap, port):
    """One `show lldp neighbors` row."""
    return f"{device:<20}{local:<15}{hold:<11}{cap:<16}{port}"


def lldp_neighbors(prompt, rows):
    """A `show lldp neighbors` capture."""
    return "\n".join([f"{prompt}# show lldp neighbors", LLDP_CAPS, "", LLDP_HEADER]
                     + list(rows) + ["", f"Total entries displayed: {len(rows)}"])


# --- show interfaces trunk ------------------------------------------------
# Four sections, each repeating the port column at width 12.
TRUNK_HEADER = (f"{'Port':<12}{'Mode':<17}{'Encapsulation':<15}{'Status':<14}"
                f"Native vlan")


def trunk_port(port, mode, encap, status, native):
    """One row of the first `show interfaces trunk` section."""
    return f"{port:<12}{mode:<17}{encap:<15}{status:<14}{native}"


def _trunk_section(title, pairs):
    return "\n".join([f"{'Port':<12}{title}"]
                     + [f"{p:<12}{v}" for p, v in pairs])


def interfaces_trunk(prompt, rows, allowed, active, forwarding):
    """A full `show interfaces trunk` capture.

    rows       list of trunk_port() strings
    allowed    [(port, "1-4094"), ...]
    active     [(port, "1,10,20"), ...]     allowed and active in the domain
    forwarding [(port, "1,10"), ...]        in spanning tree forwarding state
    """
    return "\n".join([
        f"{prompt}# show interfaces trunk", "", TRUNK_HEADER, *rows, "",
        _trunk_section("Vlans allowed on trunk", allowed), "",
        _trunk_section("Vlans allowed and active in management domain", active), "",
        _trunk_section("Vlans in spanning tree forwarding state and not pruned",
                       forwarding),
    ])


# --- show etherchannel summary --------------------------------------------
ETHERCHANNEL_FLAGS = """Flags:  D - down        P - bundled in port-channel
        I - stand-alone s - suspended
        H - Hot-standby (LACP only)
        R - Layer3      S - Layer2
        U - in use      f - failed to allocate aggregator

        M - not in use, minimum links not met
        u - unsuitable for bundling
        w - waiting to be aggregated
        d - default port

        A - formed by Auto LAG
"""

ETHERCHANNEL_RULE = ("------+-------------+-----------+"
                     "-----------------------------------------------")


def po_row(group, portchannel, protocol, ports):
    """One `show etherchannel summary` row; ports sit in 12-wide columns."""
    cols = "".join(f"{p:<12}" for p in ports).rstrip()
    return f"{group:<7}{portchannel:<16}{protocol:<10}{cols}"


def etherchannel_summary(prompt, rows, groups=1, aggregators=1):
    """A `show etherchannel summary` capture."""
    return "\n".join([
        f"{prompt}# show etherchannel summary",
        ETHERCHANNEL_FLAGS,
        "",
        f"Number of channel-groups in use: {groups}",
        f"Number of aggregators:           {aggregators}",
        "",
        "Group  Port-channel  Protocol    Ports",
        ETHERCHANNEL_RULE,
    ] + list(rows))


# --- show spanning-tree ---------------------------------------------------
STP_HEADER = (f"{'Interface':<20}{'Role':<5}{'Sts':<4}{'Cost':<10}"
              f"{'Prio.Nbr':<9}Type")
STP_RULE = ("------------------- ---- --- --------- -------- "
            "--------------------------------")


def stp_port(intf, role, sts, cost, prio, ptype="P2p"):
    """One `show spanning-tree` interface row.

    Rapid PVST+ roles: Root, Desg, Altn, Back. States: FWD, BLK, LRN.
    """
    return f"{intf:<20}{role:<5}{sts:<4}{cost:<10}{prio:<9}{ptype}"


def spanning_tree(prompt, vlan, root_pri, root_mac, bridge_pri, bridge_mac, ports,
                  root_cost=None, root_port=None):
    """A `show spanning-tree vlan <n>` capture.

    Pass root_cost/root_port as None when this switch IS the root, which is how
    IOS prints it: the cost and port lines are replaced by the statement that
    the bridge is the root.
    """
    lines = [
        f"{prompt}# show spanning-tree vlan {vlan}",
        "",
        f"VLAN{vlan:04d}",
        "  Spanning tree enabled protocol rstp",
        f"  Root ID    Priority    {root_pri}",
        f"             Address     {root_mac}",
    ]
    if root_cost is None:
        lines.append("             This bridge is the root")
    else:
        lines += [f"             Cost        {root_cost}",
                  f"             Port        {root_port}"]
    lines += [
        "             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec",
        "",
        f"  Bridge ID  Priority    {bridge_pri}  (priority {bridge_pri - vlan}"
        f" sys-id-ext {vlan})",
        f"             Address     {bridge_mac}",
        "             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec",
        "             Aging Time  300 sec",
        "",
        STP_HEADER,
        STP_RULE,
    ]
    return "\n".join(lines + list(ports))
