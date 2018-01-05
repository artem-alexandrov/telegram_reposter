from pyrogram import Client
from pyrogram.api import functions, types
from time import sleep
import random

# Globals
client = Client(session_name="example")
chats_to_track = {}

def main():
    try:
        setup_client()
        setup_chats()
        update_messages()
        teardown_client()
    except e:
        print("error: ", e)
    finally:
        print("re-running...")
        main()

def setup_client():
    client.start()

def teardown_client():
    client.stop()

def setup_chats():
    all_chats = client.send(functions.messages.GetAllChats([])).chats
    
    print("choose chats to repost from: ")
    list_chats_to_track(all_chats)
    
    get_chat_to_repost_with_message(all_chats, "choose chat to repost to (only one): ")

def list_chats_to_track(chats):
    for chat in chats:
        add = input("add " + chat.title + "? (y/n) ")
        if add == "y":
            chats_to_track[chat.id] = 0

def get_chat_to_repost_with_message(chats, message):
    print(message)
    list_chats_to_repost(chats)
    validate_chat_to_repost(chats)

def list_chats_to_repost(chats):
    for idx, chat in enumerate(chats):
        if chat.id not in chats_to_track.keys():
            add = print(idx,  ") " + chat.title)

def validate_chat_to_repost(chats):
    idx = int(input("choose index: "))
    
    if len(chats) <= idx:
        get_chat_to_repost_with_message(chats, "try again, but do it wisely. Pick from specified list :")
        return

    chat = chats[idx]

    if chat.id not in chats_to_track.keys():
        chat_to_repost = chat.id
    else:
        get_chat_to_repost_with_message(chats, "try again, but do it wisely. Pick from specified list :")

def update_messages():
    for chat in chats_to_track.keys():
        print("checking messages for: ", chat)
        print("saved message id: ", chats_to_track[chat])
        
        limit = 1000
        offset_id = chats_to_track[chat]
        
        if chats_to_track[chat] == 0: # didn't check messages yet, take only the last one
            limit = 1
        
        chat_peer = client.resolve_peer(chat)
        
        messages = client.send(
                               functions.messages.GetHistory(
                                                             chat_peer, 
                                                             0, # offset_id
                                                             0, # offset_date
                                                             0, # add_offset
                                                             limit, # limit
                                                             0, # max_id
                                                             offset_id, # min_id
                                                             0 # hash
                                                             )
                               )
        
        def get_id(message):
            return message.id

        if chats_to_track[chat] == 0: # didn't check messages yet, save last message id and retry
            print("first run")
            if len(messages.messages) == 1:
                chats_to_track[chat] = messages.messages[0].id
                print("saved message - ", messages.messages[0])
        elif len(messages.messages) > 0:
            print("running, new messages (", len(messages.messages), ")")
            print(messages)
            chats_to_track[chat] = messages.messages[0].id

            client.send(
                       functions.messages.ForwardMessages(
                                              chat_peer,
                                              list(map(get_id, messages.messages)),
                                              random.sample(range(1, 1000000), 
                                                           len(messages.messages)),
                                              client.resolve_peer(chat_to_repost)
                                              )
                      )
        else:
            print("running, no new messages")

        sleep(0.3) # avoid FLOOD_TIMEOUT 

    sleep(3)
    update_messages()

main()
