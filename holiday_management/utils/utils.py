from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination


def get_termination_condition():
    """
    Get the termination condition for the agent.
    """
    TERMINATION_WORD = "stop"
    text_mention_termination = TextMentionTermination(TERMINATION_WORD)
    max_message_termination = MaxMessageTermination(max_messages=6)
    return text_mention_termination | max_message_termination