from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from app.cruds.source_cruds import get_source_list
from app.database import AsyncSessionLocal
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

async def load_and_send(source, client, gen_api_token, vk_token):
    loader_factory = LoaderFactory(tg_client=client, gen_api_token=gen_api_token)
    loader = loader_factory.get_loader(source)
    await loader.load()
    if loader.data:
        sender_factory = SenderFactory(tg_client=client, vk_token=vk_token)
        service = NotificationService(sender_factory=sender_factory, source=source)
        for message in loader.data:
            #print(message.text)
            await service.send_message_to_subcribers(message)

async def add_job(scheduler, source, client, gen_api_token, vk_token):
    job_id = jobId(source)
    try:
        scheduler.add_job(
            load_and_send,
            trigger=CronTrigger.from_crontab(source.cron),
            args=[
                source,
                client,
                gen_api_token,
                vk_token
            ],
            id=job_id,
            replace_existing=True
        )
    except Exception as e:
        logger.error(f"Ошибка добавления источника в расписание: {e}")
        return
    
    logger.info(f"Новый обработчик {job_id}:\"{source.name}\" добавлен в расписание")



async def add_all_jobs(scheduler, client, gen_api_token, vk_token):
    async with AsyncSessionLocal() as session:  
        sources = await get_source_list(session, is_active=True)
        for source in sources:
            await add_job(scheduler, source, client, gen_api_token, vk_token)
        



'''async def sync_jobs(scheduler, client, gen_api_token):

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
    await add_all_jobs(scheduler, session, client, gen_api_token)'''