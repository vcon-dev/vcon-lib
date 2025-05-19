import requests
import hashlib
import base64
import os
import logger
import tempfile
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
    "video/mp4",              # MP4 format
    "video/quicktime",        # MOV format
    "video/webm",             # WebM format
    "video/x-msvideo",        # AVI format
    "video/x-matroska",       # MKV format
    "video/mpeg",             # MPEG format
    "video/x-flv",            # FLV format
    "video/3gpp",             # 3GP format for mobile
    "video/x-m4v",            # M4V format (Apple variant)
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
        "video/mp4",              # MP4 format
        "video/quicktime",        # MOV format
        "video/webm",             # WebM format
        "video/x-msvideo",        # AVI format
        "video/x-matroska",       # MKV format
        "video/mpeg",             # MPEG format
        "video/x-flv",            # FLV format
        "video/3gpp",             # 3GP format for mobile
        "video/x-m4v",            # M4V format (Apple variant)
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
        # New parameters for video metadata
        resolution: Optional[str] = None,
        frame_rate: Optional[float] = None,
        codec: Optional[str] = None,
        bitrate: Optional[int] = None,
        thumbnail: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Initialize a Dialog object.
        :param type: the type of the dialog (e.g. "text", "recording", "transfer", "incomplete", "video")
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
        :param resolution: video resolution (e.g., "1920x1080")
        :type resolution: str or None
        :param frame_rate: video frame rate in fps
        :type frame_rate: float or None
        :param codec: video codec (e.g., "H.264", "H.265")
        :type codec: str or None
        :param bitrate: video bitrate in kbps
        :type bitrate: int or None
        :param thumbnail: base64-encoded thumbnail image
        :type thumbnail: str or None
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

        # Auto-detect mimetype for video type
        if type == "video" and not hasattr(self, "mimetype"):
            # Try to infer mimetype from filename extension if available
            if hasattr(self, "filename") and self.filename:
                ext = self.filename.split('.')[-1].lower()
                if ext == "mp4":
                    self.mimetype = "video/mp4"
                elif ext == "mov":
                    self.mimetype = "video/quicktime"
                elif ext == "webm":
                    self.mimetype = "video/webm"
                elif ext == "avi":
                    self.mimetype = "video/x-msvideo"
                elif ext == "mkv":
                    self.mimetype = "video/x-matroska"
                elif ext in ["mpg", "mpeg"]:
                    self.mimetype = "video/mpeg"
                elif ext == "flv":
                    self.mimetype = "video/x-flv"
                elif ext == "3gp":
                    self.mimetype = "video/3gpp"
                elif ext == "m4v":
                    self.mimetype = "video/x-m4v"
                else:
                    # Default to MP4 if we can't determine from extension
                    self.mimetype = "video/mp4"
            else:
                # Default mimetype for video
                self.mimetype = "video/mp4"

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
    
    def is_video(self, content_type=None) -> bool:
        """
        Check if the dialog has video content.
        
        Args:
            content_type: Optional content type to check. If None, use the dialog's mimetype.
        
        Returns:
            True if the content is a video format, False otherwise
        """
        # Use provided content_type or dialog's mimetype
        check_type = content_type if content_type is not None else getattr(self, "mimetype", None)
        
        if not check_type:
            return False
            
        # Check if it's any of the supported video types
        video_types = [
            "video/x-mp4",
            "video/ogg",
            "video/mp4",
            "video/quicktime",
            "video/webm",
            "video/x-msvideo",
            "video/x-matroska",
            "video/mpeg",
            "video/3gpp",
            "video/x-m4v",
            "video/x-flv"
        ]
        
        return check_type in video_types

    def add_video_data(self, video_data, filename=None, mimetype=None, inline=True, metadata=None) -> None:
        """
        Add video data to the dialog.
        
        Args:
            video_data: Binary video data or URL to video
            filename: Name of the video file
            mimetype: MIME type of the video, or auto-detected from filename if None
            inline: Whether to include the video as inline content (True) or external reference (False)
            metadata: Optional video metadata to include
            
        Returns:
            None
        """
        # Set dialog type to video
        self.type = "video"
        
        # Auto-detect mimetype from filename if not provided
        if not mimetype and filename:
            ext = filename.split('.')[-1].lower()
            ext_to_mimetype = {
                'mp4': 'video/mp4',
                'mov': 'video/quicktime',
                'webm': 'video/webm',
                'avi': 'video/x-msvideo',
                'mkv': 'video/x-matroska',
                'mpg': 'video/mpeg',
                'mpeg': 'video/mpeg',
                'flv': 'video/x-flv',
                'ogg': 'video/ogg'
            }
            mimetype = ext_to_mimetype.get(ext, 'video/mp4')  # Default to MP4 if unknown
        
        # Handle external vs inline data
        if inline:
            # For base64 encoding, convert to bytes if it's a string
            if isinstance(video_data, str) and not video_data.startswith('http'):
                video_data = video_data.encode()
                
            # Add inline data
            if isinstance(video_data, bytes):
                # Base64 encode the binary data
                encoded_data = base64.b64encode(video_data).decode()
                self.add_inline_data(encoded_data, filename, mimetype)
            else:
                # Assume it's already base64 encoded
                self.add_inline_data(video_data, filename, mimetype)
        else:
            # External data
            if isinstance(video_data, str) and (video_data.startswith('http://') or video_data.startswith('https://')):
                # It's a URL, use it directly
                self.add_external_data(video_data, filename, mimetype)
            else:
                # Cannot use non-URL as external data
                raise ValueError("External video references must be URLs")
        
        # Add metadata if provided
        if metadata:
            if not hasattr(self, "metadata"):
                self.metadata = {}
            if not hasattr(self, "meta"):
                self.meta = {}
                
            self.metadata["video"] = metadata
            self.meta["video"] = metadata

    def extract_video_metadata(self, video_path=None) -> dict:
        """
        Extract comprehensive metadata from video content using FFmpeg.
        
        Args:
            video_path: Optional path to video file. If None, uses the dialog's content.
            
        Returns:
            Dictionary containing detailed video metadata
        """
        import ffmpeg
        
        # Create temporary file if working with inline data
        temp_file = None
        try:
            if video_path is None:
                if self.is_inline_data():
                    # Decode base64 content to temporary file
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{self.get_video_format_from_mimetype()}")
                    video_data = base64.urlsafe_b64decode(self.body.encode())
                    temp_file.write(video_data)
                    temp_file.close()
                    video_path = temp_file.name
                elif self.is_external_data():
                    # Download from URL to temporary file
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{self.get_video_format_from_mimetype()}")
                    response = requests.get(self.url)
                    temp_file.write(response.content)
                    temp_file.close()
                    video_path = temp_file.name
                else:
                    raise ValueError("Cannot extract metadata: no video content available")
            
            # Use FFmpeg to extract metadata
            probe = ffmpeg.probe(video_path)
            
            # Find video stream
            video_stream = next((stream for stream in probe['streams'] 
                            if stream['codec_type'] == 'video'), None)
            
            if video_stream is None:
                raise ValueError("No video stream found in file")
            
            # Get format information
            format_info = probe.get('format', {})
            
            # Extract comprehensive metadata
            metadata = {
                "duration": float(format_info.get("duration", 0)),
                "size_bytes": int(format_info.get("size", 0)),
                "bit_rate": int(format_info.get("bit_rate", 0)),
                "format": format_info.get("format_name", ""),
                
                # Video stream details
                "codec": video_stream.get("codec_name", ""),
                "codec_long_name": video_stream.get("codec_long_name", ""),
                "width": int(video_stream.get("width", 0)),
                "height": int(video_stream.get("height", 0)),
                "display_aspect_ratio": video_stream.get("display_aspect_ratio", ""),
                "pixel_format": video_stream.get("pix_fmt", ""),
                "profile": video_stream.get("profile", ""),
                "level": video_stream.get("level", -1),
                
                # Frame rate calculation
                "frame_rate": self._calculate_frame_rate(video_stream.get("avg_frame_rate", "0/1")),
                "total_frames": int(video_stream.get("nb_frames", 0)),
                
                # Color details if available
                "color_space": video_stream.get("color_space", ""),
                "color_transfer": video_stream.get("color_transfer", ""),
                "color_primaries": video_stream.get("color_primaries", ""),
                
                # Additional format-specific data
                "contains_audio": any(stream["codec_type"] == "audio" for stream in probe.get("streams", [])),
                "timestamp": datetime.now().isoformat()
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting video metadata: {str(e)}")
            # Return minimal metadata on error
            return {
                "error": str(e),
                "format": self.get_video_format_from_mimetype(),
                "timestamp": datetime.now().isoformat()
            }
        
        finally:
            # Clean up temporary file if created
            if temp_file and os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
                
    def _calculate_frame_rate(self, frame_rate_str):
        """
        Calculate numeric frame rate from FFmpeg frame rate string.
        
        Args:
            frame_rate_str: Frame rate as string in format "num/den"
            
        Returns:
            Frame rate as float
        """
        try:
            if "/" in frame_rate_str:
                num, den = map(int, frame_rate_str.split("/"))
                if den == 0:
                    return 0
                return num / den
            else:
                return float(frame_rate_str)
        except (ValueError, ZeroDivisionError):
            return 0

    def generate_thumbnail(self, timestamp=0.0, width=320, height=240, quality=90) -> bytes:
        """
        Generate a high-quality thumbnail from the video at the specified timestamp.
        
        Args:
            timestamp: Time in seconds at which to extract the thumbnail frame
            width: Desired width of the thumbnail in pixels
            height: Desired height of the thumbnail in pixels
            quality: JPEG quality (1-100)
            
        Returns:
            Binary thumbnail data in JPEG format
        """
        import ffmpeg
        
        if not self.is_video():
            raise ValueError("Cannot generate thumbnail for non-video content")
        
        # Create temporary files
        temp_video = None
        temp_thumb = None
        
        try:
            # Setup source video file
            if self.is_inline_data():
                temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=f".{self.get_video_format_from_mimetype()}")
                video_data = base64.urlsafe_b64decode(self.body.encode())
                temp_video.write(video_data)
                temp_video.close()
                video_path = temp_video.name
            elif self.is_external_data():
                temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=f".{self.get_video_format_from_mimetype()}")
                response = requests.get(self.url)
                temp_video.write(response.content)
                temp_video.close()
                video_path = temp_video.name
            else:
                raise ValueError("Cannot generate thumbnail: no video content available")
            
            # Setup thumbnail output file
            temp_thumb = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_thumb.close()
            
            # Get video duration to validate timestamp
            probe = ffmpeg.probe(video_path)
            duration = float(probe.get("format", {}).get("duration", 0))
            
            # Ensure timestamp is within video duration
            validated_timestamp = min(max(0, timestamp), duration if duration > 0 else timestamp)
            
            # Generate thumbnail using FFmpeg
            (
                ffmpeg
                .input(video_path, ss=validated_timestamp)
                .filter('scale', width, height)
                .output(temp_thumb.name, vframes=1, q=min(max(1, 31 - int(quality * 0.3)), 31))
                .overwrite_output()
                .run(quiet=True)
            )
            
            # Read the generated thumbnail
            with open(temp_thumb.name, "rb") as f:
                thumbnail_data = f.read()
            
            # Add thumbnail to metadata
            if not hasattr(self, "metadata"):
                self.metadata = {}
            if not hasattr(self, "meta"):
                self.meta = {}
                
            if "video" not in self.metadata:
                self.metadata["video"] = {}
            if "video" not in self.meta:
                self.meta["video"] = {}
            
            # Store thumbnail as base64
            thumbnail_b64 = base64.b64encode(thumbnail_data).decode()
            
            self.metadata["video"]["thumbnail"] = {
                "data": thumbnail_b64,
                "content_type": "image/jpeg",
                "timestamp": validated_timestamp,
                "width": width,
                "height": height,
                "quality": quality
            }
            self.meta["video"]["thumbnail"] = self.metadata["video"]["thumbnail"]
            
            return thumbnail_data
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {str(e)}")
            raise
            
        finally:
            # Clean up temporary files
            if temp_video and os.path.exists(temp_video.name):
                os.unlink(temp_video.name)
            if temp_thumb and os.path.exists(temp_thumb.name):
                os.unlink(temp_thumb.name)

    def add_streaming_video_reference(self, reference_id, mimetype, metadata=None) -> None:
        """
        Add a reference to a streamable video.
        
        Args:
            reference_id: Unique identifier for the streamable video
            mimetype: MIME type of the video
            metadata: Optional video metadata
            
        Returns:
            None
        """
        self.type = "video"
        self.url = f"stream://{reference_id}"
        self.mimetype = mimetype
        
        # Add streaming-specific metadata
        if not hasattr(self, "metadata"):
            self.metadata = {}
        if not hasattr(self, "meta"):
            self.meta = {}
            
        self.metadata["streaming"] = {
            "reference_id": reference_id,
            "protocol": "stream"
        }
        self.meta["streaming"] = self.metadata["streaming"]
        
        # Add video metadata if provided
        if metadata:
            self.metadata["video"] = metadata
            self.meta["video"] = metadata
    

    def get_video_format_from_mimetype(self, mimetype) -> str:
        """
        Get the video format name from a MIME type.
        
        Args:
            mimetype: MIME type of the video
            
        Returns:
            Format name (mp4, mov, etc.)
        """
        mimetype_to_format = {
            'video/mp4': 'mp4',
            'video/x-mp4': 'mp4',
            'video/quicktime': 'mov',
            'video/webm': 'webm',
            'video/x-msvideo': 'avi',
            'video/x-matroska': 'mkv',
            'video/mpeg': 'mpeg',
            'video/x-flv': 'flv',
            'video/ogg': 'ogg'
        }
        
        return mimetype_to_format.get(mimetype, 'unknown')
    
    def has_thumbnail(self) -> bool:
        """
        Check if the video has a thumbnail.
        
        Returns:
            True if the video has a thumbnail, False otherwise
        """
        if hasattr(self, "metadata") and "video" in self.metadata:
            return "thumbnail" in self.metadata["video"]
        return False
    
    def add_video_with_optimal_storage(self, video_data, filename, mimetype=None, size_threshold_mb=10) -> None:
        """
        Add video with the optimal storage method based on size.
        
        Args:
            video_data: Binary video data or URL
            filename: Name of the video file
            mimetype: MIME type of the video (optional)
            size_threshold_mb: Size threshold in MB for inline vs external storage
            
        Returns:
            None
        """
        # Determine data size if it's binary data
        if isinstance(video_data, bytes):
            size_mb = len(video_data) / (1024 * 1024)
            
            # Use inline for small videos, external for larger ones
            if size_mb <= size_threshold_mb:
                self.add_video_data(video_data, filename, mimetype, inline=True)
            else:
                # For larger videos, we would typically upload to external storage
                # and then reference the URL, but this is a placeholder
                raise ValueError(
                    f"Video size ({size_mb:.2f} MB) exceeds threshold ({size_threshold_mb} MB). "
                    "Upload to external storage and use the URL instead."
                )
        elif isinstance(video_data, str) and (video_data.startswith('http://') or video_data.startswith('https://')):
            # It's already a URL, use external reference
            self.add_video_data(video_data, filename, mimetype, inline=False)
        else:
            # Unknown format
            raise ValueError("video_data must be binary data or a URL")
        
    def transcode_video(self, target_format, codec=None, bit_rate=None, width=None, height=None) -> None:
        """
        Transcode the video to a different format or with different encoding parameters.
        
        Args:
            target_format: Target video format (mp4, webm, etc.)
            codec: Video codec to use (h264, vp9, etc.)
            bit_rate: Target bitrate in bits per second
            width: Target width (if resizing)
            height: Target height (if resizing)
            
        Returns:
            None - updates the dialog's content in place
        """
        import ffmpeg
        
        if not self.is_video():
            raise ValueError("Cannot transcode non-video content")
        
        # Setup temporary files
        temp_input = None
        temp_output = None
        
        try:
            # Get source video
            if self.is_inline_data():
                temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=f".{self.get_video_format_from_mimetype()}")
                video_data = base64.urlsafe_b64decode(self.body.encode())
                temp_input.write(video_data)
                temp_input.close()
                input_path = temp_input.name
            elif self.is_external_data():
                temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=f".{self.get_video_format_from_mimetype()}")
                response = requests.get(self.url)
                temp_input.write(response.content)
                temp_input.close()
                input_path = temp_input.name
            else:
                raise ValueError("Cannot transcode: no video content available")
            
            # Setup output file
            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=f".{target_format}")
            temp_output.close()
            
            # Setup FFmpeg conversion
            stream = ffmpeg.input(input_path)
            
            # Apply filters if needed
            if width is not None and height is not None:
                stream = stream.filter('scale', width, height)
            
            # Setup output parameters
            output_params = {}
            if codec:
                output_params['c:v'] = codec
            if bit_rate:
                output_params['b:v'] = bit_rate
            
            # Run transcoding
            ffmpeg.output(stream, temp_output.name, **output_params).run(quiet=True)
            
            # Read the transcoded file
            with open(temp_output.name, "rb") as f:
                new_video_data = f.read()
            
            # Update the dialog with the new video
            ext_to_mimetype = {
                'mp4': 'video/mp4',
                'mov': 'video/quicktime',
                'webm': 'video/webm',
                'avi': 'video/x-msvideo',
                'mkv': 'video/x-matroska',
                'mpg': 'video/mpeg',
                'mpeg': 'video/mpeg',
                'flv': 'video/x-flv',
                'ogg': 'video/ogg'
            }
            
            new_mimetype = ext_to_mimetype.get(target_format, f'video/{target_format}')
            new_filename = f"{os.path.splitext(self.filename)[0]}.{target_format}" if hasattr(self, "filename") else f"video.{target_format}"
            
            # Extract metadata from new video
            metadata = self.extract_video_metadata(temp_output.name)
            
            # Use add_video_data to replace current content (maintaining inline/external status)
            if self.is_inline_data():
                encoded_data = base64.b64encode(new_video_data).decode()
                self.add_inline_data(encoded_data, new_filename, new_mimetype)
                
                # Update metadata to include transcoding info
                if not hasattr(self, "metadata"):
                    self.metadata = {}
                if not hasattr(self, "meta"):
                    self.meta = {}
                    
                self.metadata["video"] = metadata
                self.metadata["video"]["transcoded"] = {
                    "original_format": self.get_video_format_from_mimetype(),
                    "target_format": target_format,
                    "codec": codec,
                    "bit_rate": bit_rate,
                    "width": width,
                    "height": height,
                    "timestamp": datetime.now().isoformat()
                }
                self.meta["video"] = self.metadata["video"]
                
            elif self.is_external_data():
                # For external data, we'd typically need to upload the file somewhere
                # This is just a placeholder - in a real implementation you'd upload the file
                # to an external storage service and update the URL
                logger.warning("Transcoding external video data not fully implemented")
                
        except Exception as e:
            logger.error(f"Error transcoding video: {str(e)}")
            raise
            
        finally:
            # Clean up temporary files
            if temp_input and os.path.exists(temp_input.name):
                os.unlink(temp_input.name)
            if temp_output and os.path.exists(temp_output.name):
                os.unlink(temp_output.name)

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
