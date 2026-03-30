from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from app.cruds.source_cruds import get_source_list
from app.senders.factory import SenderFactory
from app.loaders.factory import LoaderFactory
from app.services.notification import NotificationService


jobId = lambda source: f"{source.type}_{source.id}"

def is_trigger_equal_cron(trigger, cron_string):
    cron_parts = cron_string.strip().split(" ")
    if len(cron_parts) != 5:
        return False

    trigger_parts = [
        str(trigger.fields[6]),
        str(trigger.fields[5]),
        str(trigger.fields[2]),
        str(trigger.fields[1]),
        str(trigger.fields[4])
    ]

    return cron_parts == trigger_parts

async def load_and_send(source, session, client, gen_api_token):
    loader_factory = LoaderFactory(session=session, tg_client=client, gen_api_token=gen_api_token)
    loader = loader_factory.get_loader(source)
    await loader.load()
    if loader.data:
        sender_factory = SenderFactory(tg_client=client)
        service = NotificationService(session=session, sender_factory=sender_factory, source=source)
        for message in loader.data:
            await service.send_message_to_subcribers(message)

async def add_job(scheduler, source, session, client, gen_api_token):
    job_id = f"{source.type}_{source.id}"
    try:
        scheduler.add_job(
            load_and_send,
            trigger=CronTrigger.from_crontab(source.cron),
            args=[
                source,
                session,
                client,
                gen_api_token
            ],
            id=job_id,
            replace_existing=True
        )
    except Exception as e:
        logger.error(f"Ошибка добавления источника в расписание: {e}")
        return
    
    logger.info(f"Новый обработчик {job_id}:\"{source.cron}\" добавлен в расписание")



async def add_all_jobs(scheduler, session, client, gen_api_token):
    sources = await get_source_list(session, is_active=True)
    
    # проверяем удаленные задания
    scheduler_jobs = set({job.id for job in scheduler.get_jobs() if job.id != "main"})
    db_jobs = set({jobId(s) for s in sources})
    removed_jobs = list(scheduler_jobs - db_jobs)
    if removed_jobs:
        for job_id in removed_jobs:
            scheduler.remove_job(job_id)
            logger.info(f"Обработчик {job_id} удален из расписания")

    for source in sources:
        job_id = jobId(source)
        job = scheduler.get_job(job_id)
        if not job:
            # если задания нет в расписании - добавляем
            await add_job(scheduler, source, session, client, gen_api_token)
        else:
            # проверяем изменения cron строк в БД, если есть изменения 
            db_trigger = CronTrigger.from_crontab(source.cron)
            if not is_trigger_equal_cron(job.trigger, source.cron):
                scheduler.reschedule_job(job_id, trigger=db_trigger)
                logger.info(f"Обработчик {job_id} обновлен: {source.cron}")



async def sync_jobs(scheduler, session, client, gen_api_token):
    '''запуск всех активных источников и синхронизации с БД (для удаления и добавления)'''
    logger.debug(f"Синхронизация обработчиков...")
    scheduler.add_job(
        add_all_jobs,
        trigger=CronTrigger.from_crontab("* * * * *"),
        args=[
            scheduler,
            session,
            client,
            gen_api_token
        ],
        id="main",
        replace_existing=True
    )
    await add_all_jobs(scheduler, session, client, gen_api_token)