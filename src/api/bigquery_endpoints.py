"""
BigQuery GET endpoints for querying tables.
"""
from fastapi import APIRouter, HTTPException
from google.cloud import bigquery
from google.cloud.exceptions import GoogleCloudError
from google.api_core.exceptions import NotFound
import sys
import logging
import time
from pathlib import Path

# Add project root to path to import auth module
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from auth.bigquery_config import get_client

# Set up logger
logger = logging.getLogger(__name__)

router = APIRouter()

# Constant project ID
PROJECT_ID = "iucc-f4d"


async def validate_sensor_lla(hostname: str, mac_address: str, LLA: str) -> dict:
    """
    Validate if LLA exists in metadata table for the given hostname and MAC address.
    
    Args:
        hostname: Owner/hostname (e.g., "f4d_test")
        mac_address: MAC address (e.g., "aaaaaaaaaaaa")
        LLA: LLA value to validate (e.g., "fd002124b00ccf7399b")
    
    Returns:
        dict: Validation result with keys:
            - is_valid (bool): True if LLA found (count >= 1), False otherwise
            - message (str): Human-readable message
            - error (str or None): Error message if validation failed
    """
    operation_start = time.time()
    logger.info(
        f"[VALIDATE_SENSOR_LLA] Starting validation | "
        f"Hostname: {hostname} | "
        f"MAC: {mac_address} | "
        f"LLA: {LLA}"
    )
    
    # Construct table name: {mac_address}_metadata
    table_name = f"{mac_address}_metadata"
    
    # Construct dataset: use hostname
    dataset = hostname
    
    # Construct full table identifier: project.dataset.table
    full_table_name = f"{PROJECT_ID}.{dataset}.{table_name}"
    
    try:
        # Get client
        client_start = time.time()
        client = get_client()
        client_duration = time.time() - client_start
        logger.debug(f"[VALIDATE_SENSOR_LLA] Client obtained | Duration: {client_duration:.3f}s")
        
        logger.info(
            f"[VALIDATE_SENSOR_LLA] Querying metadata table | "
            f"Table: {full_table_name}"
        )
        
        # Construct query - use parameterized query to prevent SQL injection
        query = """
        SELECT COUNT(*) as count
        FROM `{full_table_name}`
        WHERE Owner = @hostname
          AND Mac_Address = @mac_address
          AND LLA = @LLA
        """.format(full_table_name=full_table_name)
        
        # Use query parameters for safety
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("hostname", "STRING", hostname),
                bigquery.ScalarQueryParameter("mac_address", "STRING", mac_address),
                bigquery.ScalarQueryParameter("LLA", "STRING", LLA),
            ]
        )
        
        # Execute query
        query_start = time.time()
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        query_duration = time.time() - query_start
        
        # Get count
        row = next(results)
        count = row.count
        
        total_duration = time.time() - operation_start
        
        if count >= 1:
            # LLA found in metadata (may exist in multiple historical records)
            result_message = f"LLA found in metadata (exists in {count} record(s))" if count > 1 else "LLA found in metadata"
            logger.info(
                f"[VALIDATE_SENSOR_LLA] Validation successful | "
                f"Count: {count} | "
                f"Query duration: {query_duration:.3f}s | "
                f"Total duration: {total_duration:.3f}s"
            )
            return {
                "is_valid": True,
                "message": result_message,
                "error": None
            }
        else:
            # LLA not found
            logger.info(
                f"[VALIDATE_SENSOR_LLA] Validation failed - LLA not found | "
                f"Count: {count} | "
                f"Query duration: {query_duration:.3f}s | "
                f"Total duration: {total_duration:.3f}s"
            )
            return {
                "is_valid": False,
                "message": "LLA not found in metadata",
                "error": None
            }
    
    except NotFound as e:
        # Table not found - this is a valid case (table doesn't exist for this MAC address)
        error_msg = f"Metadata table not found: {full_table_name}"
        total_duration = time.time() - operation_start
        logger.warning(
            f"[VALIDATE_SENSOR_LLA] Table not found | "
            f"Table: {full_table_name} | "
            f"Hostname: {hostname} | "
            f"MAC: {mac_address} | "
            f"Duration: {total_duration:.3f}s"
        )
        return {
            "is_valid": False,
            "message": f"Metadata table not found for MAC address: {mac_address}",
            "error": error_msg
        }
    except GoogleCloudError as e:
        error_msg = f"BigQuery error: {str(e)}"
        total_duration = time.time() - operation_start
        logger.error(
            f"[VALIDATE_SENSOR_LLA] BigQuery error | "
            f"Error: {error_msg} | "
            f"Duration: {total_duration:.3f}s",
            exc_info=True
        )
        return {
            "is_valid": False,
            "message": "Validation failed",
            "error": error_msg
        }
    except Exception as e:
        error_msg = f"Error validating LLA: {str(e)}"
        total_duration = time.time() - operation_start
        logger.error(
            f"[VALIDATE_SENSOR_LLA] Unexpected error | "
            f"Error: {error_msg} | "
            f"Duration: {total_duration:.3f}s",
            exc_info=True
        )
        return {
            "is_valid": False,
            "message": "Validation failed",
            "error": error_msg
        }


@router.get("/GCP-BQ/metadata")
async def query_metadata_table(
    dataset: str,
    table: str,
    limit: int = 100,
    offset: int = 0
):
    """
    Query a metadata table from BigQuery.
    
    Args:
        dataset: BigQuery dataset name (e.g., "f4d_test")
        table: Table name (e.g., "aaaaaaaaaaaa_metadata")
        limit: Maximum number of rows to return (default: 100)
        offset: Number of rows to skip (default: 0)
    
    Returns:
        dict: Query results with metadata in JSON format
    
    Example:
        GET /bq/metadata?dataset=f4d_test&table=aaaaaaaaaaaa_metadata&limit=50
    """
    try:
        client = get_client()
        
        # Construct full table identifier: project.dataset.table
        full_table_name = f"{PROJECT_ID}.{dataset}.{table}"
        print(f"Full table name: {full_table_name}")
        
        # Construct query
        query = f"""
        SELECT *
        FROM `{full_table_name}`
        LIMIT {limit}
        OFFSET {offset}
        """
        
        # Execute query
        query_job = client.query(query)
        results = query_job.result()
        
        # Convert results to list of dictionaries
        rows = []
        for row in results:
            rows.append(dict(row))
        
        return {
            "success": True,
            "project": PROJECT_ID,
            "dataset": dataset,
            "table": table,
            "full_table": full_table_name,
            "limit": limit,
            "offset": offset,
            "count": len(rows),
            "data": rows
        }
    
    except GoogleCloudError as e:
        raise HTTPException(status_code=500, detail=f"BigQuery error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying table: {str(e)}")


@router.get("/GCP-BQ/metadata/active")
async def query_active_metadata(
    hostname: str,
    mac_address: str,
    lla: str = None,
    experiment: str = None,
    all: bool = False
):
    """
    Query metadata table for active experiments.
    
    Args:
        hostname: Owner/hostname (e.g., "f4d_test")
        mac_address: MAC address (e.g., "aaaaaaaaaaaa")
        lla: Optional LLA value to filter by specific sensor
        experiment: Optional experiment identifier in format "Exp_ID_Exp_Name" (e.g., "1_Image_V2")
        all: If True, return all metadata for the mac_address (ignores lla and experiment)
    
    Returns:
        dict: Query results with metadata in JSON format (all metadata, not filtered by Active_Exp)
    
    Example:
        GET /GCP-BQ/metadata/active?hostname=f4d_test&mac_address=aaaaaaaaaaaa&lla=fd002124b00ccf7399b
        GET /GCP-BQ/metadata/active?hostname=f4d_test&mac_address=aaaaaaaaaaaa&experiment=1_Image_V2
        GET /GCP-BQ/metadata/active?hostname=f4d_test&mac_address=aaaaaaaaaaaa&all=true
    """
    operation_start = time.time()
    logger.info(
        f"[QUERY_ACTIVE_METADATA] Starting query | "
        f"Hostname: {hostname} | "
        f"MAC: {mac_address} | "
        f"LLA: {lla} | "
        f"Experiment: {experiment} | "
        f"All: {all}"
    )
    
    # Construct table name: {mac_address}_metadata
    table_name = f"{mac_address}_metadata"
    
    # Construct dataset: use hostname
    dataset = hostname
    
    # Construct full table identifier: project.dataset.table
    full_table_name = f"{PROJECT_ID}.{dataset}.{table_name}"
    
    try:
        # Get client
        client = get_client()
        
        # Build query conditions
        conditions = [
            "Owner = @hostname",
            "Mac_Address = @mac_address"
        ]
        
        # Build query parameters
        query_parameters = [
            bigquery.ScalarQueryParameter("hostname", "STRING", hostname),
            bigquery.ScalarQueryParameter("mac_address", "STRING", mac_address),
        ]
        
        # Add LLA filter if provided and not querying all
        if lla and not all:
            conditions.append("LLA = @lla")
            query_parameters.append(bigquery.ScalarQueryParameter("lla", "STRING", lla))
        
        # Add experiment filter if provided and not querying all
        if experiment and not all:
            # Parse experiment format: "Exp_ID_Exp_Name"
            try:
                parts = experiment.split("_", 1)
                if len(parts) == 2:
                    exp_id_str, exp_name = parts
                    exp_id = int(exp_id_str)
                    conditions.append("Exp_ID = @exp_id AND Exp_Name = @exp_name")
                    query_parameters.append(bigquery.ScalarQueryParameter("exp_id", "INT64", exp_id))
                    query_parameters.append(bigquery.ScalarQueryParameter("exp_name", "STRING", exp_name))
                else:
                    logger.warning(f"[QUERY_ACTIVE_METADATA] Invalid experiment format: {experiment}")
            except ValueError as e:
                logger.warning(f"[QUERY_ACTIVE_METADATA] Error parsing experiment ID: {e}")
        
        # Construct query - return all metadata (no Active_Exp filtering in backend)
        where_clause = " AND ".join(conditions)
        query = f"""
        SELECT *
        FROM `{full_table_name}`
        WHERE {where_clause}
        ORDER BY Exp_ID, Exp_Name, LLA
        """
        
        # Use query parameters for safety
        job_config = bigquery.QueryJobConfig(
            query_parameters=query_parameters
        )
        
        # Execute query
        query_start = time.time()
        query_job = client.query(query, job_config=job_config)
        results = query_job.result()
        query_duration = time.time() - query_start
        
        # Convert results to list of dictionaries
        rows = []
        for row in results:
            rows.append(dict(row))
        
        total_duration = time.time() - operation_start
        
        logger.info(
            f"[QUERY_ACTIVE_METADATA] Query completed | "
            f"Count: {len(rows)} | "
            f"Query duration: {query_duration:.3f}s | "
            f"Total duration: {total_duration:.3f}s"
        )
        
        return {
            "success": True,
            "project": PROJECT_ID,
            "dataset": dataset,
            "table": table_name,
            "full_table": full_table_name,
            "count": len(rows),
            "data": rows
        }
    
    except NotFound as e:
        error_msg = f"Metadata table not found: {full_table_name}"
        total_duration = time.time() - operation_start
        logger.warning(
            f"[QUERY_ACTIVE_METADATA] Table not found | "
            f"Table: {full_table_name} | "
            f"Duration: {total_duration:.3f}s"
        )
        raise HTTPException(status_code=404, detail=error_msg)
    
    except GoogleCloudError as e:
        error_msg = f"BigQuery error: {str(e)}"
        total_duration = time.time() - operation_start
        logger.error(
            f"[QUERY_ACTIVE_METADATA] BigQuery error | "
            f"Error: {error_msg} | "
            f"Duration: {total_duration:.3f}s",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=error_msg)
    
    except Exception as e:
        error_msg = f"Error querying metadata: {str(e)}"
        total_duration = time.time() - operation_start
        logger.error(
            f"[QUERY_ACTIVE_METADATA] Unexpected error | "
            f"Error: {error_msg} | "
            f"Duration: {total_duration:.3f}s",
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=error_msg)