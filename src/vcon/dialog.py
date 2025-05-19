import requests
import hashlib
import base64
from datetime import datetime
from typing import Optional, List, Dict, Union, Any, Tuple
from .party import PartyHistory
from dateutil import parser

MIME_TYPES = [
    "text/plain",
    "audio/x-wav",
    "audio/wav",
    "audio/wave",
    "audio/mpeg",
    "audio/mp3",
    "audio/ogg",
    "audio/webm",
    "audio/x-m4a",
    "audio/aac",
    "video/x-mp4",
    "video/ogg",
    "multipart/mixed",
    "message/rfc822",
    "image/jpeg",
    "image/tiff",
    "application/pdf",  # Added for image data
    "application/json"  # Added for signaling data
]


class Dialog:
    MIME_TYPES = [
        "text/plain",
        "audio/x-wav",
        "audio/wav",
        "audio/wave",
        "audio/mpeg",
        "audio/mp3",
        "audio/ogg",
        "audio/webm",
        "audio/x-m4a",
        "audio/aac",
        "video/x-mp4",
        "video/ogg",
        "multipart/mixed",
        "message/rfc822",
        "image/jpeg",
        "image/tiff",
        "application/pdf",  # Added for image data
        "application/json"  # Added for signaling data
    ]

    # Include the required types for tests to pass
    VALID_TYPES = [
        "recording", 
        "text", 
        "transfer", 
        "incomplete",
        "audio",
        "video"
    ]

    def __init__(
        self,
        type: str,
        start: Union[datetime, str],
        parties: List[int],
        originator: Optional[int] = None,
        mimetype: Optional[str] = None,
        filename: Optional[str] = None,
        body: Optional[str] = None,
        encoding: Optional[str] = None,
        url: Optional[str] = None,
        alg: Optional[str] = None,
        signature: Optional[str] = None,
        disposition: Optional[str] = None,
        party_history: Optional[List[PartyHistory]] = None,
        transferee: Optional[int] = None,
        transferor: Optional[int] = None,
        transfer_target: Optional[int] = None,
        original: Optional[int] = None,
        consultation: Optional[int] = None,
        target_dialog: Optional[int] = None,
        campaign: Optional[str] = None,
        interaction: Optional[str] = None,
        skill: Optional[str] = None,
        duration: Optional[float] = None,
        meta: Optional[dict] = None,
        # New parameters for signaling and extended functionality
        metadata: Optional[Dict[str, Any]] = None,
        transfer: Optional[Dict[str, Any]] = None,
        signaling: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> None:
        """
        Initialize a Dialog object.
        :param type: the type of the dialog (e.g. "text", "recording", "transfer", "incomplete")
        :type type: str
        :param start: the start time of the dialog
        :type start: datetime
        :param parties: the parties involved in the dialog
        :type parties: List[int]
        :param originator: the party that originated the dialog
        :type originator: int or None
        :param mimetype: the MIME type of the dialog body
        :type mimetype: str or None
        :param filename: the filename of the dialog body
        :type filename: str or None
        :param body: the body of the dialog
        :type body: str or None
        :param encoding: the encoding of the dialog body
        :type encoding: str or None
        :param url: the URL of the dialog
        :type url: str or None
        :param alg: the algorithm used to sign the dialog
        :type alg: str or None
        :param signature: the signature of the dialog
        :type signature: str or None
        :param disposition: the disposition of the dialog
        :type disposition: str or None
        :param party_history: the history of parties involved in the dialog
        :type party_history: List[PartyHistory] or None
        :param transferee: the party that the dialog was transferred to
        :type transferee: int or None
        :param transferor: the party that transferred the dialog
        :type transferor: int or None
        :param transfer_target: the target of the transfer
        :type transfer_target: int or None
        :param original: the original dialog
        :type original: int or None
        :param consultation: the consultation dialog
        :type consultation: int or None
        :param target_dialog: the target dialog
        :type target_dialog: int or None
        :param campaign: the campaign that the dialog is associated with
        :type campaign: str or None
        :param interaction: the interaction that the dialog is associated with
        :type interaction: str or None
        :param skill: the skill that the dialog is associated with
        :type skill: str or None
        :param duration: the duration of the dialog
        :type duration: float or None
        :param meta: additional metadata for the dialog
        :type meta: dict or None
        :param metadata: structured metadata for the dialog (newer format)
        :type metadata: dict or None
        :param transfer: transfer-specific information
        :type transfer: dict or None
        :param signaling: signaling-specific information
        :type signaling: dict or None
        :param kwargs: Additional attributes to be set on the dialog
        """

        # Validate dialog type
        if type not in self.VALID_TYPES:
            raise ValueError(f"Invalid dialog type: {type}. Must be one of {self.VALID_TYPES}")

        # Convert the start time to an ISO 8601 string from a datetime or a string
        if isinstance(start, datetime):
            start = start.isoformat()
        elif isinstance(start, str):
            start = parser.parse(start).isoformat()
        # Set attributes from named parameters that are not None
        for key, value in locals().items():
            if value is not None and key not in ("self", "kwargs"):
                setattr(self, key, value)

        # Don't merge meta and metadata; keep both for backward compatibility
        # This ensures tests relying on dialog.meta will continue to work
        # while also allowing new code to use dialog.metadata
        if not hasattr(self, "metadata") and hasattr(self, "meta"):
            self.metadata = self.meta.copy() if self.meta else {}
        elif not hasattr(self, "meta") and hasattr(self, "metadata"):
            self.meta = self.metadata.copy() if self.metadata else {}
        elif not hasattr(self, "metadata") and not hasattr(self, "meta"):
            self.metadata = {}
            self.meta = {}

        # Set any additional kwargs as attributes
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)

        # Handling for specific dialog types
        if type == "incomplete" and not hasattr(self, "disposition"):
            raise ValueError("Dialog type 'incomplete' requires a disposition")

    def to_dict(self):
        """
        Returns a dictionary representation of the Dialog object.

        :return: a dictionary containing all non-None Dialog object attributes
        :rtype: dict
        """
        # Check to see if the start time provided. If not,
        # set the start time to the current time
        if not hasattr(self, "start"):
            self.start = datetime.now().isoformat()

        # Get all attributes of the object
        dialog_dict = self.__dict__.copy()

        # Handle party_history specially
        if hasattr(self, "party_history") and self.party_history:
            dialog_dict["party_history"] = [
                party_history.to_dict() for party_history in self.party_history
            ]

        return {k: v for k, v in dialog_dict.items() if v is not None}

    def add_external_data(self, url: str, filename: str, mimetype: str) -> None:
        """
        Add external data to the dialog.

        :param url: the URL of the external data
        :type url: str
        :return: None
        :rtype: None
        """
        response = requests.get(url)
        if response.status_code == 200:
            self.mimetype = response.headers["Content-Type"]
        else:
            raise Exception(f"Failed to fetch external data: {response.status_code}")

        # Override the filename if provided, otherwise use the filename from the URL
        if filename:
            self.filename = filename
        else:
            # Extract filename from URL, removing any query parameters
            url_path = url.split("?")[0]
            self.filename = url_path.split("/")[-1]

        # Override the mimetype if provided, otherwise use the mimetype from the URL
        if mimetype:
            self.mimetype = mimetype

        # Calculate the SHA-256 hash of the body as the signature
        self.alg = "sha256"
        self.encoding = "base64url"
        self.signature = base64.urlsafe_b64encode(
            hashlib.sha256(response.text.encode()).digest()
        ).decode()

    def add_inline_data(self, body: str, filename: str, mimetype: str) -> None:
        """
        Add inline data to the dialog.

        :param body: the body of the inline data
        :type body: str
        :param filename: the filename of the inline data
        :type filename: str
        :param mimetype: the mimetype of the inline data
        :type mimetype: str
        :return: None
        :rtype: None
        """
        self.body = body
        self.mimetype = mimetype
        self.filename = filename
        self.alg = "sha256"
        self.encoding = "base64url"
        self.signature = base64.urlsafe_b64encode(
            hashlib.sha256(self.body.encode()).digest()
        ).decode()

    def is_external_data(self) -> bool:
        """
        Check if the dialog is an external data dialog.

        :return: True if the dialog is an external data dialog, False otherwise
        :rtype: bool
        """
        return hasattr(self, "url")

    def is_inline_data(self) -> bool:
        """
        Check if the dialog is an inline data dialog.

        :return: True if the dialog is an inline data dialog, False otherwise
        :rtype: bool
        """
        return not self.is_external_data()

    def is_text(self) -> bool:
        """
        Check if the dialog is a text dialog.
        :return: True if the dialog is a text dialog, False otherwise
        :rtype: bool
        """
        return hasattr(self, "type") and self.type == "text"
    
    def is_recording(self) -> bool:
        """
        Check if the dialog is a recording dialog.
        :return: True if the dialog is a recording dialog, False otherwise
        :rtype: bool
        """
        return hasattr(self, "type") and self.type == "recording"
    
    def is_transfer(self) -> bool:
        """
        Check if the dialog is a transfer dialog.
        :return: True if the dialog is a transfer dialog, False otherwise
        :rtype: bool
        """
        return hasattr(self, "type") and self.type == "transfer"
    
    def is_incomplete(self) -> bool:
        """
        Check if the dialog is an incomplete dialog.
        :return: True if the dialog is an incomplete dialog, False otherwise
        :rtype: bool
        """
        return hasattr(self, "type") and self.type == "incomplete"
    
    def is_audio(self) -> bool:
        """
        Check if the dialog has audio content.
        :return: True if the dialog has audio content, False otherwise
        :rtype: bool
        """
        return self.mimetype in [
            "audio/x-wav",
            "audio/wav",
            "audio/wave",
            "audio/mpeg",
            "audio/mp3",
            "audio/ogg",
            "audio/webm",
            "audio/x-m4a",
            "audio/aac",
        ]
    
    def is_video(self) -> bool:
        """
        Check if the dialog has video content.
        :return: True if the dialog has video content, False otherwise
        :rtype: bool
        """
        return hasattr(self, "mimetype") and self.mimetype in ["video/x-mp4", "video/ogg"]
    
    def is_email(self) -> bool:
        """
        Check if the dialog is an email dialog.
        :return: True if the dialog is an email dialog, False otherwise
        :rtype: bool
        """
        return hasattr(self, "mimetype") and self.mimetype == "message/rfc822"
    
    def is_image(self) -> bool:
        """
        Check if the dialog has image content.
        
        :return: True if the dialog has image content, False otherwise
        :rtype: bool
        """
        return hasattr(self, "mimetype") and self.mimetype in [
            "image/jpeg", 
            "image/tiff", 
            "application/pdf"
        ]
        
    def is_pdf(self) -> bool:
        """
        Check if the dialog has PDF content.
        
        :return: True if the dialog has PDF content, False otherwise
        :rtype: bool
        """
        return hasattr(self, "mimetype") and self.mimetype == "application/pdf"

    def add_image_data(self, image_path: str, mimetype: Optional[str] = None) -> None:
        """
        Add image data to the dialog from a local file.
        
        :param image_path: Path to the image file
        :type image_path: str
        :param mimetype: MIME type of the image (optional, auto-detected if not provided)
        :type mimetype: str or None
        :return: None
        :rtype: None
        """
        import os
        import mimetypes
        
        # Auto-detect mimetype if not provided
        if not mimetype:
            mimetype, _ = mimetypes.guess_type(image_path)
            
            if not mimetype or mimetype not in ["image/jpeg", "image/tiff", "application/pdf"]:
                raise ValueError(f"Unsupported image format. Must be JPEG, TIFF, or PDF.")
        
        # Read image data
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Extract filename from path
        filename = os.path.basename(image_path)
        
        # Add as inline data
        self.body = base64.b64encode(image_data).decode('utf-8')
        self.mimetype = mimetype
        self.filename = filename
        self.encoding = "base64"
        
        # Calculate hash for integrity validation
        self.alg = "sha256"
        self.signature = base64.urlsafe_b64encode(
            hashlib.sha256(image_data).digest()
        ).decode()
        
        # Extract metadata if possible
        try:
            self.extract_image_metadata(image_data, mimetype)
        except Exception as e:
            # Log the error but don't fail if metadata extraction fails
            print(f"Warning: Could not extract image metadata: {str(e)}")
            
    def extract_image_metadata(self, image_data: bytes, mimetype: str) -> None:
        """
        Extract metadata from image data and add it to the dialog metadata.
        
        :param image_data: Raw image data
        :type image_data: bytes
        :param mimetype: MIME type of the image
        :type mimetype: str
        :return: None
        :rtype: None
        """
        # Initialize metadata dict if it doesn't exist
        if not hasattr(self, "metadata") or not self.metadata:
            self.metadata = {}
        
        if "image" not in self.metadata:
            self.metadata["image"] = {}
        
        if mimetype == "application/pdf":
            # Extract PDF metadata
            try:
                import io
                from pypdf import PdfReader
                
                pdf = PdfReader(io.BytesIO(image_data))
                self.metadata["image"]["pages"] = len(pdf.pages)
                
                if pdf.metadata:
                    for key, value in pdf.metadata.items():
                        # Convert PDF metadata keys to standard format
                        clean_key = key.lower().replace('/', '_')
                        self.metadata["image"][clean_key] = str(value)
            except ImportError:
                # PyPDF not installed
                self.metadata["image"]["note"] = "Install PyPDF for enhanced PDF metadata"
        
        elif mimetype in ["image/jpeg", "image/tiff"]:
            # Extract image metadata
            try:
                import io
                from PIL import Image, ExifTags
                
                img = Image.open(io.BytesIO(image_data))
                self.metadata["image"]["width"] = img.width
                self.metadata["image"]["height"] = img.height
                self.metadata["image"]["format"] = img.format
                
                # Extract EXIF data if available
                if hasattr(img, '_getexif') and img._getexif():
                    exif = {
                        ExifTags.TAGS.get(tag, tag): value
                        for tag, value in img._getexif().items()
                        if tag in ExifTags.TAGS
                    }
                    
                    # Add select EXIF data to metadata
                    for key in ['DateTimeOriginal', 'Make', 'Model', 'Orientation']:
                        if key in exif:
                            self.metadata["image"][key.lower()] = str(exif[key])
            except ImportError:
                # PIL not installed
                self.metadata["image"]["note"] = "Install Pillow for enhanced image metadata"

    def generate_thumbnail(self, max_size: Tuple[int, int] = (200, 200)) -> Optional[str]:
        """
        Generate a thumbnail for the image and return it as a base64-encoded string.
        
        :param max_size: Maximum thumbnail dimensions (width, height)
        :type max_size: Tuple[int, int]
        :return: Base64-encoded thumbnail or None if generation fails
        :rtype: str or None
        """
        if not self.is_image():
            return None
            
        try:
            import io
            from PIL import Image
            
            # Get image data
            if hasattr(self, "body") and self.body:
                if self.encoding in ["base64", "base64url"]:
                    image_data = base64.b64decode(self.body)
                else:
                    # If not base64 encoded, assume it's already raw data
                    image_data = self.body.encode() if isinstance(self.body, str) else self.body
            else:
                # For external data
                if self.is_external_data():
                    response = requests.get(self.url)
                    if response.status_code != 200:
                        return None
                    image_data = response.content
                else:
                    return None
            
            # For PDFs, just return None as they require special handling
            if self.mimetype == "application/pdf":
                return None
                
            # Generate thumbnail
            img = Image.open(io.BytesIO(image_data))
            img.thumbnail(max_size)
            
            # Save thumbnail to bytes
            thumb_io = io.BytesIO()
            img.save(thumb_io, format='JPEG')
            thumb_data = thumb_io.getvalue()
            
            # Return base64-encoded thumbnail
            return base64.b64encode(thumb_data).decode('utf-8')
        except Exception as e:
            print(f"Thumbnail generation failed: {str(e)}")
            return None
    
    def is_external_data_changed(self) -> bool:
        """
        Check to see if it's an external data dialog, that the contents are valid by
        checking the hash of the body against the signature.

        :return: True if the dialog is an external data dialog and the contents are valid, False otherwise
        :rtype: bool
        """
        if not self.is_external_data():
            return False
        try:
            body_hash = base64.urlsafe_b64decode(self.signature.encode())
            return hashlib.sha256(self.body.encode()).digest() != body_hash
        except Exception as e:
            print(e)
            return True

    # Convert the dialog from an external data dialog to an inline data dialog
    # by reading the contents from the URL then adding the contents to the body
    def to_inline_data(self) -> None:
        """
        Convert the dialog from an external data dialog to an inline data dialog
        by reading the contents from the URL then adding the contents to the body.

        :return: None
        :rtype: None
        """
        # Read the contents from the URL
        response = requests.get(self.url)
        if response.status_code == 200:
            # For binary content, use response.content instead of response.text
            raw_content = response.content
            # Base64url encode the body
            self.body = base64.urlsafe_b64encode(raw_content).decode()
            self.mimetype = response.headers.get("Content-Type")
        else:
            raise Exception(f"Failed to fetch external data: {response.status_code}")

        # Calculate the SHA-256 hash of the original binary content
        self.alg = "sha256"
        self.encoding = "base64url"
        self.signature = base64.urlsafe_b64encode(
            hashlib.sha256(raw_content).digest()
        ).decode()

        # Set the filename if it doesn't exist
        if not hasattr(self, "filename"):
            self.filename = self.url.split("/")[-1]

        # Remove the url since this is now inline data
        delattr(self, "url")