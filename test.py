from ytscm import YTSCMonitor
from ytscm.superchat_event import YTSCEvent


def main():

    # create a new super chat monitor
    monitor = YTSCMonitor("F:/Coding with Strangers/strangest_queuemaker/client_secret_CLIENTID.json", update_function)

    # start monitoring super chats (update every 5 seconds)
    monitor.start(interval=5)

    # stop monitoring super chats
    # monitor.stop()


def update_function(super_chat_event):
    """
    This function gets called when our monitor detects a new Super Chat!
    Prints out the name and amount of the supporter's Super Chat. 
    :param super_chat_event - the new Super Chat event
    """

    # get an object containing information about the supporter
    supporter_details = super_chat_event.get_supporter_details()

    # get the supporter's channel name
    display_name = supporter_details.get_display_name()

    # get the amount of money our supporter donated as a string
    amount_string = super_chat_event.get_display_string()

    # print the name and amount that our supported donated
    print("{0} sent a {1} Super Chat!".format(display_name, amount_string))


if __name__ == '__main__':
    main()