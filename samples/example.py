import datetime
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
from vcon.party import PartyHistory

def main():
    # Create a new vCon object
    vcon = Vcon.build_new()

    # Add parties
    caller = Party(tel="+1234567890", name="Alice", role="caller")
    agent = Party(tel="+1987654321", name="Bob", role="agent")
    vcon.add_party(caller)
    vcon.add_party(agent)

    # Add a dialog
    start_time = datetime.datetime.now()
    dialog = Dialog(
        type="text",
        start=start_time.isoformat(),
        parties=[0, 1],  # Indices of the parties in the vCon
        originator=0,  # The caller (Alice) is the originator
        mimetype="text/plain",
        body="Hello, I need help with my account.",
    )
    vcon.add_dialog(dialog)

    # Add a response from the agent
    response_time = start_time + datetime.timedelta(minutes=1)
    response = Dialog(
        type="text",
        start=response_time.isoformat(),
        parties=[0, 1],
        originator=1,  # The agent (Bob) is the originator
        mimetype="text/plain",
        body="Certainly! I'd be happy to help. Can you please provide your account number?",
    )
    vcon.add_dialog(response)

    # Add some metadata
    vcon.add_tag("customer_id", "12345")
    vcon.add_tag("interaction_id", "INT-001")

    # Add an attachment (e.g., a transcript)
    transcript = "Alice: Hello, I need help with my account.\nBob: Certainly! I'd be happy to help. Can you please provide your account number?"
    vcon.add_attachment(body=transcript, type="transcript", encoding="none")

    # Add some analysis (e.g., sentiment analysis)
    sentiment_analysis = {
        "overall_sentiment": "positive",
        "customer_sentiment": "neutral",
        "agent_sentiment": "positive"
    }
    vcon.add_analysis(
        type="sentiment",
        dialog=[0, 1],  # Indices of the dialogs analyzed
        vendor="SentimentAnalyzer",
        body=sentiment_analysis,
        encoding="none"
    )

    # Generate a key pair for signing
    private_key, public_key = Vcon.generate_key_pair()

    # Sign the vCon
    vcon.sign(private_key)

    # Verify the signature
    is_valid = vcon.verify(public_key)
    print(f"Signature is valid: {is_valid}")

    # Print the vCon as JSON
    print(vcon.to_json())

if __name__ == "__main__":
    main()