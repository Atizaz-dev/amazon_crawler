import random

PROXIES = [
    '207.244.217.165:6712:kpjuvqbe:m5zo956p8177',
    '64.137.42.112:5157:kpjuvqbe:m5zo956p8177',
]

proxy_list = []
for proxy in PROXIES:
    proxy = proxy.split(':')
    proxy_list.append(f"http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}")


def get_proxy():
    return random.choice(proxy_list)
