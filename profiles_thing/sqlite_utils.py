"""
Basic Sqlite operations
"""
import os
import sqlite3
import time
from collections.abc import Iterator
from contextlib import closing
from typing import Any, Callable, Optional

from retry import retry


def close_and_ignore_errors(value: Any) -> None:
    """
    Safely close and ignore errors. Useful in __del__ directory
    error handling is meaningless.
    """
    if value:
        # pylint: disable=broad-except,bare-except
        # noinspection PyBroadException
        try:
            value.close()
        except BaseException:  # noqa # nosec
            pass


VERBOSE = False


@retry(Exception, tries=25, delay=1)
def open_database(file_name: str, check_same_thread: bool) -> sqlite3.Connection:
    """
    Try to re-open just in case it is transiently locked.
    """
    file_name = file_name.replace("\\", "/")
    file_name = os.path.abspath(file_name)
    return sqlite3.connect(
        file_name,
        check_same_thread=check_same_thread,
    )


class ConnectionManager:
    """
    Domain-free sqlite boilerplate, error handling, connection, transaction management
    """

    # pylint: disable=redefined-builtin
    # noinspection PyShadowingBuiltins
    def __init__(
        self,
        file_name: str,
        commit_every: int,
        bulk_insert_mode: bool = True,
        read_only: bool = False,
        print_this: Callable[[str], None] = print,
    ) -> None:
        """Create connection"""
        self.read_only = read_only
        self.file_name = file_name
        self.is_new_db = not os.path.exists(file_name)
        self.print = print_this
        if VERBOSE:
            self.print(file_name)
        try:
            self.connection = open_database(file_name, check_same_thread=not read_only)
        except:  # noqa
            self.print(f"Can't open {file_name}")
            raise

        if bulk_insert_mode:
            self.excute_nonquery("PRAGMA journal_mode = MEMORY;")
            self.excute_nonquery("PRAGMA synchronous = OFF;")
            # other ways to go fast & unsafe
            # PRAGMA cache_size = 100000;
            # PRAGMA temp_store = MEMORY;

        self.pending_count = 0
        self.commit_every = commit_every
        self.grand_count = 0

        self.close_called = False

    def __del__(self) -> None:
        """Runs during garbage collection
        which might never run, or if it does run, state of the application
        might be surprising because you don't know what has already been
        garbage collected
        """
        close_and_ignore_errors(self)

    def __enter__(self) -> "ConnectionManager":
        """Return connection"""
        return self

    def __exit__(
        self, exception_type: Any, exception_value: Any, traceback: Any
    ) -> None:
        """
        Close connection
        """
        self.close(skip_vacuum=False)
        self.close_called = True

    def close(self, skip_vacuum: bool = True) -> None:
        """
        Another way to close when not doing so with context manager
        """
        if self.close_called:
            return
        if self.connection:
            if not self.read_only:
                self.connection.commit()
            if not skip_vacuum and not self.read_only:
                self.excute_nonquery("VACUUM;")
            self.connection.close()
            if VERBOSE:
                self.print(
                    f"Closing {self.file_name} :"
                    f" processed {self.grand_count} transactions"
                )
        self.close_called = True

    def check_point(self) -> None:
        """
        Another way to close when not doing so with context manager
        """
        if self.read_only:
            return

        if self.connection:  # and not self.close_called:
            # pylint: disable=broad-except
            try:
                self.connection.commit()
            except Exception as exception:  # noqa
                self.print(str(exception))
                self.print("Attempted to commit, Did we call close already?")

        if self.grand_count % 100000 == 0:  # and not self.close_called:
            # pylint: disable=broad-except
            try:
                self.excute_nonquery("VACUUM;")
            except Exception as exception:  # noqa
                self.print(str(exception))
                self.print("Did we call close already?")
        if VERBOSE:
            self.print(f"{self.file_name} : processed {self.grand_count} transactions")

    def insert_record(self, data: tuple[Any, ...], sql: str) -> Optional[int]:
        """
        Insert a record
        """
        if self.read_only:
            raise TypeError("Read only mode")
        # you must explicitly close cursors or it will crash on pypy
        with closing(self.connection.cursor()) as the_cursor:
            the_cursor.execute(sql, data)
            self.process_pending()
            return the_cursor.lastrowid

    def insert_many(self, data: list[tuple[Any, ...]], sql: str) -> Optional[int]:
        """
        Insert a record
        """
        if self.read_only:
            raise TypeError("Read only mode")
        # you must explicitly close cursors or it will crash on pypy
        with closing(self.connection.cursor()) as the_cursor:
            the_cursor.executemany(sql, data)
            self.process_pending(increment=len(data))
            return the_cursor.lastrowid

    def select_sql_count(self, sql: str) -> tuple[int, Any]:
        """
        Send a select query to the database and return a rowcount and the results.
        Prints if the query execution time goes over 1s.
        """
        start = time.time()

        with closing(self.connection.cursor()) as cursor:
            cursor.execute(sql)
            total_time = time.time() - start
            if total_time > 1.0:
                self.print(f"Slow query: {total_time:.2f}s")
            return cursor.rowcount, cursor.fetchall()

    def select_sql_cursor(self, sql: str) -> Any:
        """
        Run a SQL statement in a cursor and return the cursor, which must be
        closed.
        """
        cursor: Any = self.connection.cursor()
        cursor.execute(sql)
        return cursor

    def select_sql(self, sql: str) -> Any:
        """
        Query all rows in the table
        """

        start = time.time()

        # you must explicitly close cursors or it will crash on pypy
        with closing(self.connection.cursor()) as the_cursor:
            the_cursor.execute(sql)
            total_time = time.time() - start
            if total_time > 1.0:
                self.print(f"Slow query {total_time:.2f}s")
            return the_cursor.fetchall()

    def count_table(self, table: str) -> int:
        """
        Query all rows in the table
        """
        # you must explicitly close cursors or it will crash on pypy
        with closing(self.connection.cursor()) as the_cursor:
            the_cursor.execute(f"SELECT count(*) FROM {table}")  # nosec
            return int(the_cursor.fetchall()[0][0])

    def select_table_iter(self, table: str) -> tuple[int, Iterator[Any]]:
        """
        Query all rows in a given table and return the cursor itself.
        """
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT * FROM {table}")  # nosec

        return cursor

    def select_table(self, table: str) -> tuple[int, Any]:
        """
        Query all rows in the table
        """
        # you must explicitly close cursors or it will crash on pypy
        with closing(self.connection.cursor()) as the_cursor:
            the_cursor.execute(f"SELECT count(*) FROM {table}")  # nosec

            the_count = the_cursor.fetchall()[0][0]

            the_cursor.execute(f"SELECT * FROM {table}")  # nosec

            return the_count, the_cursor.fetchall()

    def excute_nonquery(self, sql: str) -> bool:
        """Execute any sql statement, no transaction"""

        # you must explicitly close cursors or it will crash on pypy
        with closing(self.connection.cursor()) as the_cursor:
            try:
                # cursor returned for DDL is empty
                the_cursor.execute(sql)
                return True
            except sqlite3.OperationalError as operational_error:
                if "no such table" in str(operational_error):
                    return False
                if "already exists" in str(operational_error):
                    return False
                raise

    def excute_nonquery_with_transaction(self, sql: str) -> bool:
        """
        Execute and commit
        For delete, updates, etc.
        """

        with closing(self.connection.cursor()) as the_cursor:
            _ = the_cursor.execute(sql)
            # return cursor usually empty
            self.process_pending()
            return True

    def process_pending(self, increment: int = 1) -> None:
        """
        Do some bookkeeping and decide if we should commit
        """
        self.pending_count += increment
        self.grand_count += increment
        if self.pending_count % 100 == 0 and VERBOSE:
            self.print(f"processed {self.pending_count}")
        if self.pending_count > self.commit_every:
            self.connection.commit()
            if self.commit_every < 10 and self.grand_count % 100 == 0 and VERBOSE:
                self.print(f"Committing : {self.pending_count}")
            if self.commit_every >= 100 and VERBOSE:
                self.print(f"Committing : {self.pending_count}")

            self.pending_count = 0
