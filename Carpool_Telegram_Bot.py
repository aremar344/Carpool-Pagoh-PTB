import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler,ConversationHandler,filters,CallbackQueryHandler
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


#Above are all for importing and logging part
#START BELOW ----------------------------------------------------------------------------------------------------------------------------------------

#Give number for each states. 
PLACE_FROM_TO, PAX_NUMBER, WAIT_AT = range(3)


"""User type carpool request/carpool req/CARPOOL REQ/CARPOOL REQUEST to get the request template."""
async def carpool_req(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Provide carpool request predetermined choices for Place from-to, Pax num, Wait Place.""" 
    
    #Put the from - to places that the carpool service provide.
    keyboard = [
        [InlineKeyboardButton("1) A - B", callback_data="Place From-To: A - B"),
        InlineKeyboardButton("2) B - A", callback_data="Place From-To: B - A")],
            ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("You are requesting for a carpool.\nSelect below for your carpool details:\n1) Place From-To \n2) Pax Number \n3) Wait at", reply_markup=reply_markup)
    
    return PLACE_FROM_TO
 
async def pax_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """User select the number of passengers."""
    query= update.callback_query
    await query.answer()

    user_data = context.user_data
    user_data['place'] = query.data

    keyboard = [
        [InlineKeyboardButton("1pax", callback_data="Pax Number: 1"),
        InlineKeyboardButton("2pax", callback_data="Pax Number: 2"),
        InlineKeyboardButton("3pax", callback_data="Pax Number: 3")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("Neat,now how many person are going with you? If there are still available seats in the car, the driver can accept multiple requests.", reply_markup=reply_markup)

    return PAX_NUMBER

async def wait_at(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """User select the number of passengers."""
    query = update.callback_query
    await query.answer()

    user_data = context.user_data
    user_data['pax'] = query.data
    
    #Insert your waiting places.
    keyboard = [
        [InlineKeyboardButton("C", callback_data="Wait at: C"),
        InlineKeyboardButton("D", callback_data="Wait at: D"),
        InlineKeyboardButton("E", callback_data="Wait at: E")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("Alrighty, now just tell me where are you will be waiting for the car.", reply_markup=reply_markup)
    return WAIT_AT

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Display the gathered info and end the conversation."""
    
    #Since i dont know how to remove the buttons once completed. It will just show some texts. 
    keyboard = [
        [InlineKeyboardButton("Happy Carpooling!", callback_data="nothinghere")],
        [InlineKeyboardButton("And Stay Safe!", callback_data="nothingig")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query = update.callback_query
    await query.answer()

    user_data = context.user_data
    user_data['wait'] = query.data

    #Ends and show the request details.
    await query.edit_message_text(f"Your carpool request details:\n{user_data['place']}\n{user_data['pax']}\n{user_data['wait']}\n\n",reply_markup=reply_markup)

    
    user_data.clear()
    return ConversationHandler.END

"""Send a message when the command /help is issued."""
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Got a general question or feedback?\n" "Just type it here, and we’ll respond ASAP! \n" "For urgent matters, contact our support team directly by calling us at YOUR_HELPLINE_NUMBER. \n" "We’re here to make your carpool experience smooth and enjoyable! 🚘")

    """Start the bot."""
def main():
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("YOUR TOKEN").build()

   
    #application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("help", help_command))

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(carpool request|carpool req|CARPOOL REQ|CARPOOL REQUEST|Carpool req|Carpool request)$"), carpool_req)],
        states={
            PLACE_FROM_TO: [CallbackQueryHandler(pax_number)],
            PAX_NUMBER: [CallbackQueryHandler(wait_at)],
            WAIT_AT: [CallbackQueryHandler(done)]},
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
    )
    application.add_handler(conv_handler)

    # Start the Application
    application.run_polling(allowed_updates=Update.ALL_TYPES)


    

if __name__ == "__main__":
   main()
