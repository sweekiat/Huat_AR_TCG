import json

from telethon import TelegramClient
from telethon.tl.functions.messages import GetForumTopicsRequest
import os
from dotenv import load_dotenv

load_dotenv()
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')



client = TelegramClient('session_name', api_id, api_hash)
group_ids = [-1002377605362,-1002554324211,-1002636112979, -1002763695697, -1002621209736, -1002862670402, -1002418348358, -1002133714470, -1002306310020, -1002354619361, -1002331315433, -1002530464897, -1002660159960, -1002873940739, -1002974968248, -1002381288355, -1002444875579, -1002581469755, -1002305794497, -1002252561840, -1002426739478,-1001964537111,-1002376773165, -1002616358320, -1001881092148, -1002423121494]

async def list_topics():
    # Option 1: force-cache all dialogs first, then get_entity will work
    await client.get_dialogs()

    output = {}

    for group_id in group_ids:
        entity = await client.get_entity(group_id)

        result = await client(GetForumTopicsRequest(
            peer=entity,
            offset_date=0,
            offset_id=0,
            offset_topic=0,
            limit=100
        ))
        output[entity.title] = {
        "id": entity.id,
        "topics": {
    topic.title: topic.id
    for topic in result.topics
    if hasattr(topic, 'title')
}
}

    with open('output.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(json.dumps(output, indent=2))

async def send_message(dest_group_id:int, topic_id:str):
    try:
        await client.send_message(
    entity=dest_group_id,
    message="Hello topic!",
    reply_to=topic_id        # works for send_message too
    )
    except Exception as e:
        print(f"Error sending message: {e}")
    
async def forward_to_topic(client: TelegramClient, 
                            source_chat_id, 
                            source_message_id,
                            dest_group_id, 
                            topic_id):
    
    # Forward the message into a specific topic
    await client.forward_messages(
        entity=dest_group_id,
        messages=source_message_id,
        from_peer=source_chat_id,
        top_msg_id=topic_id        # This targets the specific topic
    )

with client:
    # client.loop.run_until_complete(list_topics())
    # Example usage of send_message
    client.loop.run_until_complete(send_message(-1002377605362, 1234567890))
    # Example usage of forward_to_topic
    # client.loop.run_until_complete(forward_to_topic(client, -1001234567890
