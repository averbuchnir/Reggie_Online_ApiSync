# ApiSync

**Author:** Nir Averbuch  
**Last updated:** 2025-11-04

A FastAPI application with WebSocket support for real-time payload monitoring. Includes a web-based frontend dashboard to visualize received payloads with metadata management capabilities.

## Features

- **REST API Endpoints**: HTTP endpoints for health checks and frontend serving
- **WebSocket Support**: Real-time bidirectional communication with payload broadcasting
- **BigQuery Integration**: Query Google Cloud BigQuery tables with authentication from `.env` file
- **Sensor Validation**: Automatic LLA validation against BigQuery metadata tables for each ping
- **Metadata Management**: View and edit sensor metadata with active/inactive experiment separation
- **Frontend Dashboard**: Interactive web interface to monitor WebSocket payloads with validation status
- **Connection Management**: Manages multiple WebSocket connections with broadcasting
- **Structured Logging**: Comprehensive logging with timestamps, operation tracking, and performance metrics
- **Duplicate Prevention**: Frontend prevents duplicate sensors by LLA with visual feedback
- **Visual Status Indicators**: Color-coded cards to distinguish active vs inactive experiments
- **Metadata Modal**: Clickable payload cards to view detailed sensor metadata with experiment history

## Project Structure

```
ApiSync/
├── src/
│   ├── main.py                    # Main FastAPI application
│   └── api/
│       ├── __init__.py
│       ├── get_endpoints.py      # GET endpoints (health, frontend)
│       ├── websocket_endpoints.py # WebSocket endpoints (ping)
│       └── bigquery_endpoints.py # BigQuery query endpoints
├── auth/
│   ├── .env                       # BigQuery credentials (not in git)
│   ├── bigquery_config.py        # BigQuery configuration and client setup
│   └── README.md                  # Auth setup documentation
├── frontend/
│   └── index.html                 # Web dashboard interface
├── test_script/
│   ├── README.md                  # Testing documentation
│   ├── 1.test_websocket.py        # Python WebSocket test script
│   ├── 2.test_bigquery.py         # Python BigQuery test script
│   └── output/                     # Test output files (CSV)
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Installation

1. **Clone or navigate to the project directory**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **For testing (optional):**
   ```bash
   pip install websockets requests pandas
   ```

4. **Configure BigQuery credentials:**
   - Create `auth/.env` file with your GCP credentials (see [BigQuery Configuration](#bigquery-configuration) section)

## Running the Application

### Start the FastAPI Server

```bash
python -m uvicorn src.main:app --reload
```

Or run directly:
```bash
python src/main.py
```

The server will start on `http://localhost:8000`

### Access Points

- **Frontend Dashboard**: `http://localhost:8000/`
- **Swagger UI**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **WebSocket Endpoint**: `ws://localhost:8000/ws/ping`
- **BigQuery Metadata**: `http://localhost:8000/GCP-BQ/metadata?dataset=<dataset>&table=<table>`
- **Active Metadata Query**: `http://localhost:8000/GCP-BQ/metadata/active?hostname=<hostname>&mac_address=<mac>&lla=<lla>`

## API Endpoints

### GET Endpoints

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

#### `GET /`
Serves the frontend HTML dashboard.

### BigQuery Endpoints

#### `GET /GCP-BQ/metadata`

Query a BigQuery metadata table.

**Query Parameters:**
- `dataset` (required): BigQuery dataset name (e.g., "f4d_test")
- `table` (required): Table name (e.g., "aaaaaaaaaaaa_metadata")
- `limit` (optional, default: 100): Maximum number of rows to return
- `offset` (optional, default: 0): Number of rows to skip

**Example:**
```
GET /GCP-BQ/metadata?dataset=f4d_test&table=aaaaaaaaaaaa_metadata&limit=50
```

**Response:**
```json
{
  "success": true,
  "project": "iucc-f4d",
  "dataset": "f4d_test",
  "table": "aaaaaaaaaaaa_metadata",
  "full_table": "iucc-f4d.f4d_test.aaaaaaaaaaaa_metadata",
  "limit": 50,
  "offset": 0,
  "count": 50,
  "data": [
    {
      // Row 1 data
    },
    {
      // Row 2 data
    }
  ]
}
```

**Notes:**
- Project ID is constant: `iucc-f4d`
- Dataset and table are specified as query parameters
- Returns JSON with paginated results

#### `GET /GCP-BQ/metadata/active`

Query metadata table for active or inactive experiments.

**Query Parameters:**
- `hostname` (required): Owner/hostname (e.g., "f4d_test")
- `mac_address` (required): MAC address (e.g., "aaaaaaaaaaaa")
- `lla` (optional): Specific LLA value to filter by sensor
- `experiment` (optional): Experiment identifier in format "Exp_ID_Exp_Name" (e.g., "1_Image_V2")
- `all` (optional, default: false): If true, return all metadata for the mac_address

**Example:**
```
GET /GCP-BQ/metadata/active?hostname=f4d_test&mac_address=aaaaaaaaaaaa&lla=fd002124b00ccf7399b
GET /GCP-BQ/metadata/active?hostname=f4d_test&mac_address=aaaaaaaaaaaa&experiment=1_Image_V2
GET /GCP-BQ/metadata/active?hostname=f4d_test&mac_address=aaaaaaaaaaaa&all=true
```

**Response:**
```json
{
  "success": true,
  "project": "iucc-f4d",
  "dataset": "f4d_test",
  "table": "aaaaaaaaaaaa_metadata",
  "full_table": "iucc-f4d.f4d_test.aaaaaaaaaaaa_metadata",
  "count": 7,
  "data": [
    {
      "Owner": "f4d_test",
      "Mac_Address": "aaaaaaaaaaaa",
      "Exp_ID": 1,
      "Exp_Name": "Image_V2",
      "Active_Exp": true,
      // ... other metadata fields
    }
  ]
}
```

**Notes:**
- Returns all metadata (both active and inactive) - filtering is done in frontend
- Constructs table name as: `{mac_address}_metadata`
- Uses `hostname` as the dataset name
- Supports filtering by LLA, experiment, or all sensors
- No `Active_Exp` filtering in backend - all data returned for frontend processing

### WebSocket Endpoints

#### `WebSocket /ws/ping`

Accepts WebSocket connections and handles ping payloads with automatic sensor validation.

**Request Payload:**
```json
{
  "hostname": "<string>",
  "mac_address": "<string>",
  "type": "<string>",
  "LLA": "<string>"
}
```

**Response:**
```json
{
  "received": true,
  "timestamp": "2024-01-15T10:30:45",
  "payload": {
    "hostname": "<string>",
    "mac_address": "<string>",
    "type": "<string>",
    "LLA": "<string>",
    "validation": {
      "is_valid": true,
      "message": "LLA found in metadata",
      "error": null
    }
  }
}
```

**Metadata Update (Planned):**

The WebSocket endpoint also supports metadata update messages (planned feature):

**Request Payload:**
```json
{
  "type": "metadata_update",
  "payload": {
    "hostname": "<string>",
    "mac_address": "<string>",
    "LLA": "<string>",
    "original_data": {...},
    "modified_fields": {
      "Label": "...",
      "Location": "...",
      "Coordinates_X": ...,
      ...
    }
  }
}
```

**Response:**
```json
{
  "status": "received",
  "message": "Metadata update received",
  "timestamp": "2024-01-15T10:30:45"
}
```

**Validation Logic:**
- Automatically validates each LLA against the BigQuery metadata table
- Constructs table name as: `{mac_address}_metadata`
- Uses `hostname` as the dataset name
- Queries: `{PROJECT_ID}.{hostname}.{mac_address}_metadata`
- Returns `is_valid: true` if LLA exists (count >= 1), `false` otherwise
- Handles historical records (multiple matches are valid)

**Features:**
- Broadcasts received payloads to all connected clients
- Manages multiple concurrent WebSocket connections
- Automatic cleanup of disconnected clients
- Real-time sensor validation against BigQuery metadata
- Comprehensive logging with operation timestamps and durations

## Frontend Dashboard

The frontend dashboard (`http://localhost:8000/`) provides:

1. **Connection Status**: Visual indicator and Connect/Disconnect buttons
2. **Health Check Component**: Test the `/health` endpoint with visual feedback
3. **Payload Monitor**: Real-time display of up to 10 sensors
   - Grid layout: 5 sensors per row, 2 rows maximum (oldest to newest, left to right, top to bottom)
   - **Filtering Logic**: Shows sensors only if:
     - Validation is `true` (valid sensors found in metadata)
     - OR validation message contains "LLA not found in metadata"
   - **Duplicate Prevention**: Automatically prevents duplicate sensors by LLA
   - **Validation Status**: Visual indicators showing validation results (✓ Valid / ✗ Invalid)
   - **Blink Animation**: Valid sensors blink once when they ping with configurable duration and color
   - **Color Customization**: Color picker to customize blink color for valid sensors
   - **Duration Control**: Number input to control blink duration (0.5s to 5s, default: 1.5s)
   - Clear Payloads button to reset the display
   - Automatic updates when payloads are received

4. **Metadata Modal**: Clickable payload cards to view detailed sensor metadata
   - Click any payload card to open a modal with sensor metadata
   - **Active Experiments**: Shows current state with green theme
     - Displays all active experiments directly
     - Green color scheme throughout (header, sections, borders)
     - "CURRENT STATE" banner with checkmark icon
   - **Inactive Experiments**: Shows history with gray theme
     - Dropdown selector to choose from historical experiments
     - Experiments sorted by `Exp_ID_Exp_Name` format
     - Gray color scheme throughout (header, sections, borders)
     - "HISTORY" banner with scroll icon
     - Auto-selects first experiment when opened
   - **Metadata Display**: Structured view of experiment and sensor details
     - Experiment information (ID, Name, Location, dates)
     - Sensor details (Label, Location, Coordinates, Frequency, etc.)
     - Status indicators (Active/Inactive, Valid/Invalid)
     - Last Seen timestamps, Label Options, Alerts
   - **Empty States**: Handles "No metadata yet" and "No active experiments"
   - Modal can be closed by clicking outside, pressing ESC, or clicking X button

5. **Visual Status Indicators**: Color-coded payload cards
   - **Active Experiments**: Green gradient background, green left border, green shadow
     - Automatically updates when metadata is fetched
   - **Inactive Experiments**: Gray gradient background, gray left border, gray shadow
     - Status determined when clicking to view metadata
   - **Invalid Sensors**: Red validation section (failed validation)

6. **Error/Debug Dashboard**: Separate section for validation errors
   - Displays validation errors for sensors that don't meet display criteria
   - Shows error message and details from `validation.message` and `validation.error`
   - Displays LLA, MAC Address, and Hostname for each error
   - Keeps last 20 errors (newest on top)
   - Clear Errors button to reset the error list
   - Shows "No errors yet" when empty

### Frontend Features Details

- **Sensor Tracking**: Each sensor is tracked by its LLA value
- **Duplicate Handling**: 
  - If a sensor with the same LLA already exists, a new component is not created
  - If the existing sensor receives a valid ping (`is_valid: true`), it triggers a blink animation
  - Timestamp is updated on the existing sensor component
- **Display Filtering**: 
  - Only displays sensors in "Received Payloads" if validation is valid OR LLA not found in metadata
  - Other errors (table not found, BigQuery errors, etc.) appear in "Error/Debug" dashboard
- **Validation Display**: 
  - Green checkmark (✓) and message for valid sensors
  - Red X (✗) and message for invalid sensors
  - Error messages displayed if validation fails
- **Blink Animation**: 
  - Blinks once per valid ping (instead of multiple times)
  - Configurable duration: 0.5s to 5s (default: 1.5s)
  - Configurable color via color picker (default: green `#10b981`)
  - Uses CSS variables for real-time updates
- **Error/Debug Dashboard**:
  - Shows validation errors that don't meet display criteria
  - Displays full error details including message and error field
  - Tracks sensor information (LLA, MAC, Hostname) for debugging
- **Metadata Modal**:
  - Click any payload card to view detailed metadata
  - Automatically filters for `Active_Exp = True` when displaying active experiments
  - Shows experiment history with dropdown for inactive experiments
  - Groups metadata by experiment (`Exp_ID_Exp_Name`)
  - Displays formatted dates and structured information
  - Visual separation between active (green) and inactive (gray) experiments
- **Visual Status Indicators**:
  - Payload cards automatically update with visual styling after metadata fetch
  - Green theme for sensors with active experiments
  - Gray theme for sensors with only inactive/historical experiments
  - Visual distinction through background colors, borders, and shadows
  - Hover effects match the card's status theme
- **Editable Metadata (Planned)**:
  - Inactive experiment metadata will be editable (all fields except Frequency, LLA, RFID)
  - "Save Changes" button per sensor to send updates via WebSocket
  - Updates will be sent to backend for processing (planned feature)

## Testing

### Using the Test Scripts

See `test_script/README.md` for detailed testing instructions.

#### Quick Test Commands

**Health Check (curl):**
```bash
curl http://localhost:8000/health
```

**WebSocket Test (Python):**
```bash
python test_script/1.test_websocket.py
```

**BigQuery Test (Python):**
```bash
python test_script/2.test_bigquery.py -d f4d_test -t aaaaaaaaaaaa_metadata
```

### Manual Testing

1. Open `http://localhost:8000/` in your browser
2. Click "Connect" to establish WebSocket connection
3. Click "Check Health" to test the health endpoint
4. Send payloads using test scripts or other WebSocket clients
5. Watch payloads appear in real-time on the dashboard

## BigQuery Configuration

### Setup

1. **Create `auth/.env` file** with your Google Cloud credentials:

```env
# Required
GCP_PROJECT_ID=
GCP_CLIENT_EMAIL=
GCP_PRIVATE_KEY=
# Optional but recommended
GCP_AUTH_URI=
GCP_CLIENT_ID=
GCP_PRIVATE_KEY_ID=
GCP_CLIENT_X509_CERT_URL=
```

2. **Private Key Format**: In your `.env` file, replace actual newlines in the private key with `\\n`. The code will automatically convert them back.

### Configuration Options

The code supports three ways to provide credentials (in priority order):

1. **Individual `.env` variables** (recommended): Set `GCP_*` variables as shown above
2. **`CREDENTIALS_JSON`**: Full JSON credentials as a string in `.env`
3. **`CREDENTIALS_PATH`**: Path to a JSON credentials file

### Security

**Never commit your `.env` file or credentials to version control!**

The `.gitignore` file already excludes:
- `auth/.env`
- `auth/*.json`
- Credential files

## Development

### Project Structure Details

- **`src/main.py`**: FastAPI app initialization, middleware setup, router registration, and logging configuration
- **`src/api/get_endpoints.py`**: HTTP GET endpoints using FastAPI router
- **`src/api/websocket_endpoints.py`**: WebSocket endpoints, connection manager, and payload processing with validation integration
- **`src/api/bigquery_endpoints.py`**: BigQuery query endpoints and sensor validation functions
- **`auth/bigquery_config.py`**: BigQuery client configuration and credential loading
- **`frontend/index.html`**: Single-page web application with WebSocket client, validation display, and duplicate prevention

### Adding New Endpoints

**Adding GET Endpoints:**
Add routes to `src/api/get_endpoints.py`:
```python
@router.get("/your-endpoint")
async def your_function():
    return {"message": "Hello"}
```

**Adding WebSocket Endpoints:**
Add functions to `src/api/websocket_endpoints.py` and register in `src/main.py`:
```python
app.websocket("/ws/your-endpoint")(your_websocket_function)
```

**Adding BigQuery Endpoints:**
Add routes to `src/api/bigquery_endpoints.py`:
```python
@router.get("/GCP-BQ/your-endpoint")
async def your_bigquery_function(dataset: str, table: str):
    client = get_client()
    # Your BigQuery query logic
```

**Adding WebSocket Message Types:**
Modify `src/api/websocket_endpoints.py` to handle different message types:
```python
# In websocket_ping function, check payload type
if data.get("type") == "metadata_update":
    # Handle metadata update
    # Return acknowledgment
elif data.get("type") == "ping":
    # Handle ping payload
```

## Dependencies

- **FastAPI**: Web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **google-cloud-bigquery**: Google Cloud BigQuery client library
- **python-dotenv**: Environment variable management from .env files
- **Python 3.10+**: Required Python version

See `requirements.txt` for exact versions.

## Logging

The application uses structured logging with timestamps and operation tracking:

- **Log Format**: `YYYY-MM-DD HH:MM:SS | LEVEL | MODULE | [OPERATION] Message | Details`
- **Operation Tracking**: Each operation logs start/end with duration metrics
- **Log Levels**: INFO (operations), DEBUG (detailed), ERROR (failures), WARNING (issues)
- **Log Prefixes**:
  - `[WEBSOCKET_CONNECT]` - Client connections
  - `[WEBSOCKET_DISCONNECT]` - Client disconnections
  - `[WEBSOCKET_PING]` - Payload processing and validation
  - `[BROADCAST]` - Message broadcasting
  - `[VALIDATE_SENSOR_LLA]` - BigQuery validation operations
  - `[QUERY_ACTIVE_METADATA]` - Metadata query operations
  - `[METADATA_UPDATE]` - Metadata update processing (planned)

Example log output:
```
2025-01-15 10:30:45 | INFO     | src.api.websocket_endpoints | [WEBSOCKET_PING] Payload received | Type: Ping | Hostname: f4d_test | MAC: aaaaaaaaaaaa | LLA: fd002124b0021f9fecc | Receive time: 0.001s
2025-01-15 10:30:45 | INFO     | src.api.bigquery_endpoints | [VALIDATE_SENSOR_LLA] Starting validation | Hostname: f4d_test | MAC: aaaaaaaaaaaa | LLA: fd002124b0021f9fecc
2025-01-15 10:30:46 | INFO     | src.api.bigquery_endpoints | [VALIDATE_SENSOR_LLA] Validation successful | Count: 1 | Query duration: 0.234s | Total duration: 0.235s
2025-01-15 10:30:46 | INFO     | src.api.websocket_endpoints | [WEBSOCKET_PING] Validation completed | Result: VALID | Message: LLA found in metadata | Duration: 0.235s
```

## System Architecture

### System Architecture Scheme

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐         ┌──────────────┐                      │
│  │  WebSocket   │         │   HTTP GET   │                      │
│  │   Client     │         │   Requests   │                      │
│  └──────┬───────┘         └──────┬───────┘                      │
│         │                        │                               │
└─────────┼────────────────────────┼───────────────────────────────┘
          │                        │
          │                        │
┌─────────▼────────────────────────▼───────────────────────────────┐
│                    FASTAPI SERVER (Port 8000)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  CORS Middleware (Allows cross-origin requests)          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Router: get_endpoints.py                                │  │
│  │  ├── GET /health                                          │  │
│  │  └── GET /  (Frontend HTML)                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Router: bigquery_endpoints.py                           │  │
│  │  ├── GET /GCP-BQ/metadata                                │  │
│  │  └── GET /GCP-BQ/metadata/active                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  WebSocket: websocket_endpoints.py                       │  │
│  │  └── WebSocket /ws/ping                                  │  │
│  │      ├── ConnectionManager                               │  │
│  │      ├── Receive payloads                                │  │
│  │      ├── Validate LLA (via bigquery_endpoints)          │  │
│  │      └── Broadcast to all clients                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────┬─────────────────────────────────────────────────────────┘
          │
          │
┌─────────▼─────────────────────────────────────────────────────────┐
│                    BIGQUERY INTEGRATION                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  auth/bigquery_config.py                                │  │
│  │  ├── Load credentials from auth/.env                     │  │
│  │  ├── Create BigQuery client                              │  │
│  │  └── Authenticate with GCP Service Account               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  BigQuery Functions:                                     │  │
│  │  ├── validate_sensor_lla()                              │  │
│  │  │   └── Query: {PROJECT}.{hostname}.{mac}_metadata    │  │
│  │  │       WHERE LLA = @lla                                │  │
│  │  │                                                       │  │
│  │  └── query_active_metadata()                            │  │
│  │      └── Query: {PROJECT}.{hostname}.{mac}_metadata    │  │
│  │          WHERE LLA = @lla (optional)                     │  │
│  │          Returns ALL metadata (frontend filters)          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────┬─────────────────────────────────────────────────────────┘
          │
          │
┌─────────▼─────────────────────────────────────────────────────────┐
│              GOOGLE CLOUD BIGQUERY                                │
│                                                                   │
│  Project: iucc-f4d                                                │
│  Dataset: {hostname} (e.g., "f4d_test")                          │
│  Table: {mac_address}_metadata (e.g., "aaaaaaaaaaaa_metadata")   │
│                                                                   │
│  Schema:                                                          │
│  ├── Owner, Mac_Address, Exp_ID, Exp_Name                       │
│  ├── LLA, Label, Location, Frequency                            │
│  ├── Coordinates_X, Coordinates_Y, Coordinates_Z                │
│  ├── Active_Exp (boolean)                                       │
│  ├── Exp_Started_At, Exp_Ended_At                              │
│  └── ... (other metadata fields)                                │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### a) WebSocket Ping Flow

```
Sensor Device
    │
    │ Sends: {hostname, mac_address, type, LLA}
    ▼
WebSocket /ws/ping
    │
    ├─► Validate LLA (BigQuery)
    │   │
    │   └─► Query: COUNT(*) WHERE LLA = @lla
    │       │
    │       └─► Return: is_valid (true/false)
    │
    ├─► Create Response with validation
    │
    └─► Broadcast to ALL connected clients
        │
        └─► Frontend receives & displays
```

**Steps:**
1. Sensor sends ping payload via WebSocket
2. Backend receives payload and extracts LLA
3. Backend queries BigQuery to validate LLA exists
4. Backend creates response with validation result
5. Backend broadcasts response to all connected clients
6. Frontend receives broadcast and displays payload card

### b) Metadata Query Flow

```
Frontend (User clicks payload card)
    │
    │ GET /GCP-BQ/metadata/active?hostname=X&mac=Y&lla=Z
    ▼
Backend Endpoint
    │
    ├─► Query BigQuery: SELECT * WHERE LLA = @lla
    │   │
    │   └─► Returns ALL metadata (active + inactive)
    │
    └─► Return JSON response
        │
        ▼
Frontend Processing
    │
    ├─► Filter: Active_Exp = True  → Show active experiments
    │   └─► Green theme, direct display
    │
    └─► Filter: Active_Exp = False → Show inactive experiments
        └─► Gray theme, dropdown selector
```

**Steps:**
1. User clicks on a payload card in the frontend
2. Frontend sends HTTP GET request to `/GCP-BQ/metadata/active`
3. Backend queries BigQuery for all metadata matching the LLA
4. Backend returns all metadata (both active and inactive)
5. Frontend filters results:
   - If `Active_Exp = True` entries exist → Display active experiments (green theme)
   - If only `Active_Exp = False` entries exist → Display inactive experiments (gray theme, dropdown)
6. Frontend updates payload card visual status (green/gray styling)
7. Frontend displays metadata in modal

### c) Frontend Display Logic

```
WebSocket Payload Received
    │
    ├─► Check validation.is_valid
    │   │
    │   ├─► TRUE  → Display in "Received Payloads"
    │   │   │       └─► Green validation section
    │   │   │           └─► Clickable → Fetch metadata
    │   │   │
    │   └─► FALSE → Check message
    │       │
    │       ├─► "LLA not found" → Display in "Received Payloads"
    │       │                    └─► Red validation section
    │       │
    │       └─► Other error → Display in "Error/Debug"
    │
    └─► Check for duplicates (by LLA)
        │
        ├─► New LLA → Create new card
        │
        └─► Existing LLA → Update timestamp, trigger blink
```

**Steps:**
1. Frontend receives WebSocket payload with validation result
2. Check if `validation.is_valid === true`:
   - **TRUE**: Display in "Received Payloads" section with green validation
   - **FALSE**: Check validation message:
     - If message contains "LLA not found" → Display in "Received Payloads" with red validation
     - Otherwise → Display in "Error/Debug" section
3. Check if LLA already exists in displayed payloads:
   - **New LLA**: Create new payload card
   - **Existing LLA**: Update timestamp and trigger blink animation (if valid)
4. If payload count exceeds 10, remove oldest payloads
5. When user clicks card, fetch and display metadata

**Visual Status Update:**
- After metadata is fetched, payload card updates:
  - If active experiments found → Green card (green gradient background, green border, green shadow)
  - If only inactive experiments found → Gray card (gray gradient background, gray border, gray shadow)

## Notes

- WebSocket payloads are broadcast to all connected clients simultaneously
- The frontend displays up to 10 unique sensors (prevented by LLA)
- Duplicate sensors trigger blink animation if validation passes
- Timestamps are in ISO 8601 format without milliseconds
- All endpoints support CORS for cross-origin requests
- BigQuery queries use project ID `iucc-f4d` by default (configured in `.env`)
- BigQuery credentials are loaded from `auth/.env` file at startup
- Sensor validation queries the table: `{PROJECT_ID}.{hostname}.{mac_address}_metadata`
- All operations are logged with timestamps and duration metrics for performance monitoring
- Metadata queries return all data (active and inactive) - filtering done in frontend
- Active/Inactive experiment separation is visual only - all metadata is available for both
- Payload cards automatically update visual status after metadata is fetched
- Modal can display multiple experiments if sensor participated in several
- Experiment sorting uses `Exp_ID_Exp_Name` format for consistent ordering

## Planned Features

### Metadata Editing (In Development)
- Editable fields for inactive experiments (all fields except Frequency, LLA, RFID)
- "Save Changes" button per sensor to send updates
- WebSocket integration for sending modified metadata to backend
- Backend will receive and log metadata updates (no BigQuery writes yet)

### CSV Export (Planned)
- Download button for sensors with `Active_Exp = False`
- CSV format: one row per sensor with all metadata fields
- Bulk update capability for multiple sensors

## License

[Add your license information here]

