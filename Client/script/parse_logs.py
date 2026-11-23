import re
from statistics import mean


def read_text(path):
    if not path.exists():
        return ""
    return path.read_text(errors="replace")


def read_metadata(path):
    result = {}

    for line in read_text(path).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()

    return result


def parse_iperf(path):
    text = read_text(path)

    result = {
        "throughput_mbps": None,
        "jitter_ms": None,
        "packet_loss_percent": None,
        "receiver_status": (
            0 if re.search(r"\breceiver\b", text, re.I) else 1
        ),
    }

    lines = [
        line for line in text.splitlines()
        if re.search(r"\breceiver\b", line, re.I)
    ]

    if not lines:
        return result

    line = lines[-1]

    rate = re.search(
        r"([\d.]+)\s+(bits/sec|Kbits/sec|Mbits/sec|Gbits/sec)",
        line,
        re.I,
    )

    if rate:
        value = float(rate.group(1))
        unit = rate.group(2).lower()

        factors = {
            "bits/sec": 1e-6,
            "kbits/sec": 1e-3,
            "mbits/sec": 1,
            "gbits/sec": 1000,
        }

        result["throughput_mbps"] = value * factors[unit]

    udp = re.search(
        r"([\d.]+)\s*ms\s+\d+\s*/\s*\d+\s*\(([\d.]+)%\)",
        line,
        re.I,
    )

    if udp:
        result["jitter_ms"] = float(udp.group(1))
        result["packet_loss_percent"] = float(udp.group(2))

    return result


def parse_ping(path):
    text = read_text(path)

    summary = re.search(
        r"(?:rtt|round-trip)\s+min/avg/max"
        r"(?:/[\w]+)?\s*=\s*[\d.]+/([\d.]+)/",
        text,
        re.I,
    )

    if summary:
        return float(summary.group(1))

    samples = re.findall(
        r"\btime[=<]([\d.]+)\s*ms",
        text,
        re.I,
    )

    values = [float(value) for value in samples]

    return mean(values) if values else None



def parse_cpu(path):
    text = read_text(path)
    values = []

    for line in text.splitlines():
        if not re.search(r"%?Cpu\(s\):", line, re.I):
            continue

        # Ambil nilai idle, termasuk format .100.0 yang
        # bisa muncul karena format output top tertentu.
        match = re.search(
            r"(\d+(?:\.\d+)?|\.\d+)\s*id\b",
            line,
            re.I,
        )

        if not match:
            continue

        idle = float(match.group(1))

        if 0 <= idle <= 100:
            values.append(100.0 - idle)

    return (
        mean(values) if values else None,
        len(values),
    )



def fmt(value):
    return round(value, 4) if value is not None else ""
