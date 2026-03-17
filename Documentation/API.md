#  API Reference (Beta)

Currently, the primary interaction logic runs through Flask endpoints generating files synchronously.

## Endpoint: /create (POST)
Initializes user logic into the \user_uploads\ root namespace triggering the daemon correctly.

### Request Input Layout (Multi-part Form)
| Parameter | Type | Importance | Description |
| --------- | ---- | ---------- | ----------- |
| \	ext\ | \string\ | **Required** | The explicit script mapped directly matching ElevenLabs API constraints. |
| \images[]\ | \ile list\ | **Required** | Batch Array uploading visual states cleanly defining visual layout paths. |
| \music_volume\ | \int\ (1-100) | Optional | Maps variables passed natively onto side-chain compressing \mix\ FFmpeg nodes. Default is \50\. |
| \spect_ratio\ | \string\ | Optional | Forces mapping bounds. Resolves exactly towards \9:16\ or \16:9\. Target formats automatically pad visuals mapping output correctly. |

### Output Generation Target Map
Once logically processed, endpoints DO NOT serve the MP4 explicitly. The daemon parses output dynamically tracking folder \UUID\ strings mapping standard resolution endpoints natively resolving logic across \/static/reels/UUID.mp4\.
