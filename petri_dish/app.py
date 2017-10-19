import gc
from datetime import datetime, timezone


class Dish:
    """
    A Dish instance models an experiment with a set of subjects and their
    treatement [and control] groups.

    The operations performed when running an expriment are:

    * Fetch all subjects from the ``subject_source``.
    * Filter out subjects, by running all filters for each one.
    * Split subjects into groups (this is done by the provided
        ``group_balancer``.
    * Update the current stage for all users.
    * Save all grouped users into the ``subject_sink`` connector.
    """
    GROUP_COLUMN_NAME = 'petri:group'
    STAGE_COLUMN_NAME = 'petri:stage'
    JOINED_COLUMN_NAME = 'petri:joined'

    def __init__(
        self,
        subject_source,
        subject_sink,
        group_balancer,
        stages,
        index_column_name='id',
        filters=(),
    ):
        """
        :param Connector subject_source: A source for subjects; where new
            subjects are read from. This source can also contain subjects
            already present in the experiment; this will be deduplicated
            internally.
        :param Connector subject_sink: A sink where filtered, grouped, and
            staged subjects will be dumped into. This connector must support
            reading and writing.
        :param Balancer group_balancer: A balancer instance that will balance
            subjects into groups.
        :param list(tuple(datetime.timedelta, str)) stages: A list of stages
            which subjects go through. Each stage is a tuple of
            ``datetime.timedelta`` (how long they've been in the experiment``),
            and ``str` `(the name of the stage).
            Stages MUST be provided in ascending order of timedelta.
        :param str index_column_name: The name of the column which represents
            the unique index for each subject in the data source.
        :param list[func] filter: A set of filters, which will be run against
            each new subject in the data source. Each function must return True
            if the subject is valid for the experiment, or False if they do not
            qualify.
        """
        if not stages:
            raise ValueError('The experiment must have at least one stage.')

        self.subject_source = subject_source
        self.subject_sink = subject_sink
        self.group_balancer = group_balancer
        self.filters = filters
        self.stages = stages
        self.index_column_name = index_column_name

    def get_all_subjects(self):
        """
        Returns all subjects.

        New subjects are read from the configured ``subject_source``, and
        previously processed subjects are read from the ``subject_sunk``.

        Both data sets are merged, and normalized, and returned as a single
        one.

        New subjects will include the joined date assigned.
        """
        new_subjects = self.subject_source.read()
        grouped_subjects = self.subject_sink.read()

        grouped_subjects = grouped_subjects.filter(
            [
                self.index_column_name,
                self.GROUP_COLUMN_NAME,
                self.STAGE_COLUMN_NAME,
                self.JOINED_COLUMN_NAME,
            ],
            axis='columns',
        )
        subjects = new_subjects.merge(
            grouped_subjects,
            how='left',
            on=[self.index_column_name],
        )
        subjects[self.JOINED_COLUMN_NAME].fillna(
            datetime.now(timezone.utc),
            inplace=True,
        )

        return subjects

    def stage_for_subject(self, subject):
        """Returns the current stage for a given subject."""
        # XXX: Can we make this method more efficient?
        now = datetime.now(timezone.utc)
        stage = None

        for period, name in self.stages.items():
            if subject[self.JOINED_COLUMN_NAME] + period >= now:
                stage = name
            else:
                break

        return stage

    def update_subject_stages(self, subjects):
        """
        Update the current stage for ``subjects`` using the configued stages.
        """
        stages = subjects.apply(self.stage_for_row)
        subjects[self.STAGE_COLUMN_NAME] = stages

    def run(self):
        """
        The classification of new subjects and update stages for existing
        subjects.
        """
        subjects = self._get_all_subjects()

        for filter_ in self.filters:
            subjects = subjects[subjects.apply(filter_, axis=1)]
            # We basically copy all rows that still match when filtering, so
            # run the GC since this can eat up N*rows memory, where N is the
            # amount of filters.
            gc.apply()

        self.update_subject_stages(subjects)
        self.group_balancer.balance(subjects)

        self.subject_sink.write(subjects)
        gc.apply()
