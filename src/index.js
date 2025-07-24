const TelegramBot = require("node-telegram-bot-api");
const { handleCommands } = require("./handlers/commands");
const { handleCallbacks } = require("./handlers/callbacks");
require("dotenv").config();

const bot = new TelegramBot(process.env.TELEGRAM_BOT_TOKEN, { polling: true });

// Handle commands
bot.onText(/\/start/, (msg) => handleCommands.start(bot, msg));
bot.onText(/\/add/, (msg) => handleCommands.add(bot, msg));
bot.onText(/\/inventory/, (msg) => handleCommands.inventory(bot, msg));
bot.onText(/\/sell (.+)/, (msg, match) => handleCommands.sell(bot, msg, match));
bot.onText(/\/buy (.+)/, (msg, match) => handleCommands.buy(bot, msg, match));
bot.onText(/\/search (.+)/, (msg, match) =>
  handleCommands.search(bot, msg, match)
);

// Handle callback queries (inline keyboard responses)
bot.on("callback_query", (query) => handleCallbacks(bot, query));

// Handle errors
bot.on("polling_error", (error) => {
  console.log("Polling error:", error);
});

console.log("Pokemon Card Bot is running...");
