import random
from telegram.ext import ConversationHandler, MessageHandler, filters, CommandHandler
import json
from pathlib import Path
from telethon import functions

from bot.util.admin_wrapper import admin_required

# channels_path = Path(__file__).parent.parent.parent / "channels.json"
# with open(channels_path, 'r') as f:
#     channels = json.load(f)

channels = {
  "EmonTCG\ud83d\udc7b": {
    "id": -1002377605362,
    "topics": {
      "(APPROVE) PROMOTE YOUR BUSINESS": 2576
    }
  },
  "BakaDegenTCG": {
    "id": -1002554324211,
    "topics": {
      "Marketplace": 2
    }
  },
  "PokeSG": {
    "id": -1002636112979,
    "topics": {
      "Marketplace Buy/Sell (No Sealed Products)": 650
    }
  },
  "Mew\u2019s Den TCG \ud83c\udf1d": {
    "id": -1002763695697,
    "topics": {
      "Marketplace": 227
    }
  },
  "QuagsiresCove": {
    "id": -1002621209736,
    "topics": {
      "MARKETPLACE[ NO SEALED PRODUCTS]": 5
    }
  },
  "RosieTcg": {
    "id": -1002862670402,
    "topics": {
      "Buy & Sell Market Place": 2
    }
  },
  "Chua TCG": {
    "id": -1002418348358,
    "topics": {
      "Marketplace (NO SEALED PRODUCTS)": 6
    }
  },
  "SGTCGJunction": {
    "id": -1002133714470,
    "topics": {
      "Market Place": 15
    }
  },
  "JangTCG": {
    "id": -1002306310020,
    "topics": {
      "Marketplace (NO SEALED PRODUCTS)": 3
    }
  },
  "ALL THINGS TCG": {
    "id": -1002354619361,
    "topics": {
      "Marketplace (NO Sealed, Giveaways, Mystery Items)": 4
    }
  },
  "GenieTCG": {
    "id": -1002331315433,
    "topics": {
      "WTB/WTS/WTT - Open Channel": 59
    }
  },
  "JPokeCo": {
    "id": -1002530464897,
    "topics": {
      "J POKE MARKETPLACE (NO SEALED. )": 8
    }
  },
  "viviplayhouse": {
    "id": -1002660159960,
    "topics": {
      "market": 29
    }
  },
  "JirachuTCG": {
    "id": -1002873940739,
    "topics": {
      "Buy/Sell/Trade Marketplace": 15
    }
  },
  "OverthinkTCG": {
    "id": -1002974968248,
    "topics": {
      "Marketplace Buy/Sell/Trade (NO Sealed Products)": 8
    }
  },
  "HUATZARD \ud83d\udd25": {
    "id": -1002381288355,
    "topics": {
      "Marketplace (NO SEALED OR LINKS)": 516
    }
  },
  "Odyssey Collectibles": {
    "id": -1002444875579,
    "topics": {
      "Marketplace! Sell or buy anything!": 47
    }
  },
  "tenshi club. \u27e1": {
    "id": -1002581469755,
    "topics": {
      "\ud835\uddd5\ud835\udde8\ud835\uddec / \ud835\udde6\ud835\uddd8\ud835\udddf\ud835\udddf / \ud835\udde7\ud835\udde5\ud835\uddd4\ud835\uddd7\ud835\uddd8": 35
    }
  },
  "duckducktcg": {
    "id": -1002305794497,
    "topics": {
      "wts / wtb / wtt": 193
    }
  },
  "Thecollectorium.sg": {
    "id": -1002252561840,
    "topics": {
      "WTB/WTS/WTT (NO SEALED)": 3
    }
  },
  "Pok\u00e9mon TCG SGD": {
    "id": -1002426739478,
    "topics": {
      "MARKETPLACE": 5
    }
  },
  "SELL/TRADE POKEMON SG": {
    "id": -1001964537111,
    "topics": {
      "Pasar Malam (Trades/Sales/Chat)": 11381
    }
  },
  "PokaiShop": {
    "id": -1002376773165,
    "topics": {
      "Market Place": 6
    }
  },
  "Kakushi Vault": {
    "id": -1002616358320,
    "topics": {
      "MARKET (NO SEALED)": 2
    }
  },
  "TohKiMon Card Collectibles": {
    "id": -1001881092148,
    "topics": {
      "TCG Buy, Sell and Trade": 18942
    }
  },
  "The Pok\u00e9 Vault": {
    "id": -1002423121494,
    "topics": {
      "buy - sell - trade market": 22
    }
  }
}

WAITING_FOR_MESSAGE = 1

@admin_required
async def forward_start(update, context):
    await update.message.reply_text("Please forward me a message (or reply to one).")
    return WAITING_FOR_MESSAGE

async def forward_receive(update, context):
    client = context.bot_data["telethon_client"]
    msg = update.message
    if msg.forward_origin:
        source = msg.forward_origin  # user sent a forwarded message alongside /forward
    else:
        await msg.reply_text("❌ Please forward a message.")
        return ConversationHandler.END
    for group in channels:
        try:
            await client(functions.messages.ForwardMessagesRequest(
            from_peer=source.chat.id,
            id=[source.message_id],        # must be a list
            to_peer=channels[group]["id"],
            top_msg_id=next(iter(channels[group]["topics"].values())),
            # top_msg_id=1,  # ← topic ID goes here
            random_id=[random.randint(0, 2**63)]  # required — telethon won't auto-generate this
                ))
        except Exception as e:
            await msg.reply_text(f"❌ Error forwarding message: {e} (for group {group})")
            pass
        
    await msg.reply_text("✅ Message forwarded successfully!")
    return ConversationHandler.END

async def forward_cancel(update, context):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END



def get_forward_handler(private_only):
    return ConversationHandler(
        entry_points=[CommandHandler("forward", forward_start, filters=private_only)],
        states={
            WAITING_FOR_MESSAGE: [
                MessageHandler(filters.ALL & private_only, forward_receive)
            ],
        },
        fallbacks=[CommandHandler("cancel", forward_cancel)],
    )
