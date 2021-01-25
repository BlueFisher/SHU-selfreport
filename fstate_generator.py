import base64
import json
from os import fstat
from pathlib import Path


def _generate_fstate_base64(fstate):
    fstate_json = json.dumps(fstate, ensure_ascii=False)
    fstate_bytes = fstate_json.encode("utf-8")
    return base64.b64encode(fstate_bytes).decode()


def generate_fstate_day(BaoSRQ, XiangXDZ):
    with open(Path(__file__).resolve().parent.joinpath('fstate_day.json'), encoding='utf8') as f:
        fstate = json.loads(f.read())

    fstate['p1_BaoSRQ']['Text'] = BaoSRQ
    fstate['p1_XiangXDZ']['Text'] = XiangXDZ

    fstate_base64 = _generate_fstate_base64(fstate)
    t = len(fstate_base64) // 2
    fstate_base64 = fstate_base64[:t] + 'F_STATE' + fstate_base64[t:]

    return fstate_base64


def generate_fstate_halfday(BaoSRQ):
    with open(Path(__file__).resolve().parent.joinpath('fstate_halfday.json'), encoding='utf8') as f:
        fstate = json.loads(f.read())

    fstate['p1_BaoSRQ']['Text'] = BaoSRQ

    fstate_base64 = _generate_fstate_base64(fstate)

    return fstate_base64


if __name__ == '__main__':
    print(generate_fstate_day())
    print(generate_fstate_halfday())
