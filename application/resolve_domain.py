import socket
import dns.name
import dns.query
import dns.dnssec
import dns.message
import dns.resolver
import dns.rdatatype


def resolve_domain(domain):
    # get nameservers for target domain
    response = dns.resolver.query(domain, dns.rdatatype.NS)

    # we'll use the first nameserver in this example
    nsname = response.rrset[0]  # name
    response = dns.resolver.query(str(nsname), rdtype=dns.rdatatype.A)
    nsaddr = response.rrset[0].to_text()  # IPv4

    # get DNSKEY for zone
    request = dns.message.make_query(domain,
                                     dns.rdatatype.DNSKEY,
                                     want_dnssec=True)

    # send the query
    response = dns.query.udp(request, nsaddr)

    print(response)

    if response.rcode() != 0:
        # HANDLE QUERY FAILED (SERVER ERROR OR NO DNSKEY RECORD)
        return None
    # answer should contain two RRSET: DNSKEY and RRSIG(DNSKEY)
    answer = response.answer
    if len(answer) != 2:
        # SOMETHING WENT WRONG
        return None
    # the DNSKEY should be self signed, validate it
    name = dns.name.from_text(domain)
    try:
        dns.dnssec.validate(answer[0], answer[1], {name: answer[0]})
    except dns.dnssec.ValidationFailure:
        return None
    else:
        return socket.gethostbyname(domain)


if __name__ == "__main__":
    print(resolve_domain("noodlespasswordvault.com"))
