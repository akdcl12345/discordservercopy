import requests, time, result
from requests.api import delete

from requests.models import DEFAULT_REDIRECT_LIMIT

TOKEN = ""  #자신의 디스코드 토큰 쓰기

COPY_GUILD = ""  #복사할 서버 아이디쓰기

RESULT_GUILD = "" # 복사당할 서버 아이디 쓰기





# ==================================================================
API_BASE = "https://discord.com/api/v9"

def isRatelimit(obj):
    if obj.get("global", None) != None:
        return True, obj.get("retry_after", 0.0)
    else:
        return False, 0

headers = {
    "authorization": TOKEN
}

result_channels = requests.get(f"{API_BASE}/guilds/{RESULT_GUILD}/channels", headers=headers).json()
result_roles = requests.get(f"{API_BASE}/guilds/{RESULT_GUILD}/roles", headers=headers).json()
for channel in result_channels:
    while True:
        delete_channel = requests.delete(f"{API_BASE}/channels/{channel['id']}", headers=headers).json()
        ratelimit, sleep = isRatelimit(delete_channel)
        if ratelimit:
            time.sleep(sleep)
        else:
            print("Delete Channel", channel["id"])
            break
for channel in result_roles:
    while True:
        delete_channel = requests.delete(f"{API_BASE}/guilds/{RESULT_GUILD}/roles/{channel['id']}", headers=headers)
        try:
            delete_channel = delete_channel.json()
        except:
            delete_channel = {}
        ratelimit, sleep = isRatelimit(delete_channel)
        if ratelimit:
            time.sleep(sleep)
        else:
            print("Delete Role", channel["name"])
            break
original_channels = requests.get(f"{API_BASE}/guilds/{COPY_GUILD}/channels", headers=headers).json()
original_roles = requests.get(f"{API_BASE}/guilds/{COPY_GUILD}/roles", headers=headers).json()

original_guild = requests.get(f"{API_BASE}/guilds/{COPY_GUILD}", headers=headers).json()

system_channel = original_guild.get("system_channel_id")
if system_channel == None:
    system_channel = 0

new_system_channel = 0

category_channels = []
channels = []

for channel in original_channels:
    if channel["type"] == 4:
        category_channels.append(channel)
    else:
        channels.append(channel)

original_roles.sort(key=lambda x: x["position"], reverse=True)
for role in list(original_roles):
    while True:
        if role["managed"]:
            break
        if int(role["id"]) == int(COPY_GUILD):
            for i in range(len(channels)):
                par = channels[i].get("permission_overwrites")
                if par:
                    for j in range(len(par)):
                        if par[j]["id"] == role["id"]:
                            channels[i]["permission_overwrites"][j]["id"] = RESULT_GUILD
            break
        obj = role
        create_role = requests.post(f"{API_BASE}/guilds/{RESULT_GUILD}/roles", json=obj, headers=headers).json()
        ratelimit, sleep = isRatelimit(create_role)
        if ratelimit:
            time.sleep(sleep)
        else:
            for i in range(len(channels)):
                par = channels[i].get("permission_overwrites")
                if par:
                    for j in range(len(par)):
                        if par[j]["id"] == role["id"]:
                            channels[i]["permission_overwrites"][j]['id'] = create_role['id']
            for i in range(len(category_channels)):
                par = category_channels[i].get("permission_overwrites")
                if par:
                    for j in range(len(par)):
                        if par[j]["id"] == role["id"]:
                            category_channels[i]["permission_overwrites"][j]["id"] = create_role["id"]
            print("Success", create_role['id'])
            break
for category in category_channels:
    while True:
        obj = category
        # del obj["guild_id"]
        create_channel = requests.post(f"{API_BASE}/guilds/{RESULT_GUILD}/channels", json=obj,
                                       headers=headers).json()
        ratelimit, sleep = isRatelimit(create_channel)
        if ratelimit:
            time.sleep(sleep)
        else:
            for i in range(len(channels)):
                par = channels[i].get("parent_id")
                if par:
                    if par == category["id"]:
                        channels[i]["parent_id"] = create_channel["id"]
            print("Success Catetory", create_channel["id"])
            break

for channel in channels:
    try:
        while True:
            obj = channel
            try:
                del obj['icon_emoji']
                del obj['theme_color']
                del obj["guild_id"]
            except:
                pass

            create_channel = requests.post(f"{API_BASE}/guilds/{RESULT_GUILD}/channels", json=obj,
                                           headers=headers).json()
            ratelimit, sleep = isRatelimit(create_channel)
            if ratelimit:
                time.sleep(sleep)
            else:
                print("Success Channel", create_channel["id"])
                break
    except Exception as e:
        print(e)
        pass


