#!/usr/bin/env python3
"""
Example usage of vCon extensions

This script demonstrates how to use the lawful basis and WTF extensions
with the vCon library.
"""

import sys
import os
from datetime import datetime, timezone, timedelta

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from vcon import Vcon
from vcon.extensions.lawful_basis import LawfulBasisExtension
from vcon.extensions.wtf import WTFExtension


def main():
    """Main example function."""
    print("vCon Extensions Example")
    print("=" * 50)
    
    # Create a new vCon
    vcon = Vcon.build_new()
    print(f"Created vCon with UUID: {vcon.uuid}")
    
    # Add a party
    from vcon.party import Party
    party = Party("tel:+1234567890", "caller")
    vcon.add_party(party)
    print("Added party")
    
    # Add a dialog
    from vcon.dialog import Dialog
    from datetime import datetime, timezone
    dialog = Dialog(
        type="recording",
        start=datetime.now(timezone.utc),
        parties=[0],
        mimetype="audio/mp3",
        body="dGVzdCBhdWRpbyBkYXRh",  # "test audio data" in base64
        encoding="base64"
    )
    vcon.add_dialog(dialog)
    print("Added dialog")
    
    # Example 1: Lawful Basis Extension
    print("\n1. Lawful Basis Extension Example")
    print("-" * 40)
    
    try:
        # Add lawful basis attachment
        expiration = (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
        purpose_grants = [
            {
                "purpose": "recording",
                "granted": True,
                "granted_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "purpose": "analysis",
                "granted": True,
                "granted_at": datetime.now(timezone.utc).isoformat(),
                "conditions": ["anonymized_data_only"]
            }
        ]
        
        vcon.add_lawful_basis_attachment(
            lawful_basis="consent",
            expiration=expiration,
            purpose_grants=purpose_grants,
            party_index=0
        )
        print("✓ Added lawful basis attachment")
        
        # Check permissions
        has_recording_permission = vcon.check_lawful_basis_permission("recording", 0)
        has_marketing_permission = vcon.check_lawful_basis_permission("marketing", 0)
        
        print(f"✓ Recording permission: {has_recording_permission}")
        print(f"✓ Marketing permission: {has_marketing_permission}")
        
        # Find lawful basis attachments
        lawful_basis_attachments = vcon.find_lawful_basis_attachments(0)
        print(f"✓ Found {len(lawful_basis_attachments)} lawful basis attachments")
        
    except Exception as e:
        print(f"✗ Lawful basis extension error: {str(e)}")
    
    # Example 2: WTF Extension
    print("\n2. WTF Extension Example")
    print("-" * 40)
    
    try:
        # Add WTF transcription attachment
        transcript = {
            "text": "Hello, this is a test transcription.",
            "language": "en",
            "duration": 3.5,
            "confidence": 0.95
        }
        
        segments = [
            {
                "id": 0,
                "start": 0.0,
                "end": 1.5,
                "text": "Hello, this is",
                "confidence": 0.95
            },
            {
                "id": 1,
                "start": 1.5,
                "end": 3.5,
                "text": "a test transcription.",
                "confidence": 0.94
            }
        ]
        
        metadata = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "provider": "whisper",
            "model": "whisper-1"
        }
        
        vcon.add_wtf_transcription_attachment(
            transcript=transcript,
            segments=segments,
            metadata=metadata,
            party_index=0,
            dialog_index=0
        )
        print("✓ Added WTF transcription attachment")
        
        # Find WTF attachments
        wtf_attachments = vcon.find_wtf_attachments(0)
        print(f"✓ Found {len(wtf_attachments)} WTF attachments")
        
        # Export transcription
        if wtf_attachments:
            extension = WTFExtension()
            srt_content = extension.export_transcription(wtf_attachments[0], "srt")
            print("✓ Exported to SRT format:")
            print(srt_content[:200] + "..." if len(srt_content) > 200 else srt_content)
        
    except Exception as e:
        print(f"✗ WTF extension error: {str(e)}")
    
    # Example 3: Extension Validation
    print("\n3. Extension Validation Example")
    print("-" * 40)
    
    try:
        # Validate extensions
        validation_results = vcon.validate_extensions()
        print("✓ Extension validation results:")
        
        for extension_name, result in validation_results.items():
            if extension_name != "attachments":
                status = "✓ Valid" if result["is_valid"] else "✗ Invalid"
                print(f"  {extension_name}: {status}")
                if result.get("warnings"):
                    for warning in result["warnings"]:
                        print(f"    Warning: {warning}")
        
        # Process extensions
        processing_results = vcon.process_extensions()
        print("✓ Extension processing completed")
        
    except Exception as e:
        print(f"✗ Extension validation error: {str(e)}")
    
    # Example 4: Provider Conversion
    print("\n4. Provider Conversion Example")
    print("-" * 40)
    
    try:
        # Simulate Whisper data
        whisper_data = {
            "text": "Hello world from Whisper",
            "language": "en",
            "model": "whisper-1",
            "segments": [
                {
                    "id": 0,
                    "start": 0.0,
                    "end": 2.0,
                    "text": "Hello world from Whisper",
                    "avg_logprob": -0.5
                }
            ]
        }
        
        # Convert to WTF format
        extension = WTFExtension()
        wtf_attachment = extension.convert_from_provider(whisper_data, "whisper")
        print("✓ Converted Whisper data to WTF format")
        print(f"  Provider: {wtf_attachment['body']['metadata']['provider']}")
        print(f"  Text: {wtf_attachment['body']['transcript']['text']}")
        
    except Exception as e:
        print(f"✗ Provider conversion error: {str(e)}")
    
    # Save the vCon
    print("\n5. Saving vCon")
    print("-" * 40)
    
    try:
        vcon_json = vcon.dumps()
        print(f"✓ vCon serialized ({len(vcon_json)} characters)")
        
        # Save to file
        output_file = "extension_example.vcon.json"
        with open(output_file, 'w') as f:
            f.write(vcon_json)
        print(f"✓ Saved to {output_file}")
        
    except Exception as e:
        print(f"✗ Save error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Example completed!")


if __name__ == "__main__":
    main()
