"""
Instagram Graph API publisher.

Uses Meta's official two-step publishing flow:
  1. POST /{ig-user-id}/media       -> creates a media container, returns creation_id
  2. POST /{ig-user-id}/media_publish -> publishes the container as a real post

Requires an image accessible at a public HTTPS URL (Meta downloads it server-side).
"""
import os
import time
import urllib.parse
import urllib.request
import json


GRAPH_API_VERSION = "v21.0"
# Use graph.instagram.com for IGAA-prefixed tokens (Instagram Business Login flow).
# If you ever switch to an EAA token (Facebook Login for Business), change this
# to: f"https://graph.facebook.com/{GRAPH_API_VERSION}"
BASE_URL = f"https://graph.instagram.com/{GRAPH_API_VERSION}"


def _http_post(url: str, params: dict) -> dict:
    """Simple POST using stdlib (no extra deps required)."""
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode()
            return json.loads(body)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        raise RuntimeError(f"HTTP {e.code} from {url}: {err_body}") from e


def _http_get(url: str, params: dict) -> dict:
    qs = urllib.parse.urlencode(params)
    full = f"{url}?{qs}"
    try:
        with urllib.request.urlopen(full, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code} from {full}: {e.read().decode()}") from e


def create_media_container(ig_user_id: str, image_url: str,
                           caption: str, access_token: str,
                           media_type: str = None) -> str:
    """
    Step 1: create a media container. Returns the creation_id.

    Args:
        media_type: None for a regular feed post, or "STORIES" for a story.
    """
    url = f"{BASE_URL}/{ig_user_id}/media"
    params = {
        "image_url": image_url,
        "access_token": access_token,
    }
    # Stories don't support captions
    if media_type == "STORIES":
        params["media_type"] = "STORIES"
    else:
        params["caption"] = caption
    result = _http_post(url, params)
    if "id" not in result:
        raise RuntimeError(f"No container id returned: {result}")
    return result["id"]


def wait_for_container_ready(creation_id: str, access_token: str,
                             max_wait_s: int = 120) -> None:
    """
    Meta sometimes needs a moment to fetch and process the image.
    Poll the container status until it's FINISHED (or fail).
    """
    url = f"{BASE_URL}/{creation_id}"
    deadline = time.time() + max_wait_s
    last_status = None
    while time.time() < deadline:
        result = _http_get(url, {
            "fields": "status_code",
            "access_token": access_token,
        })
        status = result.get("status_code")
        last_status = status
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Container failed with status: {status}")
        # Otherwise IN_PROGRESS / PUBLISHED — keep polling
        time.sleep(3)
    raise RuntimeError(
        f"Container not ready after {max_wait_s}s (last status: {last_status})"
    )


def publish_container(ig_user_id: str, creation_id: str,
                      access_token: str) -> str:
    """Step 2: publish the container. Returns the published media id."""
    url = f"{BASE_URL}/{ig_user_id}/media_publish"
    params = {
        "creation_id": creation_id,
        "access_token": access_token,
    }
    result = _http_post(url, params)
    if "id" not in result:
        raise RuntimeError(f"No media id returned: {result}")
    return result["id"]


def publish_image(ig_user_id: str, image_url: str, caption: str,
                  access_token: str, media_type: str = None) -> str:
    """
    End-to-end: create container, wait for it to be ready, publish it.
    Returns the published media id.

    Args:
        media_type: None for a feed post, "STORIES" for a story.
    """
    kind = "STORY" if media_type == "STORIES" else "FEED"
    print(f"[IG] Creating {kind} media container for {image_url}")
    creation_id = create_media_container(
        ig_user_id, image_url, caption, access_token, media_type=media_type
    )
    print(f"[IG] Container created: {creation_id}")

    print("[IG] Waiting for container to be ready...")
    wait_for_container_ready(creation_id, access_token)

    print("[IG] Publishing container...")
    media_id = publish_container(ig_user_id, creation_id, access_token)
    print(f"[IG] Published {kind}: {media_id}")
    return media_id
