import os
from yowsup.stacks import YowStackBuilder
from yowsup.layers import YowParallelLayer
from yowsup.layers.auth import AuthError
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity
from yowsup.layers.protocol_presence.protocolentities import PresenceProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities import OutgoingReceiptProtocolEntity
from yowsup.layers import YowLayerEvent
import schedule
import time
from datetime import datetime

# WhatsApp credentials
CREDENTIALS = ("your_phone_number", "your_whatsapp_password")

class SendLayer(YowParallelLayer):
    def __init__(self):
        super(SendLayer, self).__init__()
        self.queue = []

    def send_message(self, to, message):
        self.queue.append((to, message))
        self.on_event(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))

    def on_event(self, event):
        if event == YowNetworkLayer.EVENT_STATE_CONNECT:
            if self.queue:
                to, message = self.queue.pop(0)
                message_entity = TextMessageProtocolEntity(message, to=to)
                self.toLower(message_entity)
                self.toLower(PresenceProtocolEntity(name="WhatsApp Reminder Bot"))
                self.toLower(OutgoingReceiptProtocolEntity(message_entity.getId(), to))
            else:
                self.disconnect()

    def disconnect(self):
        self.toLower(YowLayerEvent(YowNetworkLayer.EVENT_STATE_DISCONNECT))

def send_whatsapp_message(to, message):
    stack_builder = YowStackBuilder()
    send_layer = SendLayer()
    stack = stack_builder.pushDefaultLayers(True).push(send_layer).build()
    stack.setCredentials(CREDENTIALS)

    try:
        send_layer.send_message(to, message)
        stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))
        stack.loop()
    except AuthError as e:
        print(f"Authentication Error: {e}")

def check_pending_dues():
    pending_dues = [
        {"name": "John Doe", "amount": 100, "due_date": "2025-02-23"},
        {"name": "Jane Smith", "amount": 200, "due_date": "2025-02-24"},
    ]
    today = datetime.now().strftime('%Y-%m-%d')
    for due in pending_dues:
        if due['due_date'] == today:
            message = f"Reminder: {due['name']}, you have a pending due of ${due['amount']} due today."
            send_whatsapp_message("recipient_phone_number", message)

def schedule_daily_reminders():
    schedule.every().day.at("09:00").do(check_pending_dues)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    schedule_daily_reminders()
