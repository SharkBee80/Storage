"""
2.0更新
获取服务器状态和延迟的刷新时间分开
修复bug
"""

import sys
import time
from collections import defaultdict
from mcstatus import JavaServer
import threading
from queue import Queue, Empty

O_server = "**************"  # 服务器地址address:port
player_info = "当前没有在线玩家。"


def input_with_timeout(note, timeout, default):
    queue = Queue()

    def get_input():
        mc_input = input(note)
        queue.put(mc_input)

    input_thread = threading.Thread(target=get_input)
    input_thread.start()

    try:
        address_input = queue.get(timeout=timeout)
    except Empty:
        address_input = default

    return address_input


# 获取服务器状态
while True:
    prompt = "输入Minecraft服务器地址 : (输入quit退出)\n默认服务器:************ (回车)\n##:"
    # noinspection PyBroadException
    try:
        server = input_with_timeout(prompt, 10, O_server)
        if server == "":
            server = O_server
        elif server == "quit":
            sys.exit(0)
        server = JavaServer.lookup(f"{server}")
        status = server.status()
    except Exception:
        print("请检查Minecraft服务器地址")
    else:
        break


# 服务器状态和在线人数
def Status():
    return f"服务器版本: {status.version.name}\n服务器地址: {server.address.host.upper()}\n在线人数: {status.players.online}/{status.players.max}"


def Players():
    global player_info
    # 玩家信息
    player_list = []
    player_counts = defaultdict(int)

    if status.players.sample:
        player_info = "在线玩家:"
        # 统计匿名玩家
        for player in status.players.sample:
            player_counts[player.name] += 1
            if player.name not in player_list:
                player_list.append(player.name)

        player_list.sort(reverse=False)

        for player in player_list:
            if player_counts[player] >= 2:
                player_info += f"\n  {player} ✕ {player_counts[player]}"
            else:
                player_info += f"\n  {player}"
    else:
        player_info = "当前没有在线玩家。"
    return player_info


# 服务器延迟
def Delay():
    latency = server.ping()
    return f"服务器延迟: {latency:.2f} ms"


# 更新服务器信息
def update_server_info():
    global status, server_info, players_info, error
    while True:
        # noinspection PyBroadException
        try:
            status = server.status()  # 每次循环获取最新的服务器状态
            server_info = Status()
            players_info = Players()
            error = "\n⭐"
            time.sleep(5)  # 每5秒更新一次 server_info 和 players_info
        except Exception:
            server_info = f"服务器版本: {status.version.name}\n服务器地址: {server.address.host.upper()}\n在线人数: */{status.players.max}"
            players_info = "在线玩家:\n  ***"
            error = "\nunknow error"
            time.sleep(5)
        except KeyboardInterrupt:
            break


# 更新延迟
# noinspection PyBroadException
def update_delay_info():
    global delay_info
    while True:
        try:
            delay_info = Delay()
            time.sleep(1)  # 每1秒更新一次 delay_info
        except Exception:
            delay_info = "服务器延迟: *** ms"
            time.sleep(5)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    error = "\n⭐"
    server_info = Status()
    players_info = Players()
    delay_info = Delay()

    # 创建并启动更新 server_info 和 players_info 的线程
    server_thread = threading.Thread(target=update_server_info)
    server_thread.daemon = True
    server_thread.start()

    # 创建并启动更新 delay_info 的线程
    delay_thread = threading.Thread(target=update_delay_info)
    delay_thread.daemon = True
    delay_thread.start()
    while True:
        # noinspection PyBroadException
        try:
            # 使用 ANSI 控制码将光标移动到行首并清除屏幕
            print("\033[H\033[J", end='')
            print(f"\r{server_info}\n{players_info}\n{delay_info}{error}", flush=True)

            time.sleep(1)

        except KeyboardInterrupt:
            print("\n已退出监控")
            break

        except Exception as e:
            try:
                print("unknow error")
                time.sleep(5)
            except KeyboardInterrupt:
                print("\n已退出监控")
                break
