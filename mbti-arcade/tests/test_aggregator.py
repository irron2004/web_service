import math
import unittest
from datetime import UTC, datetime, timedelta

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
except ImportError:  # pragma: no cover - optional dependency guard
    SQLALCHEMY_AVAILABLE = False
else:
    SQLALCHEMY_AVAILABLE = True

from app.database import Base
from app.models import Aggregate, OtherResponse, Question, Session, SelfResponse
from app.services.aggregator import recalculate_aggregate
from app.services.scoring import ScoringError, compute_gap_metrics, compute_norms, weight_for_relation


def _make_session():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    session = SessionLocal()
    return session, engine


def _insert_questions(db_session):
    db_session.add_all(
        [
            Question(id=1, code="Q1", dim="EI", sign=1, context="common", prompt_self="", prompt_other="", theme="", scenario=""),
            Question(id=2, code="Q2", dim="SN", sign=1, context="common", prompt_self="", prompt_other="", theme="", scenario=""),
            Question(id=3, code="Q3", dim="TF", sign=1, context="common", prompt_self="", prompt_other="", theme="", scenario=""),
            Question(id=4, code="Q4", dim="JP", sign=1, context="common", prompt_self="", prompt_other="", theme="", scenario=""),
        ]
    )
    db_session.commit()


class ScoringHelpersTest(unittest.TestCase):
    def test_compute_norms_handles_invalid_question(self):
        lookup = {1: ("EI", 1)}
        with self.assertRaises(ScoringError):
            compute_norms([(99, 3)], lookup)

    def test_compute_norms_computes_dimension_scores(self):
        lookup = {
            1: ("EI", 1),
            2: ("EI", -1),
            3: ("SN", 1),
            4: ("TF", 1),
            5: ("JP", -1),
        }
        norms = compute_norms([(1, 5), (2, 1), (3, 3), (4, 1), (5, 5)], lookup)
        self.assertTrue(math.isclose(norms["EI"], 1.0))
        self.assertTrue(math.isclose(norms["SN"], 0.0))
        self.assertTrue(math.isclose(norms["TF"], -1.0))

    def test_compute_gap_metrics_weights_and_sigma(self):
        self_norm = {dim: 0.0 for dim in ("EI", "SN", "TF", "JP")}
        other_norms = [
            {"EI": -1.0, "SN": 1.0, "TF": 1.0, "JP": -1.0},
            {"EI": 0.0, "SN": 0.5, "TF": -0.5, "JP": 0.0},
        ]
        weights = [1.0, 1.5]

        agg_other, sigma, gaps, gap_score = compute_gap_metrics(self_norm, other_norms, weights)

        self.assertTrue(math.isclose(agg_other["EI"], -0.4))
        self.assertTrue(math.isclose(agg_other["SN"], 0.7))
        self.assertTrue(math.isclose(agg_other["TF"], 0.1))
        self.assertTrue(math.isclose(agg_other["JP"], -0.4))

        self.assertTrue(math.isclose(sigma["EI"], math.sqrt(0.24), rel_tol=1e-6))
        self.assertTrue(math.isclose(gaps["SN"], 0.7))
        self.assertTrue(math.isclose(gap_score, 40.0))

    def test_compute_gap_metrics_requires_other_norms(self):
        self_norm = {dim: 0.0 for dim in ("EI", "SN", "TF", "JP")}
        with self.assertRaises(ScoringError):
            compute_gap_metrics(self_norm, [], [])

    def test_weight_for_relation_defaults(self):
        self.assertEqual(weight_for_relation("friend"), 1.0)
        self.assertTrue(math.isclose(weight_for_relation("couple"), 1.5))
        self.assertEqual(weight_for_relation("UNKNOWN"), 1.0)
        self.assertEqual(weight_for_relation(None), 1.0)


@unittest.skipUnless(SQLALCHEMY_AVAILABLE, "sqlalchemy not installed")
class AggregateRecalculationTest(unittest.TestCase):
    def test_recalculate_aggregate_computes_weighted_stats(self):
        session, engine = _make_session()
        try:
            _insert_questions(session)
            record = Session(
                id="sess-1",
                owner_id=None,
                mode="basic",
                invite_token="token-123",
                is_anonymous=True,
                expires_at=datetime.now(UTC) + timedelta(hours=1),
                max_raters=10,
            )
            session.add(record)

            session.add_all(
                [
                    SelfResponse(session_id="sess-1", question_id=1, value=5),
                    SelfResponse(session_id="sess-1", question_id=2, value=3),
                    SelfResponse(session_id="sess-1", question_id=3, value=1),
                    SelfResponse(session_id="sess-1", question_id=4, value=4),
                ]
            )

            session.add_all(
                [
                    OtherResponse(session_id="sess-1", rater_hash="r1", question_id=1, value=1, relation_tag="friend"),
                    OtherResponse(session_id="sess-1", rater_hash="r1", question_id=2, value=5, relation_tag="friend"),
                    OtherResponse(session_id="sess-1", rater_hash="r1", question_id=3, value=5, relation_tag="friend"),
                    OtherResponse(session_id="sess-1", rater_hash="r1", question_id=4, value=1, relation_tag="friend"),
                    OtherResponse(session_id="sess-1", rater_hash="r2", question_id=1, value=3, relation_tag="couple"),
                    OtherResponse(session_id="sess-1", rater_hash="r2", question_id=2, value=4, relation_tag="couple"),
                    OtherResponse(session_id="sess-1", rater_hash="r2", question_id=3, value=2, relation_tag="couple"),
                    OtherResponse(session_id="sess-1", rater_hash="r2", question_id=4, value=3, relation_tag="couple"),
                ]
            )

            session.commit()

            result = recalculate_aggregate(session, record)

            self.assertEqual(result.n, 2)
            self.assertTrue(math.isclose(result.self_norm["EI"], 1.0))
            self.assertTrue(math.isclose(result.other_norm["SN"], 0.7))
            self.assertTrue(math.isclose(result.gap["EI"], -1.4))
            self.assertTrue(math.isclose(result.sigma["JP"], math.sqrt(0.24)))
            self.assertIsNotNone(session.get(Aggregate, "sess-1"))
        finally:
            session.close()
            engine.dispose()

    def test_recalculate_aggregate_requires_self_answers(self):
        session, engine = _make_session()
        try:
            _insert_questions(session)
            record = Session(
                id="sess-2",
                owner_id=None,
                mode="basic",
                invite_token="token-456",
                is_anonymous=True,
                expires_at=datetime.now(UTC) + timedelta(hours=1),
                max_raters=10,
            )
            session.add(record)
            session.commit()

            with self.assertRaises(ScoringError):
                recalculate_aggregate(session, record)
        finally:
            session.close()
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
