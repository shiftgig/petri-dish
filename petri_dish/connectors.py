"""
This module contains several connectors all sharing a same API.
"""
import logging

import gspread
import pandas
import psycopg2
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)


logging.basicConfig(level=logging.DEBUG)


def _cast_dataframe_types(dataframe, data_types):
    for col, dtype in data_types.items():
        if col not in dataframe.columns:
            raise KeyError(
                "Dictionary dtypes's key '{col}' was not found "
                "in sheet.".format(col=col)
            )

        try:
            dataframe[col] = dataframe[col].astype(dtype)
        except ValueError as e:
            raise Exception(
                'Column "{col}" could not be typecast as {dtype}'
                .format(col=col, dtype=dtype)
            ) from e


class GoogleSheetConnector:
    """
    A connector to read or write data from a google spreadsheet.
    """
    SCOPES = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive',
    ]

    def __init__(
        self,
        secret_key_path,
        sheet_title,
        create=False,
        share_with=None,
    ):
        """
        Create a new Google Sheet connector.

        This connector is a wrapper around a spreadsheet.

        :param os.Pathlike secret_key_path: The path to the secret key file.
        :param str sheet_title: The title for the spreadsheet. It must be
            shared with the service account, unless a new one is to be created.
        :param bool create: Indicate if the spreadsheet should be created if it
            does not exist. If this value is True, ``share_with`` MUST be
            provided.
        :param str share_with: The email address of an account where newly
            created sheets will be shared by default.
        """
        credentials = Credentials.from_service_account_file(secret_key_path)
        scoped_credentials = credentials.with_scopes(self.SCOPES)

        self.client = gspread.Client(scoped_credentials)
        self.client.session = AuthorizedSession(scoped_credentials)

        self.share_with = share_with
        self.sheet = self._open(sheet_title, create=create)

    def _open(self, sheet_title, create=False):
        """
        Opens and returns a spreadsheet. Creates a new one if ``create`` is
        ``True``.

        :param str sheet_title: The title for the spreadsheet. It must be
            shared with the service account, unless a new one is to be created.
        :param bool create: Indicate if the spreadsheet should be created if it
            does not exist.
        :rtype: gspread.Spreadsheet
        """
        try:
            return self.client.open(sheet_title)
        except gspread.exceptions.SpreadsheetNotFound as e:
            # Only raise if we've been told not to create one:
            if not create:
                raise Exception(
                    'Spreadsheet {title} not found. Try sharing spreadsheet '
                    'with {email}'.format(
                        title=sheet_title,
                        email=self.creds._service_account_email
                    )
                ) from e

        if not self.share_with:
            raise Exception(
                'Creating sheets is not possible if "share_with" is unset.',
            )

        sheet = self.client.create(sheet_title)
        # NOTE: Sharing as 'owner'  fails, because service accounts seem to
        # have a different domain as gapps account (be careful editing this,
        # gspread fails SILENTLY!
        sheet.share(self.share_with, 'user', 'writer')

        logger.info('Created sheet "{}"".'.format(sheet.id))

        return sheet

    @staticmethod
    def _shape_to_range(dataframe, headers=True):
        """Returns a dataframe's shape as a gsheet range."""
        row_count, col_count = dataframe.shape
        if headers:
            return 1, 1, row_count + 1, col_count
        else:
            return 1, 1, row_count, col_count

    def write(self, dataframe, worksheet_number=1):
        """
        Write a dataframe into a spreadsheet

        :param pandas.DataFrame dataframe: The actual data to write to the
            sheet.
        :param int worksheet_number: The worksheet to read. Indexes start at 1.
        """
        worksheet = self.sheet.get_worksheet(worksheet_number - 1)

        col_indexes = {
            index: column_name
            for index, column_name in enumerate(dataframe.columns)
        }

        # Select a range (as big as the dataframe):
        cell_list = worksheet.range(*self._shape_to_range(dataframe))

        for cell in cell_list:
            if cell.row == 1:
                cell.value = col_indexes[cell.col - 1]
            else:
                # Substract 1 because gspread indexes start at 1.
                # Substract 2 to the row because we lost an extra row for the
                # header.
                cell.value = dataframe[col_indexes[cell.col - 1]][cell.row - 2]

        # Update in batch:
        worksheet.update_cells(cell_list)

    def read(self, data_types=None, worksheet_number=1):
        """
        Reads a sheet into a dataframe.

        :param dict data_types: A dictionary of column headers -> data types,
            used to cast each column to a specify type.
        :param int worksheet_number: The worksheet to read. Indexes start at 1.

        :rtype: pandas.DataFrame
        """
        worksheet = self.sheet.get_worksheet(worksheet_number - 1)

        contents = worksheet.get_all_records(head=1)
        columns = [col for col in worksheet.row_values(1) if col != '']
        dataframe = pandas.DataFrame(contents, columns=columns)

        if data_types:
            _cast_dataframe_types(dataframe, data_types)
        return dataframe


class PostgresConnector:
    """
    A connector to read data from a postgres database.

    Note that only reading is supported, and writing is not implemented.
    """
    def __init__(self, dbname, user, password, host, port, query, params=()):
        """
        Creates a new PG connector.

        :param str dbname: The name of the database from which to read.
        :param str user: The database username with which to authenticate.
        :param str password: The database password with which to authenticate.
        :param str host: The database server's hostname.
        :param int port: The port where the database server is running (default
            5432).
        :param str query: A postgres query that is executed to read data.
        :param list params: Parameteres used to contruct the full SQL query.
        """
        self.conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
        )

        self.query = query
        self.params = params

    def read(self, data_types=None):
        """
        Reads data into a dataframe.

        :param dict data_types: A dictionary of column headers -> data types,
            used to cast each column to a specify type.
        :param int worksheet_number: The worksheet to read. Indexes start at 1.

        :rtype: pandas.DataFrame
        """
        cur = self.conn.cursor()
        cur.execute(self.query, self.params)
        columns = [desc[0] for desc in cur.description]

        dataframe = pandas.DataFrame(cur.fetchall(), columns=columns)
        if data_types:
            _cast_dataframe_types(dataframe, data_types)
        return dataframe

    def write(self, dataframe):
        raise NotImplementedError('Writing to postgres is not implemented.')
