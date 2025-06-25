from sqlalchemy import create_engine, MetaData, Table, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extras import RealDictCursor

# Configure logging
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Class for secure database management with ORM, REF CURSOR, and NOTICE support"""
    def __init__(self):
        # Initialize database connection attributes
        self.engine = None  # SQLAlchemy engine for database connection
        self.session = None  # SQLAlchemy session for ORM operations
        self.metadata = None  # Metadata object to store database schema information
        self.inspector = None  # Inspector to retrieve schema details
        self.notices = []  # Store PostgreSQL NOTICE messages

    def _sanitize_value(self, value: Any) -> Any:
        """Convert NumPy types to native Python types"""
        # Purpose: Ensures values are compatible with database operations by converting NumPy types to native Python types
        # Handles None/empty strings and strips whitespace from strings
        if isinstance(value, np.generic):
            return value.item()  # Convert NumPy scalar to Python native type
        if value is None or value == "":
            return None  # Convert empty strings or None to database NULL
        if isinstance(value, str):
            return value.strip()  # Remove leading/trailing whitespace from strings
        return value

    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert all NumPy types in a dictionary to native Python types"""
        # Purpose: Applies _sanitize_value to all dictionary values to ensure database compatibility
        return {k: self._sanitize_value(v) for k, v in data.items()}

    def connect(self, connection_string: str) -> bool:
        """Connect to the database"""
        # Purpose: Establishes a database connection using SQLAlchemy, sets up metadata and session, and tests connectivity
        try:
            self.engine = create_engine(
                connection_string,
                pool_pre_ping=True,  # Check connection health before use
                pool_recycle=300,    # Recycle connections after 300 seconds to avoid timeouts
                echo=False           # Disable SQL query logging
            )

            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))  # Test connection with a simple query

            self.metadata = MetaData()  # Initialize metadata for schema reflection
            self.inspector = inspect(self.engine)  # Initialize inspector for schema details

            Session = sessionmaker(bind=self.engine)  # Create session factory
            self.session = Session()  # Create session for ORM operations

            logger.info("Successfully connected to the database")
            return True

        except Exception as e:
            logger.error(f"Error connecting to the database: {str(e)}")
            return False

    def get_table_names(self) -> List[str]:
        """Get list of all tables and views"""
        # Purpose: Retrieves all table and view names from the database for exploration or validation
        try:
            tables = self.inspector.get_table_names()  # Get all table names
            views = self.inspector.get_view_names()   # Get all view names
            return tables + views  # Combine tables and views into a single list
        except Exception as e:
            logger.error(f"Error retrieving table names and views: {str(e)}")
            return []

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get information about a table"""
        # Purpose: Fetches metadata (columns, primary keys, foreign keys) for a specific table
        try:
            columns = self.inspector.get_columns(table_name)  # Get column details
            primary_keys = self.inspector.get_pk_constraint(table_name)  # Get primary key info
            foreign_keys = self.inspector.get_foreign_keys(table_name)  # Get foreign key info

            return {
                'columns': columns,
                'primary_keys': primary_keys,
                'foreign_keys': foreign_keys
            }
        except Exception as e:
            logger.error(f"Error retrieving info for table {table_name}: {str(e)}")
            return {}

    def get_table_data(self, table_name: str, limit: int = 100) -> pd.DataFrame:
        """Get data from a table"""
        # Purpose: Retrieves up to `limit` rows from a table as a pandas DataFrame
        # Checks table existence to prevent SQL injection and errors
        if table_name not in self.get_table_names():
            logger.error(f"Table {table_name} does not exist")
            return pd.DataFrame()  # Return empty DataFrame if table doesn't exist

        try:
            query = text(f"SELECT * FROM {table_name} LIMIT :limit")  # Parameterized query for safety
            return pd.read_sql(query, self.engine, params={"limit": limit})  # Execute query and return DataFrame
        except Exception as e:
            logger.error(f"Error retrieving data from table {table_name}: {str(e)}")
            return pd.DataFrame()

    def insert_record(self, table_name: str, data: Dict[str, Any]) -> bool:
        """Insert a new record"""
        # Purpose: Inserts a new record into the specified table with sanitized data
        if table_name not in self.get_table_names():
            logger.error(f"Table {table_name} does not exist")
            return False
        try:
            data = self._sanitize_dict(data)  # Sanitize input data
            table = Table(table_name, self.metadata, autoload_with=self.engine)  # Reflect table schema
            insert_query = table.insert().values(**data)  # Build insert query

            with self.engine.connect() as conn:
                conn.execute(insert_query)  # Execute insert
                conn.commit()  # Commit transaction

            logger.info(f"Record successfully inserted into table {table_name}")
            return True

        except Exception as e:
            logger.error(f"Error inserting record into table {table_name}: {str(e)}")
            return False

    def update_record(self, table_name: str, record_id: Any, data: Dict[str, Any], id_column: str = 'id') -> bool:
        """Update a record"""
        # Purpose: Updates a record identified by `record_id` in the specified table
        if table_name not in self.get_table_names():
            logger.error(f"Table {table_name} does not exist")
            return False
        try:
            data = self._sanitize_dict(data)  # Sanitize input data
            record_id = self._sanitize_value(record_id)  # Sanitize record ID

            table = Table(table_name, self.metadata, autoload_with=self.engine)  # Reflect table schema
            update_query = table.update().where(
                getattr(table.c, id_column) == record_id
            ).values(**data)  # Build update query with condition

            with self.engine.connect() as conn:
                result = conn.execute(update_query)  # Execute update
                conn.commit()  # Commit transaction

                # Check if any rows were updated
                if result.rowcount > 0:
                    logger.info(f"Record successfully updated in table {table_name}")
                    return True
                else:
                    logger.warning(f"No record found to update in table {table_name}")
                    return False

        except Exception as e:
            logger.error(f"Error updating record in table {table_name}: {str(e)}")
            return False

    def delete_record(self, table_name: str, record_id: Any, id_column: str = 'id') -> bool:
        """Delete a record"""
        # Purpose: Deletes a record identified by `record_id` from the specified table
        if table_name not in self.get_table_names():
            logger.error(f"Table {table_name} does not exist")
            return False
        try:
            record_id = self._sanitize_value(record_id)  # Sanitize record ID

            table = Table(table_name, self.metadata, autoload_with=self.engine)  # Reflect table schema
            delete_query = table.delete().where(
                getattr(table.c, id_column) == record_id
            )  # Build delete query with condition

            with self.engine.connect() as conn:
                result = conn.execute(delete_query)  # Fixed: was update_query
                conn.commit()  # Commit transaction

                # Check if any rows were deleted
                if result.rowcount > 0:
                    logger.info(f"Record successfully deleted from table {table_name}")
                    return True
                else:
                    logger.warning(f"No record found to delete in table {table_name}")
                    return False

        except Exception as e:
            logger.error(f"Error deleting record in table {table_name}: {str(e)}")
            return False

    def get_routines(self) -> List[Dict[str, Any]]:
        """Get list of procedures and functions"""
        # Purpose: Fetches metadata about stored procedures and functions in the public schema
        # Excludes system routines and trigger-related functions
        try:
            query = text("""
                         SELECT routine_name, routine_type, specific_name
                         FROM information_schema.routines
                         WHERE routine_schema = 'public'
                           AND routine_type IN ('PROCEDURE', 'FUNCTION')
                           AND NOT routine_name LIKE 'postgres_%'
                           AND NOT routine_name LIKE 'check_%'
                           AND NOT routine_name LIKE 'log_changes'
                         ORDER BY routine_name
                         """)  # Query to get routines, filtering out system/trigger routines
            with self.engine.connect() as conn:
                result = pd.read_sql(query, self.engine)  # Execute query and return as DataFrame
                return result.to_dict('records')  # Convert to list of dictionaries
        except Exception as e:
            logger.error(f"Error retrieving routines: {str(e)}")
            return []

    def get_function_parameters(self, specific_name: str) -> List[Dict[str, Any]]:
        """Get parameters for a specific function, including their mode"""
        # Purpose: Retrieves parameter details (name, type, mode, position) for use in GUI or execution
        try:
            query = text("""
                         SELECT parameter_name, data_type, parameter_mode, ordinal_position
                         FROM information_schema.parameters
                         WHERE specific_name = :specific_name
                           AND specific_schema = 'public'
                           AND parameter_name IS NOT NULL
                         ORDER BY ordinal_position
                         """)  # Query to get parameter metadata
            with self.engine.connect() as conn:
                result = pd.read_sql(query, self.engine, params={"specific_name": specific_name})
                return result.to_dict('records')  # Convert to list of dictionaries
        except Exception as e:
            logger.error(f"Error retrieving parameters for function {specific_name}: {str(e)}")
            return []

    def _detect_refcursor_return(self, specific_name: str) -> bool:
        """Check if function returns REFCURSOR"""
        # Purpose: Checks if a function returns a REF CURSOR by examining OUT parameters
        # Importance: Enables automatic detection of REF CURSOR functions for proper handling in execute_routine
        try:
            with self.engine.connect() as conn:
                query = text("""
                             SELECT data_type
                             FROM information_schema.parameters
                             WHERE specific_name = :specific_name
                               AND parameter_mode = 'OUT'
                               AND data_type = 'refcursor'
                             """)  # Query to check for REF CURSOR in OUT parameters
                result = conn.execute(query, {"specific_name": specific_name})
                return result.fetchone() is not None  # True if REF CURSOR is found
        except Exception as e:
            logger.warning(f"Could not detect REFCURSOR return type: {e}")
            return False

    def _get_function_return_type(self, specific_name: str) -> Optional[str]:
        """Get the return type of a function"""
        # Purpose: Retrieves the return type of a function, handling standard and user-defined types
        try:
            with self.engine.connect() as conn:
                query = text("""
                             SELECT data_type, type_udt_name
                             FROM information_schema.routines
                             WHERE specific_name = :specific_name
                             """)  # Query to get return type
                result = conn.execute(query, {"specific_name": specific_name})
                row = result.mappings().fetchone()
                if row:
                    return row['data_type'] if row['data_type'] != 'USER-DEFINED' else row['type_udt_name']
        except Exception as e:
            logger.warning(f"Could not get function return type: {e}")
        return None

    def execute_routine(self, name: str, routine_type: str, specific_name: str,
                        params: List[Any] = None, refcursor_flag: bool = False) -> Tuple[pd.DataFrame, List[str]]:
        """
        Enhanced execution of PostgreSQL procedures and functions with NOTICE support and REF CURSOR handling.

        Supports:
        - PROCEDURE: CALL ...
        - FUNCTION: SELECT * FROM ... (for SETOF)
        - FUNCTION (REFCURSOR): SELECT ... AS refname → FETCH ALL IN <refname>
        - NOTICE message capture
        - Automatic REF CURSOR detection and handling

        Args:
            name: The routine name
            routine_type: 'PROCEDURE' or 'FUNCTION'
            specific_name: The specific routine identifier
            params: List of parameters to pass
            refcursor_flag: Explicit flag to indicate REF CURSOR expected

        Returns:
            Tuple[pd.DataFrame, List[str]]: (result_data, notice_messages)

        REF CURSOR Complexity:
        - REF CURSOR functions return a cursor object that must be fetched separately
        - Requires transaction management (BEGIN/COMMIT) to keep the cursor open
        - Uses psycopg2 for direct access to PostgreSQL's cursor and NOTICE features
        - Automatically detects REF CURSOR via _detect_refcursor_return or explicit flag
        - Fetches all rows from the cursor and closes it properly
        """
        self.notices = []  # Reset notices list

        try:
            params = params or []
            sanitized_params = [self._sanitize_value(p) for p in params]  # Sanitize input parameters

            # Check if this is a REF CURSOR function
            is_refcursor = refcursor_flag or self._detect_refcursor_return(specific_name)

            # Try SQLAlchemy for non-REF CURSOR routines (simpler cases)
            if not is_refcursor:
                try:
                    result_df = self._execute_routine_sqlalchemy(name, routine_type, specific_name, sanitized_params)
                    return result_df, []  # No notices captured with SQLAlchemy
                except Exception as sqlalchemy_error:
                    logger.info(f"SQLAlchemy execution failed, trying psycopg2: {sqlalchemy_error}")

            # Use psycopg2 for REF CURSOR or when SQLAlchemy fails
            return self._execute_routine_psycopg2(name, routine_type, specific_name, sanitized_params, is_refcursor)

        except Exception as e:
            logger.error(f"Error executing {routine_type} {name}: {str(e)}")
            return pd.DataFrame(), [f"Error: {str(e)}"]

    def _execute_routine_sqlalchemy(self, name: str, routine_type: str, specific_name: str, params: List[Any]) -> pd.DataFrame:
        """Execute routine using SQLAlchemy (for compatibility with simple cases)"""
        # Purpose: Handles procedures and non-REF CURSOR functions using SQLAlchemy
        # Does not support NOTICE capture or REF CURSOR
        param_dict = {f"param{i}": p for i, p in enumerate(params)}
        placeholders = ', '.join([f":param{i}" for i in range(len(params))])

        with self.engine.connect() as conn:
            with conn.begin():
                if routine_type.upper() == 'PROCEDURE':
                    query = text(f"CALL {name}({placeholders})")  # Execute procedure
                    conn.execute(query, param_dict)
                    return pd.DataFrame()  # Procedures typically don't return data

                elif routine_type.upper() == 'FUNCTION':
                    # Try as SETOF function (returns multiple rows)
                    try:
                        query = text(f"SELECT * FROM {name}({placeholders})")
                        result = conn.execute(query, param_dict)
                        rows = result.fetchall()
                        return pd.DataFrame(rows, columns=result.keys()) if rows else pd.DataFrame()
                    except Exception:
                        # Fallback to scalar function (returns single value)
                        query = text(f"SELECT {name}({placeholders}) AS result")
                        result = conn.execute(query, param_dict)
                        row = result.fetchone()
                        return pd.DataFrame([dict(row)]) if row else pd.DataFrame()

                else:
                    raise ValueError(f"Unsupported routine type: {routine_type}")

    def _execute_routine_psycopg2(self, name: str, routine_type: str, specific_name: str,
                                  sanitized_params: List[Any], is_refcursor: bool = False) -> Tuple[pd.DataFrame, List[str]]:
        """
        Execute routine using psycopg2 with NOTICE capture and REF CURSOR support.
        Purpose: Provides robust handling for procedures and functions, especially those returning REF CURSORs
        """
        # Create raw psycopg2 connection for advanced PostgreSQL features
        raw_conn = self.engine.raw_connection()
        raw_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        try:
            with raw_conn.cursor(cursor_factory=RealDictCursor) as cursor:
                if routine_type.upper() == 'PROCEDURE':
                    return self._execute_procedure_psycopg2(cursor, name, sanitized_params, raw_conn)
                else:
                    return self._execute_function_psycopg2(cursor, name, sanitized_params, is_refcursor, raw_conn)

        finally:
            raw_conn.close()

    def _execute_procedure_psycopg2(self, cursor, name: str, params: List[Any], raw_conn) -> Tuple[pd.DataFrame, List[str]]:
        """Execute a stored procedure"""
        # Purpose: Executes a stored procedure using psycopg2 and captures NOTICE messages
        param_placeholders = ', '.join(['%s'] * len(params))

        if params:
            query = f"CALL {name}({param_placeholders})"
            cursor.execute(query, params)
        else:
            query = f"CALL {name}()"
            cursor.execute(query)

        # Capture NOTICE messages from PostgreSQL
        notices = [notice.message.strip() for notice in raw_conn.notices if hasattr(notice, 'message')]
        return pd.DataFrame(), notices  # Procedures typically don't return data

    def _execute_function_psycopg2(self, cursor, name: str, params: List[Any],
                                   is_refcursor: bool, raw_conn) -> Tuple[pd.DataFrame, List[str]]:
        """Execute function with proper REF CURSOR handling"""
        # Purpose: Routes function execution to appropriate handler based on REF CURSOR status
        if is_refcursor:
            return self._execute_refcursor_function(cursor, name, params, raw_conn)
        else:
            return self._execute_regular_function(cursor, name, params, raw_conn)

    def _execute_refcursor_function(self, cursor, name: str, params: List[Any], raw_conn) -> Tuple[pd.DataFrame, List[str]]:
        """Execute a function that returns REF CURSOR and fetch its results"""
        # Purpose: Handles REF CURSOR functions by managing transactions, fetching results, and capturing notices
        # Complexity:
        # - Requires explicit transaction (BEGIN/COMMIT) to keep cursor open
        # - Retrieves dynamic cursor name and fetches all rows
        # - Properly closes cursor and handles errors
        try:
            cursor.execute("BEGIN")  # Start transaction for REF CURSOR

            # Call function to get cursor name
            param_placeholders = ', '.join(['%s'] * len(params))
            if params:
                query = f"SELECT {name}({param_placeholders}) AS cursor_name"
                cursor.execute(query, params)
            else:
                query = f"SELECT {name}() AS cursor_name"
                cursor.execute(query)

            result = cursor.fetchone()
            cursor_name = result['cursor_name']  # Get cursor name returned by function

            logger.info(f"REF CURSOR returned: {cursor_name}")

            # Fetch all rows from the cursor
            cursor.execute(f"FETCH ALL IN \"{cursor_name}\"")
            rows = cursor.fetchall()

            # Close the cursor and commit transaction
            cursor.execute(f"CLOSE \"{cursor_name}\"")
            cursor.execute("COMMIT")

            # Capture NOTICE messages
            notices = [notice.message.strip() for notice in raw_conn.notices if hasattr(notice, 'message')]

            # Convert results to DataFrame
            if rows:
                df = pd.DataFrame([dict(row) for row in rows])
                logger.info(f"REF CURSOR fetched {len(df)} rows with columns: {list(df.columns)}")
            else:
                df = pd.DataFrame()
                logger.info("REF CURSOR returned no data")

            return df, notices

        except Exception as e:
            cursor.execute("ROLLBACK")  # Rollback transaction on error
            logger.error(f"Error executing REF CURSOR function {name}: {str(e)}")
            raise

    def _execute_regular_function(self, cursor, name: str, params: List[Any], raw_conn) -> Tuple[pd.DataFrame, List[str]]:
        """Execute a regular function (SETOF or scalar)"""
        # Purpose: Handles non-REF CURSOR functions, attempting SETOF (multiple rows) or scalar (single value)
        param_placeholders = ', '.join(['%s'] * len(params))

        # Try as SETOF function first
        try:
            if params:
                query = f"SELECT * FROM {name}({param_placeholders})"
                cursor.execute(query, params)
            else:
                query = f"SELECT * FROM {name}()"
                cursor.execute(query)

            rows = cursor.fetchall()
            notices = [notice.message.strip() for notice in raw_conn.notices if hasattr(notice, 'message')]

            if rows:
                df = pd.DataFrame([dict(row) for row in rows])
            else:
                df = pd.DataFrame()

            return df, notices

        except Exception as setof_error:
            logger.info(f"SETOF execution failed, trying scalar: {setof_error}")

            # Try as scalar function
            try:
                if params:
                    query = f"SELECT {name}({param_placeholders}) AS result"
                    cursor.execute(query, params)
                else:
                    query = f"SELECT {name}() AS result"
                    cursor.execute(query)

                result = cursor.fetchone()
                notices = [notice.message.strip() for notice in raw_conn.notices if hasattr(notice, 'message')]

                df = pd.DataFrame([dict(result)]) if result else pd.DataFrame()
                return df, notices

            except Exception as scalar_error:
                logger.error(f"Both SETOF and scalar execution failed: {scalar_error}")
                raise

    def close(self):
        """Close the connection"""
        # Purpose: Properly closes the SQLAlchemy session and engine to free resources
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()