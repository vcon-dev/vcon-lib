"""Example script demonstrating the usage of the vCon library.

This script creates a sample vCon object representing a conversation between
a caller and an agent, including text dialogs, audio content, metadata, 
and analysis.
"""

import datetime
import base64
import os
from vcon import Vcon
from vcon.party import Party
from vcon.dialog import Dialog
import requests


def main():
    """Create and manipulate a sample vCon object."""
    # Create a new vCon object
    vcon = Vcon.build_new()

    # Add parties
    caller = Party(
        tel="+1234567890",
        name="Alice",
        role="caller",
    )
    agent = Party(
        tel="+1987654321",
        name="Bob",
        role="agent",
    )
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
        body=(
            "Certainly! I'd be happy to help. "
            "Can you please provide your account number?"
        ),
    )
    vcon.add_dialog(response)

    # Add an audio dialog from the MP3 file
    mp3_path = os.path.join(
        os.path.dirname(__file__), "c81c84f5-bb32-40a6-8a26-76749cc642c2.mp3"
    )
    with open(mp3_path, "rb") as f:
        audio_data = f.read()
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")

    audio_time = response_time + datetime.timedelta(minutes=1)
    audio_dialog = Dialog(
        type="audio",
        start=audio_time.isoformat(),
        parties=[0, 1],
        originator=0,  # The caller (Alice) is the originator
        mimetype="audio/mp3",
        body=audio_base64,
        encoding="base64",
        filename="conversation.mp3",
    )
    vcon.add_dialog(audio_dialog)

    # Add some metadata
    vcon.add_tag("customer_id", "12345")
    vcon.add_tag("interaction_id", "INT-001")

    # Add an attachment (e.g., a transcript)
    transcript = (
        "Alice: Hello, I need help with my account.\n"
        "Bob: Certainly! I'd be happy to help. "
        "Can you please provide your account number?\n"
        "[Audio conversation follows...]"
    )
    vcon.add_attachment(
        body=transcript,
        type="transcript",
        encoding="none",
    )

    # Add some analysis (e.g., sentiment analysis)
    sentiment_analysis = {
        "overall_sentiment": "positive",
        "customer_sentiment": "neutral",
        "agent_sentiment": "positive",
    }
    vcon.add_analysis(
        type="sentiment",
        dialog=[0, 1, 2],  # Indices of all dialogs analyzed
        vendor="SentimentAnalyzer",
        body=sentiment_analysis,
        encoding="none",
    )

    # Generate a key pair for signing
    private_key, public_key = Vcon.generate_key_pair()

    # Sign the vCon
    vcon.sign(private_key)

    # Verify the signature
    is_valid = vcon.verify(public_key)
    print(f"Signature is valid: {is_valid}")

    # Save the vCon to a file
    output_filename = "example.vcon.json"
    try:
        vcon.save_to_file(output_filename)
        print(f"Successfully saved vCon to {output_filename}")
    except IOError as e:
        print(f"Error saving vCon to file: {str(e)}")

    # Post the vCon to a server (example using httpbin.org as a test endpoint)
    try:
        # Example with authentication and custom headers
        headers = {
            'x-conserver-api-token': 'your-token-here',
            'x-custom-header': 'test-value'
        }
        response = vcon.post_to_url(
            'https://httpbin.org/post',  # Test endpoint that echoes back the request
            headers=headers
        )
        
        if response.status_code == 200:
            print("Successfully posted vCon to server")
            # The response from httpbin.org includes the sent data and headers
            response_data = response.json()
            print("Server received our custom headers:")
            for header, value in response_data['headers'].items():
                if header.lower().startswith('x-'):
                    print(f"  {header}: {value}")
        else:
            print(f"Server returned status code: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"Error posting vCon to server: {str(e)}")


if __name__ == "__main__":
    main()
