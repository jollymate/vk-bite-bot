from vk_api.longpoll import VkLongPoll
from vk_api.longpoll import VkEventType
import vk_captchasolver as vc
import threading
import random
import vk_api
import time
import cfg


token = cfg.token
headers = {
    "User-Agent": "Mozilla/5.0 (Android 10; Mobile; rv:100.0) Gecko/100.0 Firefox/100.0",
    "Connection": "keep-alive"
}
user_ignore = cfg.user_ignore
chat_ignore = cfg.chat_ignore
chance = list(range(cfg.chance))

vk_session = vk_api.VkApi(token=token)
vk_session.http.headers.update(headers)
vk = vk_session.get_api()
longpoll = VkLongPoll(vk_session)
m_file = open("words.txt", encoding="utf-8", errors="ignore")
msgs = [t for t in m_file.read().split("\n") if t]
m_file.close()


def print_msg(u_id, text):
    print("*" * 50)
    print("Сообщение в личке")
    print(f"От кого: https://vk.com/id{u_id}")
    print(f"Сообщение: {text}")


def thr_st(void, arg=()):
    b = threading.Thread(target=void, args=arg)
    b.start()


def friends():
    while True:
        try:
            friend_rq = vk.friends.getRequests()['items']
            for user in friend_rq:
                vk.friends.add(user_id=user)
            unfriend_rq = vk.friends.getRequests(out="true")['items']
            for user in unfriend_rq:
                vk.friends.delete(user_id=user)
        except:
            pass
        time.sleep(20)


thr_st(friends, ())

while True:
    try:
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and not event.from_me:
                peer_id = event.peer_id
                chat_id = peer_id - 2000000000
                user_id = event.user_id
                msg_id = event.message_id
                if chat_id not in chat_ignore and user_id not in user_ignore and user_id > 0 and event.from_me is False:
                    ch = random.choice(chance)
                    try:
                        if cfg.acc_id in event.raw['mentions']:
                            ch = 1
                            print_msg(user_id, event.text)
                    except:
                        pass
                    if event.text and peer_id < 2000000000:
                        print_msg(user_id, event.text)
                        kf_pos = event.text.find("https://vk.me/join/")
                        if kf_pos > -1:
                            link = event.text[kf_pos:].split(" ")[0]
                            vk.messages.joinChatByInviteLink(link=link)
                    if ch == 1:
                        msg = random.choice(msgs)
                        try:
                            vk.messages.send(
                                peer_id=peer_id,
                                random_id=random.randint(1, 999999),
                                message=msg,
                                reply_to=msg_id
                            )
                        except vk_api.Captcha as e:
                            answer = vc.solve(sid=e.sid, s=1)
                            time.sleep(5)
                            vk.messages.send(
                                peer_id=peer_id,
                                message=msg,
                                random_id=random.randint(1, 999999),
                                reply_to=msg_id,
                                captcha_key=answer,
                                captcha_sid=e.sid
                            )
    except KeyboardInterrupt:
        break
    except:
        pass
