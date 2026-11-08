"""Read the scalar summaries the authors left inside the fine-tuned model folders.

The folders ship runs/*/events.out.tfevents.* from their own fine-tuning in March 2023.
This is a minimal TFRecord + protobuf reader, so it needs no tensorflow and no tensorboard:
Event.summary is field 5, Summary.value is field 1, Value.tag is field 1 and
Value.simple_value is field 2.
"""
import glob
import struct
import sys


def varint(buf, i):
    shift = 0
    val = 0
    while True:
        b = buf[i]
        val |= (b & 0x7F) << shift
        i += 1
        if not b & 0x80:
            return val, i
        shift += 7


def fields(buf):
    i = 0
    while i < len(buf):
        key, i = varint(buf, i)
        tag, wire = key >> 3, key & 7
        if wire == 0:
            val, i = varint(buf, i)
            yield tag, ("varint", val)
        elif wire == 1:
            yield tag, ("fixed64", buf[i:i + 8])
            i += 8
        elif wire == 2:
            n, i = varint(buf, i)
            yield tag, ("bytes", buf[i:i + n])
            i += n
        elif wire == 5:
            yield tag, ("fixed32", buf[i:i + 4])
            i += 4
        else:
            return


def records(path):
    with open(path, "rb") as fh:
        blob = fh.read()
    i = 0
    while i + 12 <= len(blob):
        (n,) = struct.unpack_from("<Q", blob, i)
        i += 12
        if i + n + 4 > len(blob):
            return
        yield blob[i:i + n]
        i += n + 4


for path in sorted(glob.glob(sys.argv[1], recursive=True)):
    print("##", path)
    for rec in records(path):
        step = None
        summary = None
        for tag, (wire, val) in fields(rec):
            if tag == 2 and wire == "varint":
                step = val
            if tag == 5 and wire == "bytes":
                summary = val
        if summary is None:
            continue
        for tag, (wire, val) in fields(summary):
            if tag != 1 or wire != "bytes":
                continue
            name, value = None, None
            for t2, (w2, v2) in fields(val):
                if t2 == 1 and w2 == "bytes":
                    name = v2.decode("utf8", "replace")
                elif t2 == 2 and w2 == "fixed32":
                    (value,) = struct.unpack("<f", v2)
            if name is not None and value is not None:
                print("step={} {}={:.6f}".format(step, name, value))
