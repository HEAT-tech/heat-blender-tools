import aiohttp
import asyncio
import json
import os
import bpy
import ssl
import certifi
from typing import Dict
from .. import dotenv


class HeatAPIClient:
    base_url = "https://partner-api.heat.tech/prod/"
    download_dir = os.getenv('TEMP') or '/tmp'
    sslcontext = ssl.create_default_context(cafile=certifi.where())
    timeout = aiohttp.ClientTimeout(total=90)

    def __init__(self):
        env = dotenv.DotENV()
        if env.is_true('HEAT_USE_DEV_API'):
            self.base_url = "https://dev-partner-api.heat.tech/dev/"

    def _get_user_api_key_header(self):
        this_plugin_name = __name__.split(".")[0]
        heat_user_api_key = bpy.context.preferences.addons[this_plugin_name].preferences.heat_user_api_key
        return {"X-API-KEY": heat_user_api_key}

    async def _get_json(self, url):
        header = self._get_user_api_key_header()
        async with aiohttp.ClientSession(headers=header, timeout=self.timeout) as session:
            async with session.get(url, ssl=self.sslcontext) as resp:
                assert resp.status == 200
                data = await resp.json()
                return data

    def _to_params_string(self, params: Dict[str, str]) -> str:
        param_string = ''

        if params:
            param_string = '?' + '&'.join([f'{key}={value}' for key, value in params.items()])

        return param_string

    async def get_movements(self, v=1, params: Dict[str, str] = None):
        """
        Fetches movements from the Heat API
        :param v: API version number
        :param params: Dictionary of params to filter movement results
        :return: Dictionary of results
        """
        url = self.base_url + f"v{v}/movements" + self._to_params_string(params)
        data = await self._get_json(url)
        if data['nextPage']:
            bpy.context.scene.heat_animation_next_results_page = int(data['nextPage'])
        else:
            bpy.context.scene.heat_animation_next_results_page = -1
        return data["movements"]

    async def get_movement_tags(self, v=2):
        """
        Fetches list of movement tags from Heat API
        :param v: API version number
        :return: Dictionary of results
        """
        url = self.base_url + f"v{v}/movement-tags"
        data = await self._get_json(url)
        return data["tags"]

    async def download_file(self, url, file_path, caller=None):
        """
        Async download file
        :param url: File url
        :param file_path: Location to save file to
        :param caller: Object to sync download_progress to
        """
        header = self._get_user_api_key_header()
        async with aiohttp.ClientSession(headers=header, timeout=self.timeout) as session:
            async with session.get(url, ssl=self.sslcontext) as resp:
                if resp.status == 200:
                    total_size = int(resp.headers.get('Content-Length', '0'))
                    downloaded_size = 0
                    with open(file_path, 'wb') as fd:
                        while True:
                            chunk = await resp.content.read(1024)
                            downloaded_size += len(chunk)

                            if caller:
                                caller.download_progress = (downloaded_size / total_size)
                            if not chunk:
                                break
                            fd.write(chunk)

    def synchronous_download_file(self, url, file_path):
        """
        Synchronously download a file
        :param url: File url
        :param file_path: Location to save file to
        """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.download_file(url, file_path))


def build_params_list_from_scene_params() -> Dict[str, str]:
    params = {}
    context = bpy.context

    if context.scene.heat_search_query != '':
        params['q'] = context.scene.heat_search_query
    motion_type_set = context.scene.heat_motion_types
    motion_types = ','.join([str(m_type) for m_type in motion_type_set])
    if motion_types!= '':
        params['motionTypes'] = motion_types
    tags = bpy.context.scene.heat_tag_results_list
    selected_tags = [tag for tag in tags if tag.selected]
    if len(selected_tags):
        params['tags'] = ','.join([str(tag.id) for tag in selected_tags])

    return params


def add_movements_to_results_list(movements):
    for movement in movements:
        new_movement = bpy.context.scene.heat_animation_results_list.add()
        new_movement.name = movement['name']
        new_movement.movement_id = movement['id']
        new_movement.description = movement['description']
        new_movement.download_url = movement['downloadUrl']
        new_movement.preview_image_url = movement['previewImageUrl']
        new_movement.url = movement['url']

        if not movement['tags']:
            continue
        for tag in movement['tags']:
            tag_item = new_movement.tags.add()
            tag_item['id'] = tag['id']
            tag_item['url'] = tag['url']
            tag_item['parent_id'] = tag['parentID'] or -1
            tag_item['name'] = tag['name']
