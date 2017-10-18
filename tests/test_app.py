from datetime import date, datetime, timezone
from unittest import TestCase

import pandas
from freezegun import freeze_time
from pandas.testing import assert_frame_equal

from petri_dish.app import Dish
from petri_dish.connectors import DummyConnector


class GetAllSubjectsTestCase(TestCase):
    @freeze_time('2017-10-17 17:21')
    def setUp(self):
        self.empty_source = DummyConnector(
            pandas.DataFrame(
                columns=[
                    'id',
                    'name',
                    'dob',
                    'colour',
                ],
            )
        )
        self.empty_sink = DummyConnector(
            pandas.DataFrame(
                columns=[
                    'id',
                    'name',
                    'dob',
                    'colour',
                    Dish.GROUP_COLUMN_NAME,
                    Dish.STAGE_COLUMN_NAME,
                    Dish.JOINED_COLUMN_NAME,
                ],
            )
        )
        self.partial_source = DummyConnector(
            pandas.DataFrame({
                'id': [1, 7],
                'name': ['Alice', 'Bob'],
                'dob': [
                    date(1997, 1, 1),
                    date(1990, 1, 1),
                ],
                'colour': ['Purple', 'Red'],
            })
        )
        self.grouped_sink = DummyConnector(
            pandas.DataFrame({
                'id': [1, 7],
                'name': ['Alice', 'Bob'],
                'dob': [
                    date(1997, 1, 1),
                    date(1990, 1, 1),
                ],
                'colour': ['Purple', 'Red'],
                Dish.GROUP_COLUMN_NAME: ['A', 'B'],
                Dish.STAGE_COLUMN_NAME: ['stage1', 'stage3'],
                Dish.JOINED_COLUMN_NAME: [
                    datetime(2017, 9, 30, 12, 30, tzinfo=timezone.utc),
                    datetime(2017, 10, 1, tzinfo=timezone.utc),
                ],
            })
        )

    @freeze_time('2017-10-17 17:21')
    def test_new_subjects_only(self):
        now = datetime.now(timezone.utc)
        dish = Dish(
            subject_source=DummyConnector(),
            subject_sink=self.empty_sink,
            group_balancer=None,
            stages=1,
        )

        subjects = dish.get_all_subjects()

        expected = pandas.DataFrame({
            'id': [1, 7, 100, 18],
            'name': ['Alice', 'Bob', 'Charlie', 'Dave'],
            'dob': [
                date(1997, 1, 1),
                date(1990, 1, 1),
                date(2010, 1, 1),
                date(1985, 1, 1),
            ],
            'colour': ['Purple', 'Red', 'Blue', 'Green'],
            Dish.GROUP_COLUMN_NAME: [None, None, None, None],
            Dish.STAGE_COLUMN_NAME: [None, None, None, None],
            Dish.JOINED_COLUMN_NAME: [now, now, now, now],
        })
        assert_frame_equal(subjects, expected, check_like=True)

    def test_grouped_subjects_only(self):
        dish = Dish(
            subject_source=self.partial_source,
            subject_sink=self.grouped_sink,
            group_balancer=None,
            stages=1,
        )

        subjects = dish.get_all_subjects()
        expected = pandas.DataFrame({
            'id': [1, 7],
            'name': ['Alice', 'Bob'],
            'dob': [
                date(1997, 1, 1),
                date(1990, 1, 1),
            ],
            'colour': ['Purple', 'Red'],
            Dish.GROUP_COLUMN_NAME: ['A', 'B'],
            Dish.STAGE_COLUMN_NAME: ['stage1', 'stage3'],
            Dish.JOINED_COLUMN_NAME: [
                datetime(2017, 9, 30, 12, 30, tzinfo=timezone.utc),
                datetime(2017, 10, 1, tzinfo=timezone.utc),
            ],
        })

        assert_frame_equal(subjects, expected, check_like=True)

    @freeze_time('2017-10-17 17:21')
    def test_mixed_subjects(self):
        now = datetime.now(timezone.utc)
        dish = Dish(
            subject_source=DummyConnector(),
            subject_sink=self.grouped_sink,
            group_balancer=None,
            stages=1,
        )

        subjects = dish.get_all_subjects()
        expected = pandas.DataFrame({
            'id': [1, 7, 100, 18],
            'name': ['Alice', 'Bob', 'Charlie', 'Dave'],
            'dob': [
                date(1997, 1, 1),
                date(1990, 1, 1),
                date(2010, 1, 1),
                date(1985, 1, 1),
            ],
            'colour': ['Purple', 'Red', 'Blue', 'Green'],
            Dish.GROUP_COLUMN_NAME: ['A', 'B', None, None],
            Dish.STAGE_COLUMN_NAME: ['stage1', 'stage3', None, None],
            Dish.JOINED_COLUMN_NAME: [
                datetime(2017, 9, 30, 12, 30, tzinfo=timezone.utc),
                datetime(2017, 10, 1, tzinfo=timezone.utc),
                now,
                now,
            ],
        })

        assert_frame_equal(subjects, expected, check_like=True)
