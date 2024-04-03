import asyncio
import asyncpg
import httpx
import json
import time

import meilisearch

from autostudent.settings import Settings
from autostudent.repository.summarization import (
    try_find_summarization_for_video,
    insert_summarization_for_video,
)


REQUEST_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36",
}

MEILISEARCH_INDEX_NAME = "keypoints"


def _is_youtube_url(video_url: str) -> bool:
    return video_url.startswith("https://www.youtube.com")


async def _poll_summarization_task(
    poll_interval_ms: int,
    session_id: str,
    video_url: str,
    http_client: httpx.AsyncClient,
) -> str:
    settings = Settings()

    deadline = int(time.time()) + settings.generate_summarization_timeout_seconds

    await asyncio.sleep(poll_interval_ms / 1000)

    poll_summarization_task_request_body = {
        "session_id": session_id,
        "video_url": video_url,
    }
    error_message_template = "Failed to poll summarization: {reason}"

    while int(time.time()) < deadline:
        response = await http_client.post(
            url=settings.generate_summarization_endpoint,
            json=poll_summarization_task_request_body,
            headers=REQUEST_HEADERS,
        )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise Exception(
                error_message_template.format(
                    reason=f"error response {exc.response.status_code} while requesting {exc.request.url!r}.",
                )
            )

        response_json = response.json()
        if "keypoints" in response_json and response_json["status_code"] == 0:
            return json.dumps(response_json["keypoints"])
        elif "error_code" in response_json:
            raise Exception(
                error_message_template.format(
                    reason=f"got an unsuccessful polling response: {json.dumps(response_json)}",
                )
            )

        poll_interval_ms = int(response_json.get("poll_interval_ms", 1000))
        await asyncio.sleep(poll_interval_ms / 1000)

    raise Exception(
        error_message_template.format(
            reason="timeout was reached",
        )
    )


async def get_summarization(
    video_url: str,
    lesson_id: int,
    conn: asyncpg.Connection,
) -> str:
    if not _is_youtube_url(video_url):
        raise Exception(
            f"Currently, only YouTube videos are supported. URL: {video_url}"
        )

    settings = Settings()
    summarization: str = None

    error_message_template = "Failed to get summarization: {reason}"

    summarization = await try_find_summarization_for_video(
        conn=conn,
        video_url=video_url,
    )

    if summarization is not None:
        return summarization

    create_summarization_task_request_body = {
        "video_url": video_url,
    }

    async with httpx.AsyncClient(http2=True) as http_client:
        response = await http_client.post(
            url=settings.generate_summarization_endpoint,
            json=create_summarization_task_request_body,
            headers=REQUEST_HEADERS,
        )

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise Exception(
                error_message_template.format(
                    reason=f"error response {exc.response.status_code} while requesting {exc.request.url!r}.",
                )
            )

        response_json = response.json()

        if "session_id" in response_json:
            summarization = await _poll_summarization_task(
                poll_interval_ms=int(response_json.get("poll_interval_ms", 1000)),
                session_id=(response_json["session_id"]),
                video_url=video_url,
                http_client=http_client,
            )
        elif "error_code" in response_json:
            raise Exception(
                error_message_template.format(
                    reason=f"got an unsuccessful http response: {json.dumps(response_json)}",
                )
            )
        elif "keypoints" in response_json:
            summarization = json.dumps(response_json["keypoints"])
        else:
            raise Exception(
                error_message_template.format(
                    reason=f"got an invalid http response: {json.dumps(response_json)}",
                )
            )

    if summarization is None:
        raise Exception(f"Cannot get summarization for the URL {video_url}")

    await insert_summarization_for_video(
        conn=conn,
        video_url=video_url,
        lesson_id=lesson_id,
        summarization=summarization,
    )

    return summarization


async def _wait_for_meilisearch_task(
    task_id: int, 
    client: meilisearch.Client, 
    poll_interval_ms: int,
    timeout_seconds: int,
):
    deadline = int(time.time()) + timeout_seconds
    while int(time.time()) < deadline:
        task_result = client.get_task(task_id)
        if task_result.status in ['enqueued', 'processing']:
            await asyncio.sleep(poll_interval_ms / 1000)
        elif task_result.status in ['succeeded', 'canceled']:
            return
        else:
            raise Exception('Failed to add documents to search index')
    raise TimeoutError('Operation timeouted')



async def add_summary_to_meilisearch(
    summary: str, 
    lesson_id: int,
    client: meilisearch.Client,
    retries = 3,
):
    keypoints = json.loads(summary)
    documents = []
    for keypoint in keypoints:
        documents.append({
            "start_time": keypoint["start_time"],
            "lesson_id": lesson_id,
            "id": f'{lesson_id}_{keypoint["id"]}',
            "theses": [thesis["content"] for thesis in keypoint["theses"]],
        })
    index = client.index(MEILISEARCH_INDEX_NAME)
    task_id = index.add_documents(documents, primary_key='id').task_uid

    retry_num = 0
    settings = Settings()
    base_delay = settings.add_to_meilisearch_timeout_seconds
    base_poll_interval_ms = settings.add_to_meilisearch_poll_interval_ms
    while retry_num < retries:
        try:
            timeout = base_delay * 2 ** retry_num
            poll_interval_ms = base_poll_interval_ms * 2 ** retry_num
            await _wait_for_meilisearch_task(task_id, client, poll_interval_ms, timeout)
            return
        except TimeoutError:
            retry_num += 1
        except Exception as e:
            raise e
    raise Exception('Failed to add documents to search index due to timeout')
