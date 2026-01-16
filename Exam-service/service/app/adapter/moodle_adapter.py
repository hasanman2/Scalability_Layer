from typing import Any, Dict, List, Optional, Tuple
from sqlalchemy import create_engine, text
from app.config import settings
import time

class MoodleAdapter:
    """
    Encapsulates all Moodle-specific logic.
    """

    TABLE_PREFIX = "mdl_"

    def __init__(self) -> None: 
        self.engine = create_engine(settings.lms_db_url, future = True)

    def _t(self, name: str) -> str:
        """Prefix helper: _t('quiz_attempts') -> 'mdl_quiz_attempts'."""
        return f"{self.TABLE_PREFIX}{name}"
    
    def _get_usage_id(self, conn, attempt_id: int) -> int:
        row = conn.execute(
            text(f"SELECT uniqueid FROM {self._t('quiz_attempts')} WHERE id = :attempt_id"),
            {"attempt_id": attempt_id},
        ).mappings().first()
        if not row:
            raise ValueError(f"Attempt ID {attempt_id} not found")
        usage_id = int(row["uniqueid"] or 0)
        if usage_id <= 0:
            raise ValueError(f"Invalid usage_id for attempt {attempt_id}: {usage_id}")
        return usage_id

    def _get_question_attempt_id(self, conn, usage_id: int, slot: int) -> int:
        row = conn.execute(
            text(f"""
                SELECT id
                FROM {self._t('question_attempts')}
                WHERE questionusageid = :usage_id AND slot = :slot
            """),
            {"usage_id": usage_id, "slot": slot},
        ).mappings().first()
        if not row:
            raise ValueError(f"No question_attempt for usage_id={usage_id}, slot={slot}")
        return int(row["id"])

    def get_question_payload(self, attempt_id: int, slot: int) -> Dict[str, Any]:
        """
        Minimal DB-only implementation:
        attempt_id -> quiz_attempts.uniqueid (questionusageid)
        (uniqueid, slot) -> question_attempts.questionid + maxmark
        questionid -> question.questiontext (+ answers if available)
        """
        import logging
        logger = logging.getLogger(__name__)

        try:
            with self.engine.connect() as conn:
                # 1) quiz_attempts.id -> uniqueid (questionusageid)
                attempt_row = conn.execute(
                    text(f"""
                        SELECT uniqueid 
                        FROM {self._t('quiz_attempts')} 
                        WHERE id = :attempt_id
                    """),
                    {"attempt_id": attempt_id}
                ).mappings().first()
                if not attempt_row:
                    raise ValueError(f"Attempt ID {attempt_id} not found.")

                usage_id = int(attempt_row["uniqueid"])
                if usage_id <= 0:
                    raise ValueError(
                        f"Invalid question usage ID {usage_id} for attempt ID {attempt_id}."
                    )

                # 2) (questionusageid, slot) -> questionid, maxmark
                qa_row = conn.execute(
                    text(f"""
                        SELECT id AS question_attempt_id, questionid, maxmark
                        FROM {self._t('question_attempts')}
                        WHERE questionusageid = :usage_id AND slot = :slot
                    """),
                    {"usage_id": usage_id, "slot": slot},
                ).mappings().first()
                if not qa_row:
                    raise ValueError(
                        f"No question_attempt found for attempt {attempt_id} "
                        f"(usage {usage_id}) and slot {slot}"
                    )

                question_id = int(qa_row["questionid"])
                max_mark = float(qa_row["maxmark"] or 1.0)

                # 3) questionid -> question text + qtype
                q_row = conn.execute(
                    text(f"""
                        SELECT id, qtype, questiontext
                        FROM {self._t('question')}
                        WHERE id = :question_id
                    """),
                    {"question_id": question_id},
                ).mappings().first()

                if not q_row:
                    raise ValueError(
                        f"Question {question_id} not found in question table"
                    )

                qtype = (q_row["qtype"] or "").strip()
                questiontext_html = q_row["questiontext"] or ""

                # 4) For some qtypes, fetch answers
                answers: List[Dict[str, Any]] = []
                if qtype in {"multichoice", "truefalse"}:
                    ans_rows = conn.execute(
                        text(f"""
                            SELECT id, answer, fraction
                            FROM {self._t('question_answers')}
                            WHERE question = :question_id
                            ORDER BY id ASC
                        """),
                        {"question_id": question_id},
                    ).mappings().all()

                    for r in ans_rows:
                        answers.append(
                            {
                                "id": int(r["id"]),
                                "answer_html": r["answer"] or "",
                                "fraction": float(r["fraction"] or 0.0),
                            }
                        )

                rendered_html = self._build_simple_question_html(
                    questiontext_html=questiontext_html,
                    qtype=qtype,
                    answers=answers,
                    slot=slot,
                )

                return {
                    "attempt_id": attempt_id,
                    "slot": slot,
                    "question_html": rendered_html,
                    "meta": {"max_mark": max_mark},
                }

        except Exception as e:
            logger.exception(
                "Error in get_question_payload(attempt_id=%s, slot=%s): %s",
                attempt_id, slot, e,
            )
            return {
                "attempt_id": attempt_id,
                "slot": slot,
                "question_html": (
                    f"<p>Temporary dummy question (fallback) for attempt {attempt_id}, "
                    f"slot {slot}. Error: {e}</p>"
                ),
                "meta": {"max_mark": 0.0},
            }

    def _build_simple_question_html(
        self,
        *,
        questiontext_html: str,
        qtype: str,
        answers: List[Dict[str, Any]],
        slot: int,
    ) -> str:
        """
        Minimal HTML builder for testing.
        - keeps Moodle's questiontext HTML as-is
        - for multichoice/truefalse: adds a radio list of answers
        """
        # Header / wrapper
        html = []
        html.append(f'<div class="exam-question" data-slot="{slot}" data-qtype="{qtype}">')
        html.append('<div class="question-text">')
        html.append(questiontext_html or "<p>(no question text)</p>")
        html.append("</div>")

        # Answer area (only for qtypes we handle simply)
        if answers:
            html.append('<div class="answers">')
            html.append("<ul>")
            for a in answers:
                aid = a["id"]
                ahtml = a["answer_html"] or ""
                # Name includes slot so your client can read one selected option per slot
                html.append(
                    "<li>"
                    f'<label>'
                    f'<input type="radio" name="slot_{slot}" value="{aid}"> '
                    f'{ahtml}'
                    f"</label>"
                    "</li>"
                )
            html.append("</ul>")
            html.append("</div>")
        else:
            # Generic placeholder for qtypes like shortanswer/essay/numerical
            html.append('<div class="answers">')
            html.append('<input type="text" name="slot_{slot}" placeholder="Your answer..." />'.replace("{slot}", str(slot)))
            html.append("</div>")

        html.append("</div>")
        return "\n".join(html)

    
    def save_answer(
            self, 
            attempt_id: int,
            slot: int,
            response: Dict[str, Any]
    ) -> None:
        """
        Synchronous prototype persistence:
        - create a new question_attempt_step
        - attach step_data that represents the response
        """
        now = int(time.time())

        # light validation (optional but helps debugging)
        if not isinstance(response, dict):
            raise ValueError("response must be an object")

        answer_id: Optional[int] = None
        text_answer: Optional[str] = None

        if "answer_id" in response:
            answer_id = int(response["answer_id"])
        if "text" in response:
            text_answer = str(response["text"])

        if answer_id is None and (text_answer is None or text_answer.strip() == ""):
            raise ValueError("response must contain either answer_id or non-empty text")

        with self.engine.begin() as conn:
            usage_id = self._get_usage_id(conn, attempt_id)
            question_attempt_id = self._get_question_attempt_id(conn, usage_id, slot)

            # 1) insert a new step
            # NOTE: schema differs slightly by Moodle version. Common columns include:
            # questionattemptid, sequencenumber, state, fraction, timecreated, userid
            #
            # We compute sequencenumber = MAX+1 for this question_attempt_id.
            seq_row = conn.execute(
                text(f"""
                    SELECT COALESCE(MAX(sequencenumber), -1) AS maxseq
                    FROM {self._t('question_attempt_steps')}
                    WHERE questionattemptid = :qaid
                """),
                {"qaid": question_attempt_id},
            ).mappings().first()

            next_seq = int(seq_row["maxseq"]) + 1

            # Try a minimal insert that usually exists. You may need to adjust columns based on your DB schema.
            step_insert = conn.execute(
                text(f"""
                    INSERT INTO {self._t('question_attempt_steps')}
                        (questionattemptid, sequencenumber, state, fraction, timecreated)
                    VALUES
                        (:qaid, :seq, :state, :fraction, :timecreated)
                    RETURNING id
                """),
                {
                    "qaid": question_attempt_id,
                    "seq": next_seq,
                    "state": "todo",      # prototype value; Moodle uses states like 'todo', 'complete', etc.
                    "fraction": None,     # grading not handled here
                    "timecreated": now,
                },
            ).mappings().first()

            step_id = int(step_insert["id"])

            # 2) insert step_data (key/value pairs)
            # Keys depend on qtype, but for a prototype you can store something stable.
            # Common patterns in Moodle step data include keys like 'answer', 'choice', etc.
            data_rows = []
            if answer_id is not None:
                # store selected answer option id
                data_rows.append(("answer_id", str(answer_id)))
            if text_answer is not None:
                data_rows.append(("text", text_answer))

            for name, value in data_rows:
                conn.execute(
                    text(f"""
                        INSERT INTO {self._t('question_attempt_step_data')}
                            (attemptstepid, name, value)
                        VALUES
                            (:stepid, :name, :value)
                    """),
                    {"stepid": step_id, "name": name, "value": value},
                )

            # 3) optional: bump quiz attempt modified time
            conn.execute(
                text(f"""
                    UPDATE {self._t('quiz_attempts')}
                    SET timemodified = :now
                    WHERE id = :attempt_id
                """),
                {"now": now, "attempt_id": attempt_id},
            )

adapter = MoodleAdapter()