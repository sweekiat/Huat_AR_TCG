const cardService = require("../services/cardService");
const { formatCardInfo, createInlineKeyboard } = require("../utils/helpers");

const handleCommands = {
  start: async (bot, msg) => {
    const chatId = msg.chat.id;
    const welcomeMessage = `
🎴 Welcome to Pokemon Card Inventory Bot!

Available commands:
/add - Add a new card to inventory
/inventory - View your collection
/search <name> - Search for cards
/buy <card_name> <quantity> - Mark cards as bought
/sell <card_name> <quantity> - Mark cards as sold

Let's start building your collection! 🚀
    `;

    bot.sendMessage(chatId, welcomeMessage);
  },

  add: async (bot, msg) => {
    const chatId = msg.chat.id;
    const userId = msg.from.id;

    bot.sendMessage(
      chatId,
      "What card would you like to add? Please provide:\n\n📝 Card Name\n🎯 Set Name\n🔢 Card Number\n💎 Condition (NM, LP, MP, HP, DMG)\n📊 Quantity\n💰 Purchase Price (optional)"
    );

    // Set user state to expect card details
    // You might want to implement a state management system here
    bot.once("message", async (response) => {
      if (response.chat.id === chatId && response.from.id === userId) {
        try {
          // Parse the message (you'd want better parsing logic)
          const lines = response.text.split("\n");
          const cardData = {
            user_id: userId,
            name: lines[0] || "Unknown Card",
            set_name: lines[1] || "Unknown Set",
            card_number: lines[2] || "001",
            condition: lines[3] || "NM",
            quantity: parseInt(lines[4]) || 1,
            purchase_price: parseFloat(lines[5]) || 0,
          };

          const result = await cardService.addCard(cardData);

          if (result.success) {
            bot.sendMessage(
              chatId,
              `✅ Added ${cardData.quantity}x ${cardData.name} to your inventory!`
            );
          } else {
            bot.sendMessage(chatId, `❌ Error adding card: ${result.error}`);
          }
        } catch (error) {
          bot.sendMessage(chatId, "❌ Invalid format. Please try again.");
        }
      }
    });
  },

  inventory: async (bot, msg) => {
    const chatId = msg.chat.id;
    const userId = msg.from.id;

    try {
      const cards = await cardService.getUserCards(userId);

      if (cards.length === 0) {
        bot.sendMessage(
          chatId,
          "📭 Your inventory is empty. Use /add to add some cards!"
        );
        return;
      }

      let message = "🎴 Your Pokemon Card Inventory:\n\n";
      let totalValue = 0;

      cards.forEach((card) => {
        const cardValue =
          card.quantity * (card.current_value || card.purchase_price || 0);
        totalValue += cardValue;

        message += `${formatCardInfo(card)}\n`;
      });

      message += `\n💰 Total Collection Value: $${totalValue.toFixed(2)}`;

      // Create inline keyboard for actions
      const keyboard = createInlineKeyboard([
        [{ text: "🔍 Search Cards", callback_data: "search_prompt" }],
        [{ text: "📊 View Stats", callback_data: "view_stats" }],
      ]);

      bot.sendMessage(chatId, message, { reply_markup: keyboard });
    } catch (error) {
      bot.sendMessage(chatId, "❌ Error fetching inventory");
      console.error("Inventory error:", error);
    }
  },

  buy: async (bot, msg, match) => {
    const chatId = msg.chat.id;
    const userId = msg.from.id;
    const input = match[1].split(" ");
    const quantity = parseInt(input.pop()) || 1;
    const cardName = input.join(" ");

    try {
      const result = await cardService.updateCardQuantity(
        userId,
        cardName,
        quantity,
        "buy"
      );

      if (result.success) {
        bot.sendMessage(
          chatId,
          `✅ Added ${quantity}x ${cardName} to your inventory!`
        );
      } else {
        bot.sendMessage(chatId, `❌ ${result.error}`);
      }
    } catch (error) {
      bot.sendMessage(chatId, "❌ Error processing purchase");
    }
  },

  sell: async (bot, msg, match) => {
    const chatId = msg.chat.id;
    const userId = msg.from.id;
    const input = match[1].split(" ");
    const quantity = parseInt(input.pop()) || 1;
    const cardName = input.join(" ");

    try {
      const result = await cardService.updateCardQuantity(
        userId,
        cardName,
        -quantity,
        "sell"
      );

      if (result.success) {
        bot.sendMessage(
          chatId,
          `✅ Sold ${quantity}x ${cardName} from your inventory!`
        );
      } else {
        bot.sendMessage(chatId, `❌ ${result.error}`);
      }
    } catch (error) {
      bot.sendMessage(chatId, "❌ Error processing sale");
    }
  },

  search: async (bot, msg, match) => {
    const chatId = msg.chat.id;
    const userId = msg.from.id;
    const searchTerm = match[1];

    try {
      const cards = await cardService.searchCards(userId, searchTerm);

      if (cards.length === 0) {
        bot.sendMessage(chatId, `🔍 No cards found matching "${searchTerm}"`);
        return;
      }

      let message = `🔍 Search results for "${searchTerm}":\n\n`;
      cards.forEach((card) => {
        message += `${formatCardInfo(card)}\n`;
      });

      bot.sendMessage(chatId, message);
    } catch (error) {
      bot.sendMessage(chatId, "❌ Error searching cards");
    }
  },
};

module.exports = { handleCommands };
