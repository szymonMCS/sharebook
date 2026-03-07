import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from src.services.interfaces import ISaga, ISagaStep, SagaResult, SagaContext

logger = logging.getLogger(__name__)


class SagaOrchestrator(ISaga):
    def __init__(self, steps: List[ISagaStep], saga_repository=None):
        self._steps = steps
        self._saga_repo = saga_repository

    async def execute(self, **kwargs) -> SagaResult:
        saga_id = kwargs.get("saga_id")
        if not saga_id:
            saga_id = UUID(int=0)

        context = SagaContext(saga_id=saga_id, current_step=0, payload=kwargs)

        executed_steps = []

        try:
            for i, step in enumerate(self._steps):
                context.current_step = i
                logger.info(f"Executing step {i}: {step.name}")

                success = await step.execute(context)
                if not success:
                    raise Exception(f"Step {step.name} failed")

                executed_steps.append(step)

            return SagaResult(
                success=True,
                data=context.payload
            )

        except Exception as e:
            logger.error(f"Saga failed at step {context.current_step}: {e}")
            await self._compensate(executed_steps, context)
            return SagaResult(
                success=False,
                error_message=str(e)
            )

    async def _compensate(self, steps: List[ISagaStep], context: SagaContext) -> None:
        for step in reversed(steps):
            try:
                logger.info(f"Compensating step: {step.name}")
                await step.compensate(context)
            except Exception as e:
                logger.error(f"Compensation failed for {step.name}: {e}")
